import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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
            model: Claude model to use (default: claude-3-5-haiku-20241022)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Set it in .env file or pass as argument.")

        self.model = model or os.getenv('CLAUDE_MODEL', 'claude-3-5-haiku-20241022')
        self.client = Anthropic(api_key=self.api_key)

    def select_resume_content(self, full_resume_data, job_description):
        """
        Select the most relevant resume content based on job description.

        Args:
            full_resume_data: Complete resume data dictionary (from resume_data_enhanced.json)
            job_description: Job description text to tailor the resume for

        Returns:
            tuple: (trimmed_data: dict, validation_result: tuple)
                - trimmed_data: Dictionary with trimmed resume data
                - validation_result: (is_valid: bool, message: str)
        """

        # Build the prompt
        prompt = self._build_prompt(full_resume_data, job_description)
        print(f"Model is: {self.model}")
        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=int(os.getenv('MAX_TOKENS', 4096)),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract the JSON response
            response_text = response.content[0].text

            # Parse JSON from response
            trimmed_data = self._parse_response(response_text)

            # Validate the response (non-blocking)
            is_valid, validation_message = self._validate_response(trimmed_data, full_resume_data)

            return trimmed_data, (is_valid, validation_message)

        except Exception as e:
            print(f"Error calling Claude API: {e}")
            raise

    def _build_prompt(self, full_resume_data, job_description):
        """Build the prompt for Claude with instructions and data."""

        config = full_resume_data.get('config', {})

        # Build per-company constraints list
        company_constraints = ""
        for company in full_resume_data.get('companies', []):
            constraints = company.get('bullet_constraints', {})
            min_count = constraints.get('min', 4)
            max_count = constraints.get('max', 6)
            company_constraints += f"     * {company['id']} ({company['position']} at {company['name']}): MUST have EXACTLY {min_count} bullets minimum, {max_count} maximum\n"

        prompt = f"""You are an expert resume writer and ATS optimization specialist. Your task is to select the most relevant content from a candidate's resume based on a specific job description.

**CRITICAL INSTRUCTIONS - THESE ARE MANDATORY:**
1. Return a JSON object with the EXACT SAME STRUCTURE as the input resume data
2. DO NOT paraphrase or rewrite any content - return the EXACT text from the original bullets, skills, and projects
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
   - Languages: SELECT AT LEAST {config.get('skills_per_category', {}).get('languages', {}).get('min', 5)} items (max {config.get('skills_per_category', {}).get('languages', {}).get('max', 8)})
   - Platforms: SELECT AT LEAST {config.get('skills_per_category', {}).get('platforms', {}).get('min', 5)} items (max {config.get('skills_per_category', {}).get('platforms', {}).get('max', 8)})
   - Skills: SELECT AT LEAST {config.get('skills_per_category', {}).get('skills', {}).get('min', 8)} items (max {config.get('skills_per_category', {}).get('skills', {}).get('max', 12)})
   - Frameworks: SELECT AT LEAST {config.get('skills_per_category', {}).get('frameworks', {}).get('min', 8)} items (max {config.get('skills_per_category', {}).get('frameworks', {}).get('max', 15)})
   - Tools: SELECT AT LEAST {config.get('skills_per_category', {}).get('tools', {}).get('min', 6)} items (max {config.get('skills_per_category', {}).get('tools', {}).get('max', 10)})
   - Database: SELECT AT LEAST {config.get('skills_per_category', {}).get('database', {}).get('min', 4)} items (max {config.get('skills_per_category', {}).get('database', {}).get('max', 6)})
   - ALWAYS include ALL items from "*_mandatory" arrays FIRST

3. **Projects - MANDATORY COUNT:**
   - MUST select {config.get('projects', {}).get('min', 2)}-{config.get('projects', {}).get('max', 3)} projects
   - Aim for {config.get('projects', {}).get('max', 3)} projects to maximize content

4. **Summary:**
   - Select EXACTLY ONE summary type that best matches the job description

**STEP-BY-STEP SELECTION PROCESS:**

Step 1: For EACH company, select bullets in this order:
   a) Start with most relevant bullets
   b) Keep adding until you reach the MINIMUM count for that company
   c) If still below minimum, add remaining bullets even if less relevant
   d) Stop when you hit the maximum count for that company

Step 2: Check total bullet count:
   - If below {config.get('bullets', {}).get('total_min', 16)}, go back and add more bullets to companies that haven't hit their maximum
   - If above {config.get('bullets', {}).get('total_max', 20)}, remove least relevant bullets from companies

Step 3: Select skills - prioritize mandatory items, then most relevant

Step 4: Select {config.get('projects', {}).get('max', 3)} projects

**OUTPUT FORMAT:**
Return ONLY a valid JSON object with this structure:

{{
  "title": "Company Name - Job Title from job description",
  "reasoning": "Explain how you met the count requirements: 'Selected X bullets for company1 (minimum Y required), Z bullets for company2 (minimum W required), total A bullets (requirement: {config.get('bullets', {}).get('total_min', 16)}-{config.get('bullets', {}).get('total_max', 20)}). Chose B projects, C skills per category.'",
  "static_info": {{ ... }},
  "summaries": {{
    "selected_type": "the exact summary text"
  }},
  "skills": {{
    "languages": ["exact skill names"],
    "platforms": ["exact platform names"],
    "skills": ["exact skill names"],
    "frameworks": ["exact framework names"],
    "tools": ["exact tool names"],
    "database": ["exact database names"]
  }},
  "companies": [
    {{
      "id": "exact company id",
      "mandatory": true,
      "name": "exact company name",
      "position": "exact position",
      "dates": "exact dates",
      "location": "exact location",
      "bullets": [
        {{"text": "exact bullet text - no paraphrasing"}},
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
      "description": "exact description",
      "date": "exact date",
      "link": "exact link"
    }},
    ...
  ],
  "education": [ ... ]
}}

**FINAL VALIDATION CHECKLIST (Check before returning):**
- [ ] Total bullets = {config.get('bullets', {}).get('total_min', 16)}-{config.get('bullets', {}).get('total_max', 20)}? (Count them!)
- [ ] Each company meets its minimum bullet requirement? (Check each one!)
- [ ] All {len(full_resume_data.get('companies', []))} companies included?
- [ ] Each skill category meets minimum count?
- [ ] {config.get('projects', {}).get('min', 2)}-{config.get('projects', {}).get('max', 3)} projects selected?
- [ ] Exactly 1 summary?
- [ ] Approximately 770 - 820 words in total?

If ANY checkbox above is NO, your response is WRONG. Fix it before returning.

Return ONLY the JSON object, nothing else. No markdown, no explanations outside the JSON."""

        return prompt

    def _parse_response(self, response_text):
        """Parse JSON from Claude's response, handling markdown code blocks if present."""

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
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Response text: {response_text[:500]}...")
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
        summaries = trimmed_data.get('summaries', {})
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


def select_resume_content(full_resume_data, job_description, api_key=None):
    """
    Convenience function to select resume content.

    Args:
        full_resume_data: Complete resume data dictionary
        job_description: Job description text
        api_key: Optional API key (if not set in environment)

    Returns:
        tuple: (trimmed_data: dict, validation_result: tuple)
    """
    selector = ResumeSelector(api_key=api_key)
    return selector.select_resume_content(full_resume_data, job_description)


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

    print("Testing LLM Resume Selector with Claude Haiku...")
    print(f"Job Description: {job_description[:100]}...\n")

    try:
        # Select resume content
        selector = ResumeSelector()
        trimmed_data, (is_valid, validation_message) = selector.select_resume_content(full_data, job_description)

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