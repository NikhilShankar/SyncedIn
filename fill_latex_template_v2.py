import json
import subprocess
import os


# --- LaTeX Special Character Escaping Function ---
def escape_latex_special_chars(text):
    """Escapes common LaTeX special characters in a string."""
    if not isinstance(text, str):
        return text

    # List of common LaTeX special characters that need escaping
    text = text.replace('\\', '\\textbackslash{}')  # Must be first
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')
    text = text.replace('$', '\\$')
    text = text.replace('&', '\\&')
    text = text.replace('#', '\\#')  # FIX: Escapes C# to C\#
    text = text.replace('%', '\\%')
    text = text.replace('_', '\\_')
    text = text.replace('~', '\\textasciitilde{}')
    text = text.replace('^', '\\textasciicircum{}')
    return text


def fill_latex_template(template_path, trimmed_resume_data, output_path):
    """
    Fill LaTeX template with trimmed resume data from LLM.

    Args:
        template_path: Path to LaTeX template file
        trimmed_resume_data: Dictionary with TRIMMED resume data (subset returned by LLM)
                            This should have the EXACT same structure as the original JSON,
                            just with fewer items selected.
        output_path: Where to save the filled template

    Returns:
        Path to the generated .tex file
    """

    # Default display settings if not provided
    default_display_settings = {
        "sections": {
            "summary": {"enabled": True, "title": "Professional Summary"},
            "experience": {"enabled": True, "title": "Professional Experience"},
            "skills": {
                "enabled": True,
                "title": "Technical Skills",
                "categories": ["Languages", "Platforms", "Skills", "Frameworks", "Tools", "Database"]
            },
            "education": {"enabled": True, "title": "Education"},
            "projects": {"enabled": True, "title": "Personal Projects"}
        }
    }

    # Get display settings from data or use defaults
    display_settings = trimmed_resume_data.get('display_settings', default_display_settings)
    sections = display_settings.get('sections', default_display_settings['sections'])

    # Read template
    with open(template_path, 'r') as f:
        template = f.read()

    # --- 1. Fill static info (ALWAYS ESCAPE USER-PROVIDED TEXT) ---
    static = trimmed_resume_data['static_info']
    template = template.replace('{{NAME}}', escape_latex_special_chars(static['name']))
    template = template.replace('{{ADDRESS}}', escape_latex_special_chars(static['address']))
    template = template.replace('{{PHONE}}', escape_latex_special_chars(static['phone']))
    template = template.replace('{{EMAIL}}', escape_latex_special_chars(static['email']))

    # Handle links - support both old format (linkedin, leetcode fields) and new format (links array)
    if 'links' in static and isinstance(static['links'], list):
        # New format: links array
        # Generate pipe-separated links for new template format
        links_parts = []
        for link in static['links']:
            title = escape_latex_special_chars(link.get('title', ''))
            url = link.get('url', '')  # Keep raw for href
            if title and url:
                links_parts.append(f"\\href{{{url}}}{{{title}}}")
        links_text = " | ".join(links_parts)
        template = template.replace('{{LINKS}}', links_text)

        # Also support old template format for backwards compatibility
        linkedin_url = ""
        leetcode_url = ""
        portfolio_url = ""

        for link in static['links']:
            link_title = link.get('title', '').lower()
            if 'linkedin' in link_title:
                linkedin_url = link.get('url', '')
            elif 'leetcode' in link_title:
                leetcode_url = link.get('url', '')
            elif 'portfolio' in link_title or 'website' in link_title:
                portfolio_url = link.get('url', '')

        template = template.replace('{{LINKEDIN}}', linkedin_url)
        template = template.replace('{{LEETCODE}}', leetcode_url)
        template = template.replace('{{PORTFOLIO}}', portfolio_url)
    else:
        # Old format: separate fields
        template = template.replace('{{LINKEDIN}}', static.get('linkedin', ''))
        template = template.replace('{{LEETCODE}}', static.get('leetcode', ''))
        template = template.replace('{{PORTFOLIO}}', static.get('portfolio', ''))
        template = template.replace('{{LINKS}}', '')

    # --- 2. Build Summary Section ---
    summary_section = ""
    if sections.get('summary', {}).get('enabled', True):
        summaries = trimmed_resume_data.get('summaries', [])
        if summaries:
            summary_title = sections['summary'].get('title', 'Professional Summary')
            # Handle both array (new format) and dict (old format) for backward compatibility
            if isinstance(summaries, list):
                summary_text = summaries[0].get('text', '') if summaries else ''
            else:
                # Backward compatibility with old dict format
                summary_text = list(summaries.values())[0] if summaries else ''

            if summary_text:
                summary_section = f"%----------{summary_title.upper()}----------\n"
                summary_section += f"\\section{{{summary_title}}}\n"
                summary_section += escape_latex_special_chars(summary_text)

    template = template.replace('{{SUMMARY_SECTION}}', summary_section)

    # --- 3. Build Experience Section ---
    experience_section = ""
    if sections.get('experience', {}).get('enabled', True):
        companies = trimmed_resume_data.get('companies', [])
        if companies:
            experience_title = sections['experience'].get('title', 'Professional Experience')
            experience_section = f"%----------{experience_title.upper()}----------\n"
            experience_section += f"\\section{{{experience_title}}}\n"
            experience_section += "\\begin{itemize}[leftmargin=0.15in, label={}]\n"

            for company in companies:
                title = escape_latex_special_chars(company['position'])
                dates = escape_latex_special_chars(company['dates'])
                company_name = escape_latex_special_chars(company['name'])
                location = escape_latex_special_chars(company['location'])

                experience_section += f"\\resumeSubheading\n"
                experience_section += f"  {{{title}}}{{{dates}}}\n"
                experience_section += f"  {{{company_name}}}{{{location}}}\n"
                experience_section += f"\\begin{{itemize}}[leftmargin=0.3in]\n"

                for bullet in company.get('bullets', []):
                    escaped_bullet = escape_latex_special_chars(bullet['text'])
                    experience_section += f"  \\resumeItem{{{escaped_bullet}}}\n"

                experience_section += f"\\end{{itemize}}\n\n"

            experience_section += "\\end{itemize}\n"

    template = template.replace('{{EXPERIENCE_SECTION}}', experience_section)

    # --- 4. Build Skills Section with Dynamic Categories ---
    skills_section = ""
    if sections.get('skills', {}).get('enabled', True):
        skills_content = trimmed_resume_data.get('skills', {})
        if skills_content:
            skills_title = sections['skills'].get('title', 'Technical Skills')
            categories = sections['skills'].get('categories',
                ["Languages", "Platforms", "Skills", "Frameworks", "Tools", "Database"])

            # Skill keys in order (must match the categories array order)
            skill_keys = ['languages', 'platforms', 'skills', 'frameworks', 'tools', 'database']

            skills_section = f"%----------{skills_title.upper()}----------\n"
            skills_section += f"\\section{{{skills_title}}}\n"
            skills_section += "\\begin{itemize}[leftmargin=0.15in, label={}]\n"
            skills_section += "    \\normalfont{\\item{\n"

            # Build skill category lines dynamically
            skill_lines = []
            for i, key in enumerate(skill_keys):
                if i < len(categories):  # Only if we have a title for this category
                    value = skills_content.get(key, [])
                    if value:  # Only add if there's content
                        if isinstance(value, list):
                            value_str = ", ".join(value)
                        else:
                            value_str = value
                        category_title = categories[i]
                        skill_lines.append(f"     \\textbf{{{category_title}: }}{{{escape_latex_special_chars(value_str)}}}")

            # Join with \\ and add final line
            skills_section += " \\\\\n".join(skill_lines)
            skills_section += "\n    }}\n\\end{itemize}\n"

    template = template.replace('{{SKILLS_SECTION}}', skills_section)

    # --- 5. Build Education Section ---
    education_section = ""
    if sections.get('education', {}).get('enabled', True):
        education_data = trimmed_resume_data.get('education', [])
        if education_data:
            education_title = sections['education'].get('title', 'Education')
            education_section = f"%----------{education_title.upper()}----------\n"
            education_section += f"\\section{{{education_title}}}\n"
            education_section += "\\begin{itemize}[leftmargin=0.15in, label={}]\n"

            for edu in education_data:
                degree = escape_latex_special_chars(edu['degree'])
                dates = escape_latex_special_chars(edu['dates'])
                course = escape_latex_special_chars(edu['course'])
                institution = escape_latex_special_chars(edu['institution'])
                location = escape_latex_special_chars(edu['location'])
                empty = ""
                education_section += f"\\resumeThreeLineSubheading\n"
                education_section += f"  {{{degree}}}\n"
                education_section += f"  {{{dates}}}\n"
                education_section += f"  {{{course}}}\n"
                education_section += f"  {{{location}}}\n"
                education_section += f"  {{{institution}}}\n"
                education_section += f"  {{{empty}}}\n\n"

            education_section += "\\end{itemize}\n"

    template = template.replace('{{EDUCATION_SECTION}}', education_section)

    # --- 6. Build Projects Section ---
    projects_section = ""
    if sections.get('projects', {}).get('enabled', True):
        projects = trimmed_resume_data.get('projects', [])
        if projects:
            projects_title = sections['projects'].get('title', 'Personal Projects')
            projects_section = f"%----------{projects_title.upper()}----------\n"
            projects_section += f"\\section{{{projects_title}}}\n"
            projects_section += "\\begin{itemize}[leftmargin=0.15in, label={}]\n"

            for project in projects:
                projects_section += f"    \\item \\textbf{{{escape_latex_special_chars(project['name'])}}} - {escape_latex_special_chars(project['description'])}\n"

                details_line = f"          \\textit{{{escape_latex_special_chars(project['tech'])}}} | {escape_latex_special_chars(project['date'])}"
                if project.get('link'):
                    details_line += f" | \\href{{{project['link']}}}{{Link}}"

                projects_section += details_line + "\n\n"

            projects_section += "\\end{itemize}\n"

    template = template.replace('{{PROJECTS_SECTION}}', projects_section)

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Write the filled content to the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)

    return output_path


def compile_latex_to_pdf(tex_path, output_dir='./generated'):
    """Compiles a .tex file to PDF using lualatex."""
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # We need to run lualatex multiple times for cross-references (like hyperref)
        command = [
            'lualatex',
            '-output-directory', output_dir,
            '-interaction=nonstopmode',  # Do not stop on minor errors
            tex_path
        ]

        # Run the compilation command twice for safety
        print("Running lualatex (Pass 1)...")
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Running lualatex (Pass 2)...")
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Assuming successful compilation, the PDF will have the same name as the TEX file
        pdf_name = os.path.splitext(os.path.basename(tex_path))[0] + '.pdf'
        return os.path.join(output_dir, pdf_name)

    except subprocess.CalledProcessError as e:
        print(f"Error during PDF compilation:")
        print(f"Stdout (Last 10 lines of log):")
        log_lines = e.stdout.decode().split('\n')
        print('\n'.join(log_lines[-10:]))
        return None
    except FileNotFoundError:
        print("Error: 'lualatex' command not found. Ensure TeX Live is installed and added to your system PATH.")
        return None


if __name__ == '__main__':
    """
    Example usage with a MOCK trimmed JSON (simulating LLM output).
    In production, this trimmed_resume_data would come from the LLM selector.
    """

    # Load the FULL data from JSON (in production, LLM would receive this)
    try:
        with open('resume_data_enhanced.json', 'r') as f:
            full_data = json.load(f)
    except FileNotFoundError:
        print("Error: 'resume_data_enhanced.json' not found.")
        exit()
    except json.JSONDecodeError:
        print("Error: 'resume_data_enhanced.json' is improperly formatted JSON.")
        exit()

    # MOCK: Simulate LLM output - a trimmed version of the full JSON
    # In production, this would be returned by llm_selector.py
    trimmed_resume_data = {
        "static_info": full_data["static_info"],
        "summaries": [
            full_data["summaries"][0]  # LLM selected first summary option
        ],
        "skills": {
            # LLM trimmed skills based on job description
            "languages": ["Kotlin", "Java", "Python", "Dart", "Golang"],
            "platforms": ["Android Studio", "Firebase", "AWS", "IntelliJ", "VSCode"],
            "skills": [
                "Modular code using MVVM MVI and Clean Architecture",
                "Multi Module App Design",
                "Complex UI Development using Compose",
                "UI Optimizations",
                "Design patterns",
                "Code Reviews and detecting code smells and bugs",
                "Performance profiling",
                "Mentoring Junior Developers"
            ],
            "frameworks": [
                "Android SDK", "Jetpack Compose", "Retrofit", "OkHttp",
                "Dagger", "Hilt", "Room", "Coroutines", "Livedata"
            ],
            "tools": ["Git", "AS Profiler", "Debugger", "Postman", "Leak Canary", "Github Actions"],
            "database": ["SQLite", "Firebase Firestore", "MongoDB", "Room"]
        },
        "companies": [
            {
                "id": "slice",
                "name": "Slice, Fintech",
                "position": "Software Development Engineer 3 - Android",
                "dates": "Nov 2022 - Feb 2024",
                "location": "Bengaluru, India",
                "bullets": [
                    {
                        "text": "Designed core architecture for the UPI payment system using Clean Architecture and MVI, serving 1.5 million users per day as of Feb 2024."},
                    {
                        "text": "Analyzed, profiled, and reduced network latency by ~18-20%, resulting in faster transaction completion time across the fintech app."},
                    {
                        "text": "Optimized CI/CD settings in AWS Codebuild and Gradle files to reduce build times by 40% and cost by a huge 70%"},
                    {"text": "Adopted unit tests for modules under the UPI project, achieving 90% code coverage."},
                    {
                        "text": "Designed a library to create statistical graphs in Jetpack Compose seamlessly and refactored code to achieve minimal re-compositions."}
                ]
            },
            {
                "id": "slice2",
                "name": "Slice, Fintech",
                "position": "Software Development Engineer 2 - Android",
                "dates": "Nov 2020 - Nov 2022",
                "location": "Bengaluru, India",
                "bullets": [
                    {
                        "text": "Ensured quality of deliverables by mentoring Junior developers, doing extensive code reviews and walkthroughs and by helping to adhere to best coding practices."},
                    {
                        "text": "Designed and created architecture for web socket library for real-time chat and achieved seamless integration between backend API's and complex UI elements of chat feature."},
                    {
                        "text": "Analyzed, profiled, and reduced network latency by ~18-20%, resulting in faster transaction completion time across the fintech app."},
                    {"text": "Adopted unit tests for modules under the UPI project, achieving 90% code coverage."}
                ]
            },
            {
                "id": "greedygame",
                "name": "GreedyGame, Ad-Tech",
                "position": "Fullstack Developer iOS, Backend",
                "dates": "Sep 2015 - Oct 2019",
                "location": "Bengaluru, India",
                "bullets": [
                    {
                        "text": "Initiated development of the iOS plugin from scratch as a personal project by learning swift and iOS app development which was later incorporated as a separate product line in the organization attracting iOS app and game development companies into the business."},
                    {
                        "text": "Refactored the monolithic Backend written in NodeJS to microservices based architecture using Golang, which helped streamline the development and reduced overall development time, time for debugging issues, and time for deployment."},
                    {
                        "text": "Integrated Jenkins CI/CD pipeline for automating artifact creation thereby reducing previous manual effort of 2-3 hours"},
                    {
                        "text": "Developed integration documentation website in Angular JS thereby reducing integration related queries"}
                ]
            },
            {
                "id": "greedygame2",
                "name": "GreedyGame, Ad-Tech",
                "position": "Senior Developer | Android",
                "dates": "Sep 2015 - Apr 2018",
                "location": "Bengaluru, India",
                "bullets": [
                    {
                        "text": "Developed core Android library, which other developers can integrate to show native ads, focusing on optimization and performance thereby reducing memory consumption and library conflicts"},
                    {
                        "text": "Refactored a single monolithic codebase into multiple modules following facade, adapter, mediator design patterns, and more, applying good coding standards, reducing development time and cross team conflicts."},
                    {
                        "text": "Integrated Admob, Mopub and Facebook Ads and wrote wrappers for Unity Game Engine and Cocos-2dx using JNI, C#, and C++, facilitating the Android library to inject ads into games and apps thereby increasing compatible dev environment by 4x"},
                    {
                        "text": "Created a Unity game engine plugin that reduced developers' initial integration time from 1-2 days to less than 10 minutes."}
                ]
            }
        ],
        "projects": [
            {
                "id": "aingel",
                "name": "AIngel",
                "tech": "Android, AI, LLMs, Machine Learning",
                "description": "An android app to nurture relationships created using AI powered bots with LLMs and Machine Learning algorithms to find meaningful matches. This is currently part of Venture Tech Lab CEC Conestoga College.",
                "date": "Jan 2025",
                "link": ""
            },
            {
                "id": "fanfight",
                "name": "Fan Fight Club",
                "tech": "Android, Python Scripts",
                "description": "An android repository that can be used to generate multiple apps by using python scripts. Fan Fight Club Messi vs Ronaldo was one such app out of around 10 that were created which garnered 2 lakh installs with more than 200 ratings averaged at 4.7/5 stars",
                "date": "2019",
                "link": "https://bitbucket.org/nikhilshankarcs/fanfightclub"
            }
        ],
        "education": full_data["education"]
    }

    # Fill template with the trimmed data
    print("Filling LaTeX template with trimmed resume data...")
    filled_tex = fill_latex_template(
        template_path='resume_template.tex',
        trimmed_resume_data=trimmed_resume_data,
        output_path='./generated/resume_filled.tex'
    )

    print(f"✅ LaTeX file generated: {filled_tex}")

    # Try to compile to PDF (optional)
    print("\nAttempting PDF compilation...")
    pdf_path = compile_latex_to_pdf(filled_tex, output_dir='./generated')

    if pdf_path:
        print(f"✅ Resume PDF generated: {pdf_path}")
    else:
        print("❌ PDF compilation failed - please check the LaTeX log for errors.")