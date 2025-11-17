import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load LLM configuration
def load_llm_config():
    """Load LLM configuration from llm_config.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'llm_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

LLM_CONFIG = load_llm_config()


class ResumeSelector:
    """
    Uses Claude API to intelligently select resume content based on job description.
    Returns a trimmed subset of the resume data in the exact same JSON structure.
    """

    def __init__(self, api_key=None, model=None):
        """
        Initialize the ResumeSelector with Claude API.

        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
            model: Claude model to use (default: claude-3-5-haiku-20241022) or claude-sonnet-4-20250514
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Set it in .env file or pass as argument.")

        self.model = model or os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
        self.client = Anthropic(api_key=self.api_key)

    def select_resume_content(self, full_resume_data, job_description, should_rewrite_selected=False):
        """
        Select the most relevant resume content based on job description.

        Args:
            full_resume_data: Complete resume data dictionary (from resume_data_enhanced.json)
            job_description: Job description text to tailor the resume for
            should_rewrite_selected: If True, LLM rewrites bullets/projects to better match job description.
                                    If False, uses exact text from original data.

        Returns:
            tuple: (trimmed_data: dict, validation_result: tuple)
                - trimmed_data: Dictionary with trimmed resume data
                - validation_result: (is_valid: bool, message: str)
        """

        # Build system prompt and user message separately for caching
        system_blocks, user_message = self._build_prompt_with_caching(
            full_resume_data, job_description, should_rewrite_selected
        )

        print(f"Model is: {self.model}")
        print(f"Rewrite mode: {'ENABLED ✏️' if should_rewrite_selected else 'DISABLED 📋'}")
        print(f"🔥 Prompt caching: ENABLED (resume data cached for 5 minutes)")

        # Call Claude API with prompt caching
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=int(os.getenv('MAX_TOKENS', 4096)),
                system=system_blocks,  # System blocks with caching
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            # Extract the JSON response
            response_text = response.content[0].text

            # Print cache usage stats if available
            usage = response.usage
            if hasattr(usage, 'cache_creation_input_tokens') and usage.cache_creation_input_tokens:
                print(f"💾 Cache write: {usage.cache_creation_input_tokens} tokens")
            if hasattr(usage, 'cache_read_input_tokens') and usage.cache_read_input_tokens:
                print(f"⚡ Cache hit: {usage.cache_read_input_tokens} tokens (90% savings!)")

            # Debug: Print first 500 chars of response
            print(f"📝 LLM Response (first 500 chars):\n{response_text[:500]}")

            # Parse JSON from response
            trimmed_data = self._parse_response(response_text)

            # Validate the response (non-blocking)
            is_valid, validation_message = self._validate_response(trimmed_data, full_resume_data)

            return trimmed_data, (is_valid, validation_message)

        except Exception as e:
            print(f"Error calling Claude API: {e}")
            raise

    def _build_skills_constraints(self, full_resume_data, config):
        """Build skills constraints dynamically from resume data structure."""
        skills_data = full_resume_data.get('skills', [])
        skills_config = config.get('skills_per_category', {})

        # Handle both old dict format and new array format
        if isinstance(skills_data, list):
            # New v2.0 format - array of skill sections with embedded min/max
            constraints = []
            for skill_section in skills_data:
                title = skill_section.get('title', '')
                # Try to get min/max from section itself, fall back to config
                min_val = skill_section.get('min')
                max_val = skill_section.get('max')

                if min_val is None or max_val is None:
                    # Fall back to config if not in section
                    title_key = title.lower()
                    min_val = min_val or skills_config.get(title_key, {}).get('min', 5)
                    max_val = max_val or skills_config.get(title_key, {}).get('max', 10)

                constraints.append(f"   - {title}: SELECT AT LEAST {min_val} items (max {max_val})")
            return '\n'.join(constraints)
        else:
            # Old v1.0 format - dict with hardcoded categories (backward compatibility)
            constraints = []
            for category_key in ['languages', 'platforms', 'skills', 'frameworks', 'tools', 'database']:
                if category_key in skills_data:
                    min_val = skills_config.get(category_key, {}).get('min', 5)
                    max_val = skills_config.get(category_key, {}).get('max', 10)
                    constraints.append(f"   - {category_key.title()}: SELECT AT LEAST {min_val} items (max {max_val})")
            return '\n'.join(constraints)

    def _build_skills_json_schema(self, full_resume_data):
        """Build the skills section of the JSON schema dynamically."""
        skills_data = full_resume_data.get('skills', [])

        # Handle both old dict format and new array format
        if isinstance(skills_data, list):
            # New v2.0 format - return array schema
            schema_items = []
            for skill_section in skills_data:
                title = skill_section.get('title', '')
                min_val = skill_section.get('min', 5)
                max_val = skill_section.get('max', 10)
                schema_items.append(f'''    {{
      "title": "{title}",
      "items": ["exact skill names"],
      "mandatoryItems": ["exact mandatory skill names"],
      "min": {min_val},
      "max": {max_val}
    }}''')
            return '  "skills": [\n' + ',\n'.join(schema_items) + '\n  ]'
        else:
            # Old v1.0 format - dict schema (backward compatibility)
            return '''  "skills": {
    "languages": ["exact skill names"],
    "platforms": ["exact platform names"],
    "skills": ["exact skill names"],
    "frameworks": ["exact framework names"],
    "tools": ["exact tool names"],
    "database": ["exact database names"]
  }'''

    def _build_prompt(self, full_resume_data, job_description, should_rewrite_selected=False):
        """Build the prompt for Claude with instructions and data."""

        config = full_resume_data.get('config', {})

        # Build per-company constraints list
        company_constraints = ""
        for company in full_resume_data.get('companies', []):
            constraints = company.get('bullet_constraints', {})
            min_count = constraints.get('min', 4)
            max_count = constraints.get('max', 6)
            company_constraints += f"     * {company['id']} ({company['position']} at {company['name']}): MUST have EXACTLY {min_count} bullets minimum, {max_count} maximum\n"

        # Conditional instruction based on rewrite mode
        if should_rewrite_selected:
            rewrite_instruction = """2. **REWRITE MODE ENABLED**: You MAY rewrite the selected bullets and project descriptions to better align with the job description.

   🚨 **CRITICAL: ZERO TOLERANCE FOR FABRICATION** 🚨
   - NEVER add facts, contexts, industries, or details not in the original
   - NEVER infer or assume information
   - NEVER add impressive-sounding but unverified claims
   - EXAMPLES OF FORBIDDEN ADDITIONS:
     ❌ Adding "healthcare" when original says "fintech"
     ❌ Adding "enterprise-grade" when not mentioned
     ❌ Adding "startup environment" when not specified
     ❌ Adding "critical" or "mission-critical" if not stated
     ❌ Adding specific technologies not in original

   **WHAT YOU CAN DO:**
   ✅ Rephrase using synonyms for existing words
   ✅ Reorder existing information for emphasis
   ✅ Highlight different aspects that ARE in the original
   ✅ Change sentence structure while keeping all facts

   **STRICTLY MAINTAIN:**
   - EVERY factual detail from the original (companies, technologies, numbers, outcomes)
   - Technical accuracy - NO adding technologies or skills not mentioned in original
   - NO fabricating or adding context that wasn't in the original bullet
   - Similar length to original

   Example CORRECT transformation:
   Original: "Developed Android library for ad integration with 90% code coverage"
   Job needs: Testing focus
   ✅ GOOD: "Implemented Android library with comprehensive testing achieving 90% code coverage for ad integration"
   ❌ BAD: "Developed enterprise-grade Android library for ad integration with 90% code coverage in healthcare sector"
   Why BAD? Added "enterprise-grade" and "healthcare" - NOT in original!

   Example 2:
   Original: "Designed UPI payment system using Clean Architecture at Slice fintech startup"
   Job needs: Architecture focus  
   ✅ GOOD: "Architected UPI payment system using Clean Architecture principles at Slice fintech"
   ❌ BAD: "Architected healthcare-critical payment system using Clean Architecture at Slice"
   Why BAD? Changed "fintech" to "healthcare" and added "critical" - NOT in original!

   **GOLDEN RULE: When in doubt, use EXACT original text. Better to be less optimized than dishonest.**"""
        else:
            rewrite_instruction = """2. DO NOT paraphrase or rewrite any content - return the EXACT text from the original bullets, skills, and projects"""

        prompt = f"""You are an expert resume writer and ATS optimization specialist. Your task is to select the most relevant content from a candidate's resume based on a specific job description.

**CRITICAL INSTRUCTIONS - THESE ARE MANDATORY:**
1. Return a JSON object with the EXACT SAME STRUCTURE as the input resume data
{rewrite_instruction}
3. Select content that best matches the job description requirements
4. THE CONSTRAINTS BELOW ARE HARD REQUIREMENTS - YOU MUST MEET ALL OF THEM
5. Maintain chronological order for all companies and bullets

**JOB DESCRIPTION:**
{job_description}

**RESUME DATA:**
{json.dumps(full_resume_data, indent=2)}

**⚠️  MANDATORY SELECTION CONSTRAINTS (MUST FOLLOW EXACTLY):**

These are NON-NEGOTIABLE requirements. Your response is INVALID if ANY constraint is violated.

1. **Bullets (Experience) - MANDATORY COUNTS:**

   Total bullets requirement:
   - MUST have between {config.get('bullets', {}).get('total_min', 16)} and {config.get('bullets', {}).get('total_max', 20)} bullets total across ALL companies

   Per-company requirements (YOU MUST MEET EACH ONE):
{company_constraints}

   Important notes:
   - ALL {len(full_resume_data.get('companies', []))} companies are MANDATORY
   - If a company doesn't have enough relevant bullets, ADD LESS RELEVANT ONES to meet the minimum
   - Meeting count constraints is MORE IMPORTANT than perfect relevance
   - Each company's bullets must come from THAT company's bullet list only

2. **Skills - MANDATORY COUNTS (Must meet MINIMUM in each category):**
{self._build_skills_constraints(full_resume_data, config)}
   - ALWAYS include ALL items from "mandatoryItems" arrays FIRST

3. **Projects - MANDATORY COUNT:**
   - MUST select {config.get('projects', {}).get('min', 2)}-{config.get('projects', {}).get('max', 3)} projects
   - Aim for {config.get('projects', {}).get('max', 3)} projects to maximize content
   {'- REWRITE project descriptions to align with job requirements while keeping technical details' if should_rewrite_selected else '- Use EXACT project descriptions from original data'}

4. **Summary:**
   - Select EXACTLY ONE summary from the available options that best matches the job description

**STEP-BY-STEP SELECTION PROCESS:**

Step 1: For EACH company, select bullets in this order:
   a) Start with most relevant bullets
   b) Keep adding until you reach the MINIMUM count for that company
   c) If still below minimum, add remaining bullets even if less relevant
   d) Stop when you hit the maximum count for that company
   {'d1) CAREFULLY rewrite each selected bullet - ONLY rephrase existing info, NEVER add new facts or contexts' if should_rewrite_selected else ''}

Step 2: Check total bullet count:
   - If below {config.get('bullets', {}).get('total_min', 16)}, go back and add more bullets to companies that haven't hit their maximum
   - If above {config.get('bullets', {}).get('total_max', 20)}, remove least relevant bullets from companies

Step 3: Select skills - prioritize mandatory items, then most relevant

Step 4: Select {config.get('projects', {}).get('max', 3)} projects{'and carefully rewrite descriptions using ONLY information from the original description' if should_rewrite_selected else ''}

**OUTPUT FORMAT:**
Return ONLY a valid JSON object with this structure:

{{
  "title": "Company Name - Job Title from job description",
  "reasoning": "Explain how you met the count requirements: 'Selected X bullets for company1 (minimum Y required), Z bullets for company2 (minimum W required), total A bullets (requirement: {config.get('bullets', {}).get('total_min', 16)}-{config.get('bullets', {}).get('total_max', 20)}). Chose B projects, C skills per category.{' Rewrote bullets and projects to align with job requirements.' if should_rewrite_selected else ''}'",
  "static_info": {{
    "name": "exact name from resume data",
    "email": "exact email",
    "phone": "exact phone",
    "address": "exact address",
    "links": [
      {{"title": "exact title", "url": "exact URL"}},
      ...copy ALL links from resume data exactly as they appear
    ]
  }},
  "summaries": [
    {{
      "id": "exact id from selected summary",
      "label": "exact label from selected summary",
      "text": "exact text from selected summary"
    }}
  ],
{self._build_skills_json_schema(full_resume_data)},
  "companies": [
    {{
      "id": "exact company id",
      "mandatory": true,
      "name": "exact company name",
      "position": "exact position",
      "dates": "exact dates",
      "location": "exact location",
      "bullets": [
        {{"text": "{'rephrased bullet using ONLY information from original - NO added facts or contexts' if should_rewrite_selected else 'exact bullet text - no paraphrasing'}"}},
        ...
      ]
    }},
    ...
  ],
  "projects": [
    {{
      "id": "exact project id",
      "name": "exact name",
      "tech": "exact tech",
      "description": "{'rephrased description using ONLY original information - NO fabricated details' if should_rewrite_selected else 'exact description'}",
      "date": "exact date",
      "link": "exact link"
    }},
    ...
  ],
  "education": [
    {{
      "degree": "exact degree",
      "dates": "exact dates",
      "course": "exact course",
      "institution": "exact institution",
      "location": "exact location"
    }},
    ... (copy ALL education entries exactly from resume data)
  ],
  "display_settings": {{
    ... (copy the ENTIRE display_settings object EXACTLY as-is from resume data - do NOT modify or omit)
  }}
}}

**CRITICAL: Copy static_info, education, and display_settings EXACTLY from the resume data with ALL fields. Do NOT omit anything. If display_settings is present in the input, it MUST be included in the output.**

**FINAL VALIDATION CHECKLIST (Check before returning):**
- [ ] Total bullets = {config.get('bullets', {}).get('total_min', 16)}-{config.get('bullets', {}).get('total_max', 20)}? (Count them!)
- [ ] Each company meets its minimum bullet requirement? (Check each one!)
- [ ] All {len(full_resume_data.get('companies', []))} companies included?
- [ ] Each skill category meets minimum count?
- [ ] {config.get('projects', {}).get('min', 2)}-{config.get('projects', {}).get('max', 3)} projects selected?
- [ ] Exactly 1 summary?
- [ ] Approximately 770 - 820 words in total?
{'- [ ] All rewritten bullets contain ONLY information from originals - NO added facts, industries, or contexts?' if should_rewrite_selected else '- [ ] All bullets and project descriptions are EXACT copies from original?'}
{'- [ ] Double-checked: No "healthcare", "enterprise", or other terms added that were not in original?' if should_rewrite_selected else ''}

If ANY checkbox above is NO, your response is WRONG. Fix it before returning.

Return ONLY the JSON object, nothing else. No markdown, no explanations outside the JSON."""

        return prompt

    def _build_prompt_with_caching(self, full_resume_data, job_description, should_rewrite_selected=False):
        """
        Build the prompt split into system blocks (with caching) and user message.

        This enables prompt caching by placing the resume data (which stays constant)
        in the system parameter with cache_control, and the job description (which varies)
        in the user message.

        Returns:
            tuple: (system_blocks: list, user_message: str)
        """

        config = full_resume_data.get('config', {})

        # Build per-company constraints list
        company_constraints = ""
        for company in full_resume_data.get('companies', []):
            constraints = company.get('bullet_constraints', {})
            min_count = constraints.get('min', 4)
            max_count = constraints.get('max', 6)
            company_constraints += f"     * {company['id']} ({company['position']} at {company['name']}): MUST have EXACTLY {min_count} bullets minimum, {max_count} maximum\n"

        # Get rewrite instruction from config
        rewrite_mode_config = LLM_CONFIG['system_prompt']['rewrite_mode']
        if should_rewrite_selected:
            rewrite_instruction = f"2. {rewrite_mode_config['enabled_instruction']}"
        else:
            rewrite_instruction = f"2. {rewrite_mode_config['disabled_instruction']}"

        # Build system instructions using config
        role_desc = LLM_CONFIG['system_prompt']['role_description']
        critical_instructions = LLM_CONFIG['system_prompt']['critical_instructions']

        instructions_text = "\n".join([f"{i+1}. {instr}" if i > 0 else f"{i+1}. {instr}"
                                       for i, instr in enumerate([critical_instructions[0], rewrite_instruction] + critical_instructions[1:])])

        system_instructions = f"""{role_desc}

**CRITICAL INSTRUCTIONS - THESE ARE MANDATORY:**
{instructions_text}

**⚠️  MANDATORY SELECTION CONSTRAINTS (MUST FOLLOW EXACTLY):**

These are NON-NEGOTIABLE requirements. Your response is INVALID if ANY constraint is violated.

1. **Bullets (Experience) - MANDATORY COUNTS:**

   Total bullets requirement:
   - MUST have between {config.get('bullets', {}).get('total_min', 16)} and {config.get('bullets', {}).get('total_max', 20)} bullets total across ALL companies

   Per-company requirements (YOU MUST MEET EACH ONE):
{company_constraints}

   Important notes:
   - ALL {len(full_resume_data.get('companies', []))} companies are MANDATORY
   - If a company doesn't have enough relevant bullets, ADD LESS RELEVANT ONES to meet the minimum
   - Meeting count constraints is MORE IMPORTANT than perfect relevance
   - Each company's bullets must come from THAT company's bullet list only

2. **Skills - MANDATORY COUNTS (Must meet MINIMUM in each category):**
{self._build_skills_constraints(full_resume_data, config)}
   - ALWAYS include ALL items from "mandatoryItems" arrays FIRST

3. **Projects - MANDATORY COUNT:**
   - MUST select {config.get('projects', {}).get('min', 2)}-{config.get('projects', {}).get('max', 3)} projects
   - Aim for {config.get('projects', {}).get('max', 3)} projects to maximize content
   {'- REWRITE project descriptions to align with job requirements while keeping technical details' if should_rewrite_selected else '- Use EXACT project descriptions from original data'}

4. **Summary:**
   - Select EXACTLY ONE summary from the available options that best matches the job description

**STEP-BY-STEP SELECTION PROCESS:**

Step 1: For EACH company, select bullets in this order:
   a) Start with most relevant bullets
   b) Keep adding until you reach the MINIMUM count for that company
   c) If still below minimum, add remaining bullets even if less relevant
   d) Stop when you hit the maximum count for that company
   {'d1) CAREFULLY rewrite each selected bullet - ONLY rephrase existing info, NEVER add new facts or contexts' if should_rewrite_selected else ''}

Step 2: Check total bullet count:
   - If below {config.get('bullets', {}).get('total_min', 16)}, go back and add more bullets to companies that haven't hit their maximum
   - If above {config.get('bullets', {}).get('total_max', 20)}, remove least relevant bullets from companies

Step 3: Select skills - prioritize mandatory items, then most relevant

Step 4: Select {config.get('projects', {}).get('max', 3)} projects{'and carefully rewrite descriptions using ONLY information from the original description' if should_rewrite_selected else ''}

**OUTPUT FORMAT:**
Return ONLY a valid JSON object with this structure:

{{
  "title": "Company Name - Job Title from job description",
  "reasoning": "Explain how you met the count requirements: 'Selected X bullets for company1 (minimum Y required), Z bullets for company2 (minimum W required), total A bullets (requirement: {config.get('bullets', {}).get('total_min', 16)}-{config.get('bullets', {}).get('total_max', 20)}). Chose B projects, C skills per category.{' Rewrote bullets and projects to align with job requirements.' if should_rewrite_selected else ''}'",
  "static_info": {{
    "name": "exact name from resume data",
    "email": "exact email",
    "phone": "exact phone",
    "address": "exact address",
    "links": [
      {{"title": "exact title", "url": "exact URL"}},
      ...copy ALL links from resume data exactly as they appear
    ]
  }},
  "summaries": [
    {{
      "id": "exact id from selected summary",
      "label": "exact label from selected summary",
      "text": "exact text from selected summary"
    }}
  ],
{self._build_skills_json_schema(full_resume_data)},
  "companies": [
    {{
      "id": "exact company id",
      "mandatory": true,
      "name": "exact company name",
      "position": "exact position",
      "dates": "exact dates",
      "location": "exact location",
      "bullets": [
        {{"text": "{'rephrased bullet using ONLY information from original - NO added facts or contexts' if should_rewrite_selected else 'exact bullet text - no paraphrasing'}"}},
        ...
      ]
    }},
    ...
  ],
  "projects": [
    {{
      "id": "exact project id",
      "name": "exact name",
      "tech": "exact tech",
      "description": "{'rephrased description using ONLY original information - NO fabricated details' if should_rewrite_selected else 'exact description'}",
      "date": "exact date",
      "link": "exact link"
    }},
    ...
  ],
  "education": [
    {{
      "degree": "exact degree",
      "dates": "exact dates",
      "course": "exact course",
      "institution": "exact institution",
      "location": "exact location"
    }},
    ... (copy ALL education entries exactly from resume data)
  ],
  "display_settings": {{
    ... (copy the ENTIRE display_settings object EXACTLY as-is from resume data - do NOT modify or omit)
  }}
}}

**CRITICAL: Copy static_info, education, and display_settings EXACTLY from the resume data with ALL fields. Do NOT omit anything. If display_settings is present in the input, it MUST be included in the output.**

**FINAL VALIDATION CHECKLIST (Check before returning):**
- [ ] Total bullets = {config.get('bullets', {}).get('total_min', 16)}-{config.get('bullets', {}).get('total_max', 20)}? (Count them!)
- [ ] Each company meets its minimum bullet requirement? (Check each one!)
- [ ] All {len(full_resume_data.get('companies', []))} companies included?
- [ ] Each skill category meets minimum count?
- [ ] {config.get('projects', {}).get('min', 2)}-{config.get('projects', {}).get('max', 3)} projects selected?
- [ ] Exactly 1 summary?
- [ ] Approximately 770 - 820 words in total?
{'- [ ] All rewritten bullets contain ONLY information from originals - NO added facts, industries, or contexts?' if should_rewrite_selected else '- [ ] All bullets and project descriptions are EXACT copies from original?'}
{'- [ ] Double-checked: No "healthcare", "enterprise", or other terms added that were not in original?' if should_rewrite_selected else ''}

If ANY checkbox above is NO, your response is WRONG. Fix it before returning.

{LLM_CONFIG['system_prompt']['final_instruction']}"""

        # Resume data - THIS GETS CACHED! 🔥
        resume_data_block = f"""**FULL RESUME DATA:**

{json.dumps(full_resume_data, indent=2)}"""

        # Build system blocks - conditionally add caching based on config
        system_blocks = [
            {
                "type": "text",
                "text": system_instructions
            }
        ]

        # Add resume data block with optional caching
        resume_block = {
            "type": "text",
            "text": resume_data_block
        }

        if LLM_CONFIG['cache_config']['use_prompt_caching']:
            resume_block["cache_control"] = {"type": "ephemeral"}  # 🔥 CACHE THIS!

        system_blocks.append(resume_block)

        # User message using template from config
        user_message = LLM_CONFIG['user_prompt_template'].format(job_description=job_description)

        return system_blocks, user_message

    def _parse_response(self, response_text):
        """Parse JSON from Claude's response, handling markdown code blocks and extra text."""

        response_text = response_text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        elif response_text.startswith('```'):
            response_text = response_text[3:]

        if response_text.endswith('```'):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        try:
            # First, try normal JSON parsing
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            # If that fails, try to extract just the JSON object
            # This handles cases where there's extra text after the JSON
            print(f"Failed to parse JSON response: {e}")
            print(f"Response text: {response_text[:500]}...")

            try:
                # Use JSONDecoder to parse just the first valid JSON object
                # This will ignore any extra text after the JSON
                decoder = json.JSONDecoder()
                obj, idx = decoder.raw_decode(response_text)

                # Warn if there was extra data
                remaining = response_text[idx:].strip()
                if remaining:
                    print(f"Warning: Ignoring extra text after JSON: {remaining[:200]}...")

                return obj
            except json.JSONDecodeError as e2:
                print(f"Failed to parse JSON even with raw_decode: {e2}")
                raise

    def _validate_response(self, trimmed_data, full_resume_data):
        """
        Validate that the LLM response meets all constraints.
        Does NOT raise errors - collects issues and returns validation result.

        Returns:
            tuple: (is_valid: bool, validation_message: str)
        """

        config = full_resume_data.get('config', {})
        issues = []

        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)

        # 1. Validate bullet counts
        total_bullets = sum(len(company.get('bullets', [])) for company in trimmed_data.get('companies', []))
        min_bullets = config.get('bullets', {}).get('total_min', 16)
        max_bullets = config.get('bullets', {}).get('total_max', 20)

        if not (min_bullets <= total_bullets <= max_bullets):
            issue = f"⚠️  Total bullets ({total_bullets}) outside range {min_bullets}-{max_bullets}"
            print(issue)
            issues.append(issue)
        else:
            print(f"✅ Total bullets: {total_bullets} (within {min_bullets}-{max_bullets})")

        # 2. Validate all companies are present
        original_company_ids = {c['id'] for c in full_resume_data.get('companies', [])}
        trimmed_company_ids = {c['id'] for c in trimmed_data.get('companies', [])}

        if original_company_ids != trimmed_company_ids:
            missing = original_company_ids - trimmed_company_ids
            issue = f"⚠️  Missing companies: {missing}"
            print(issue)
            issues.append(issue)
        else:
            print(f"✅ All {len(original_company_ids)} companies present")

        # 3. Validate per-company bullet constraints
        print("\n📊 Per-Company Bullet Counts:")
        for company in trimmed_data.get('companies', []):
            company_id = company['id']
            original_company = next((c for c in full_resume_data['companies'] if c['id'] == company_id), None)
            if not original_company:
                issue = f"⚠️  Company '{company_id}' not found in original data"
                print(f"  {issue}")
                issues.append(issue)
                continue

            constraints = original_company.get('bullet_constraints', {})
            bullet_count = len(company.get('bullets', []))
            min_count = constraints.get('min', 4)
            max_count = constraints.get('max', 6)

            if not (min_count <= bullet_count <= max_count):
                issue = f"⚠️  {company_id}: {bullet_count} bullets (expected {min_count}-{max_count})"
                print(f"  {issue}")
                issues.append(issue)
            else:
                print(f"  ✅ {company_id}: {bullet_count} bullets (within {min_count}-{max_count})")

        # 4. Validate project count
        project_count = len(trimmed_data.get('projects', []))
        min_projects = config.get('projects', {}).get('min', 2)
        max_projects = config.get('projects', {}).get('max', 3)

        if not (min_projects <= project_count <= max_projects):
            issue = f"⚠️  Project count ({project_count}) outside range {min_projects}-{max_projects}"
            print(f"\n{issue}")
            issues.append(issue)
        else:
            print(f"\n✅ Projects: {project_count} (within {min_projects}-{max_projects})")

        # 5. Validate skills counts
        print("\n🛠️  Skills Validation:")
        skills_config = config.get('skills_per_category', {})
        for skill_category, constraints in skills_config.items():
            if skill_category in trimmed_data.get('skills', {}):
                count = len(trimmed_data['skills'][skill_category])
                min_count = constraints.get('min', 0)
                max_count = constraints.get('max', 100)

                if not (min_count <= count <= max_count):
                    issue = f"⚠️  {skill_category}: {count} items (expected {min_count}-{max_count})"
                    print(f"  {issue}")
                    issues.append(issue)
                else:
                    print(f"  ✅ {skill_category}: {count} items")

        # 6. Validate summary is present and only one
        summaries = trimmed_data.get('summaries', [])
        if isinstance(summaries, list):
            # New array format
            if len(summaries) != 1:
                issue = f"⚠️  Expected exactly 1 summary, got {len(summaries)}"
                print(f"\n{issue}")
                issues.append(issue)
            else:
                summary_label = summaries[0].get('label', 'unknown')
                print(f"\n✅ Summary: 1 option selected ({summary_label})")
        else:
            # Old dict format (backward compatibility)
            if len(summaries) != 1:
                issue = f"⚠️  Expected exactly 1 summary, got {len(summaries)}"
                print(f"\n{issue}")
                issues.append(issue)
            else:
                summary_type = list(summaries.keys())[0]
                print(f"\n✅ Summary: 1 type selected ({summary_type})")

        # Print final result
        print("\n" + "=" * 60)
        if not issues:
            print("✅ VALIDATION PASSED - All constraints met!")
            print("=" * 60)
            return True, "Validation passed - all constraints met"
        else:
            print(f"⚠️  VALIDATION FAILED - {len(issues)} issue(s) found")
            print("=" * 60)
            print("\n⚠️  Note: PDF will still be generated but may not meet all requirements")
            validation_message = "Validation issues found:\n" + "\n".join(issues)
            return False, validation_message


def select_resume_content(full_resume_data, job_description, api_key=None, should_rewrite_selected=False):
    """
    Convenience function to select resume content.

    Args:
        full_resume_data: Complete resume data dictionary
        job_description: Job description text
        api_key: Optional API key (if not set in environment)
        should_rewrite_selected: If True, rewrites bullets/projects to match job description

    Returns:
        tuple: (trimmed_data: dict, validation_result: tuple)
    """
    selector = ResumeSelector(api_key=api_key)
    return selector.select_resume_content(full_resume_data, job_description, should_rewrite_selected)


if __name__ == '__main__':
    """Test the LLM selector with a sample job description."""

    # Load full resume data
    try:
        with open('resume_data_enhanced.json', 'r') as f:
            full_data = json.load(f)
    except FileNotFoundError:
        print("Error: 'resume_data_enhanced.json' not found.")
        exit(1)

    # Sample job description
    job_description = """
    Senior Android Developer

    We are looking for an experienced Android developer to join our fintech team.

    Requirements:
    - 5+ years of Android development experience
    - Expert in Kotlin and Java
    - Strong experience with Jetpack Compose and MVVM/MVI architecture
    - Experience with payment systems and financial applications
    - Proficient in CI/CD, unit testing, and performance optimization
    - Experience mentoring junior developers

    Nice to have:
    - Experience with UPI payment systems
    - Background in fintech or banking applications
    - Knowledge of Clean Architecture principles
    """

    print("Testing LLM Resume Selector with Claude...")
    print(f"Job Description: {job_description[:100]}...\n")

    # Ask user which mode to test
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--rewrite':
        should_rewrite = True
        print("🔄 Testing REWRITE mode - bullets will be tailored to job description\n")
    else:
        should_rewrite = False
        print("📋 Testing EXACT mode - using original bullet text\n")
        print("💡 Tip: Use '--rewrite' flag to test rewrite mode: python llm_selector.py --rewrite\n")

    try:
        # Select resume content
        selector = ResumeSelector()
        trimmed_data, (is_valid, validation_message) = selector.select_resume_content(
            full_data,
            job_description,
            should_rewrite_selected=should_rewrite
        )

        # Print summary of selections
        print("\n" + "=" * 60)
        print("SELECTION SUMMARY")
        print("=" * 60)

        print(f"\n📝 Summary Type: {list(trimmed_data['summaries'].keys())[0]}")

        print(f"\n💼 Experience:")
        for company in trimmed_data['companies']:
            bullet_count = len(company['bullets'])
            print(f"  - {company['name']}: {bullet_count} bullets")

        total_bullets = sum(len(c['bullets']) for c in trimmed_data['companies'])
        print(f"  Total bullets: {total_bullets}")

        print(f"\n🛠️ Skills:")
        for category, items in trimmed_data['skills'].items():
            print(f"  - {category}: {len(items)} items")

        print(f"\n🚀 Projects: {len(trimmed_data['projects'])} selected")
        for project in trimmed_data['projects']:
            print(f"  - {project['name']}")

        # Save the trimmed data
        output_file = 'resume_data_trimmed.json'
        with open(output_file, 'w') as f:
            json.dump(trimmed_data, f, indent=2)

        print(f"\n✅ Trimmed resume data saved to: {output_file}")

        # Print validation result
        if not is_valid:
            print(f"\n⚠️  VALIDATION WARNINGS:")
            print(validation_message)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise