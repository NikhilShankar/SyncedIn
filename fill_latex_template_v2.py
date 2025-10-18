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

    # Read template
    with open(template_path, 'r') as f:
        template = f.read()

    # --- 1. Fill static info (ALWAYS ESCAPE USER-PROVIDED TEXT) ---
    static = trimmed_resume_data['static_info']
    template = template.replace('{{NAME}}', escape_latex_special_chars(static['name']))
    template = template.replace('{{ADDRESS}}', escape_latex_special_chars(static['address']))
    template = template.replace('{{PHONE}}', escape_latex_special_chars(static['phone']))
    template = template.replace('{{EMAIL}}', escape_latex_special_chars(static['email']))
    template = template.replace('{{LINKEDIN}}', static['linkedin'])  # Keep raw for href
    #template = template.replace('{{PORTFOLIO}}', static['portfolio'])  # Keep raw for href
    template = template.replace('{{LEETCODE}}', static['leetcode'])  # Keep raw for href

    # --- 2. Fill summary (LLM should select which summary type to use) ---
    # The trimmed JSON will have only ONE summary in the 'summaries' dict
    summaries = trimmed_resume_data.get('summaries', {})
    if summaries:
        # Get the first (and only) summary value
        summary_text = list(summaries.values())[0]
        template = template.replace('{{SUMMARY}}', escape_latex_special_chars(summary_text))

    # --- 3. Fill technical skills (CONVERT LISTS TO STRINGS & APPLY ESCAPING) ---
    skills_content = trimmed_resume_data.get('skills', {})

    def get_skill_string(key):
        """Helper to safely retrieve skill data, joining lists into a string."""
        value = skills_content.get(key, [])
        if isinstance(value, list):
            # Join list into a comma-separated string, as expected by LaTeX formatting
            return ", ".join(value)
        return value

    template = template.replace('{{LANGUAGES}}', escape_latex_special_chars(get_skill_string('languages')))
    template = template.replace('{{PLATFORMS}}', escape_latex_special_chars(get_skill_string('platforms')))
    template = template.replace('{{SKILLS}}', escape_latex_special_chars(get_skill_string('skills')))
    template = template.replace('{{FRAMEWORKS}}', escape_latex_special_chars(get_skill_string('frameworks')))
    template = template.replace('{{TOOLS}}', escape_latex_special_chars(get_skill_string('tools')))
    template = template.replace('{{DATABASE}}', escape_latex_special_chars(get_skill_string('database')))

    # --- 4. Generate Experience Section ---
    experience_text = ""
    companies = trimmed_resume_data.get('companies', [])

    for company in companies:
        # Extract company info
        title = escape_latex_special_chars(company['position'])
        dates = escape_latex_special_chars(company['dates'])
        company_name = escape_latex_special_chars(company['name'])
        location = escape_latex_special_chars(company['location'])

        experience_text += f"\\resumeSubheading\n"
        experience_text += f"  {{{title}}}{{{dates}}}\n"
        experience_text += f"  {{{company_name}}}{{{location}}}\n"
        experience_text += f"\\begin{{itemize}}[leftmargin=0.3in]\n"

        # Bullets are objects with 'text' field
        for bullet in company.get('bullets', []):
            escaped_bullet = escape_latex_special_chars(bullet['text'])
            experience_text += f"  \\resumeItem{{{escaped_bullet}}}\n"

        experience_text += f"\\end{{itemize}}\n\n"

    template = template.replace('{{EXPERIENCE_ITEMS}}', experience_text)

    # --- 5. Generate Education Section (APPLY ESCAPING) ---
    education_text = ""
    for edu in trimmed_resume_data.get('education', []):
        degree = escape_latex_special_chars(edu['degree'])
        dates = escape_latex_special_chars(edu['dates'])
        course = escape_latex_special_chars(edu['course'])
        institution = escape_latex_special_chars(edu['institution'])
        location = escape_latex_special_chars(edu['location'])
        empty = ""
        education_text += f"\\resumeThreeLineSubheading\n"
        education_text += f"  {{{degree}}}\n"
        education_text += f"  {{{dates}}}\n"
        education_text += f"  {{{course}}}\n"
        education_text += f"  {{{location}}}\n"
        education_text += f"  {{{institution}}}\n"
        education_text += f"  {{{empty}}}\n\n"

    template = template.replace('{{EDUCATION_ITEMS}}', education_text)

    # --- 6. Generate Projects Section (APPLY ESCAPING) ---
    projects_text = ""
    projects = trimmed_resume_data.get('projects', [])

    for project in projects:
        # Item line: \item \textbf{Name} - Description
        projects_text += f"    \\item \\textbf{{{escape_latex_special_chars(project['name'])}}} - {escape_latex_special_chars(project['description'])}\n"

        # Details line: \textit{Tech} | Date | \href{link}{Link}
        details_line = f"          \\textit{{{escape_latex_special_chars(project['tech'])}}} | {escape_latex_special_chars(project['date'])}"
        if project.get('link'):
            details_line += f" | \\href{{{project['link']}}}{{Link}}"  # Keep raw for href

        projects_text += details_line + "\n\n"

    template = template.replace('{{PROJECT_ITEMS}}', projects_text)

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
        "summaries": {
            "android": full_data["summaries"]["android"]  # LLM selected 'android' summary
        },
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