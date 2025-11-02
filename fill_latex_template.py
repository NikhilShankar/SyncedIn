import json
import subprocess
import os


# --- LaTeX Special Character Escaping Function ---
def escape_latex_special_chars(text):
    """Escapes common LaTeX special characters in a string."""
    if not isinstance(text, str):
        # Should not happen if we pre-process lists correctly, but good for safety.
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


def fill_latex_template(template_path, data, selected_summary_type, selected_companies, selected_projects, output_path):
    """
    Fill LaTeX template with selected data

    Args:
        template_path: Path to LaTeX template file
        data: Dictionary with resume data (from JSON)
        selected_summary_type: Which summary to use (android/fullstack/ml/general)
        selected_companies: List of company IDs to include with selected bullets
        selected_projects: List of project IDs to include
        output_path: Where to save the filled template
    """

    # Read template
    with open(template_path, 'r') as f:
        template = f.read()

    # --- 1. Fill static info (ALWAYS ESCAPE USER-PROVIDED TEXT) ---
    static = data['static_info']
    template = template.replace('{{NAME}}', escape_latex_special_chars(static['name']))
    template = template.replace('{{ADDRESS}}', escape_latex_special_chars(static['address']))
    template = template.replace('{{PHONE}}', escape_latex_special_chars(static['phone']))
    template = template.replace('{{EMAIL}}', escape_latex_special_chars(static['email']))

    # Generate pipe-separated links from the links array
    links_parts = []
    for link in static.get('links', []):
        title = escape_latex_special_chars(link['title'])
        url = link['url']  # Keep raw for href
        links_parts.append(f"\\href{{{url}}}{{{title}}}")
    links_text = " | ".join(links_parts)
    template = template.replace('{{LINKS}}', links_text)

    # Fill summary
    template = template.replace('{{SUMMARY}}', escape_latex_special_chars(data['summaries'][selected_summary_type]))

    # --- 2. Fill technical skills (CONVERT LISTS TO STRINGS & APPLY ESCAPING) ---
    skills_content = data['skills']

    def get_skill_string(key):
        """Helper to safely retrieve skill data, joining lists into a string."""
        value = skills_content[key]
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

    # --- 3. Generate Experience Section ---
    experience_text = ""
    experience_data = data.get('companies', [])
    for company_id in selected_companies:
        company_data = next((c for c in experience_data if c['id'] == company_id['id']), None)
        if company_data:
            # Use data from the dictionary
            title = escape_latex_special_chars(company_data['position'])
            dates = escape_latex_special_chars(company_data['dates'])
            company = escape_latex_special_chars(company_data['name'])
            location = escape_latex_special_chars(company_data['location'])

            experience_text += f"\\resumeSubheading\n"
            experience_text += f"  {{{title}}}{{{dates}}}\n"
            experience_text += f"  {{{company}}}{{{location}}}\n"
            experience_text += f"\\begin{{itemize}}[leftmargin=0.3in]\n"

            # Use selected bullets from the function argument
            for bullet in company_id['bullets']:
                escaped_bullet = escape_latex_special_chars(bullet)
                experience_text += f"  \\resumeItem{{{escaped_bullet}}}\n"

            experience_text += f"\\end{{itemize}}\n\n"

    # FIX: Using {{EXPERIENCE_ITEMS}} to match the placeholder in resume_template.tex
    template = template.replace('{{EXPERIENCE_ITEMS}}', experience_text)

    # --- 4. Generate Education Section (APPLY ESCAPING) ---
    education_text = ""
    for edu in data.get('education', []):
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
    # FIX: Using {{EDUCATION_ITEMS}} to match the placeholder in resume_template.tex
    template = template.replace('{{EDUCATION_ITEMS}}', education_text)

    # --- 5. Generate Projects Section (APPLY ESCAPING) ---
    projects_text = ""
    projects_data = data.get('projects', [])
    for project_id in selected_projects:
        project = next((p for p in projects_data if p['id'] == project_id), None)
        if project:
            # Item line: \item \textbf{Name} - Description
            projects_text += f"    \\item \\textbf{{{escape_latex_special_chars(project['name'])}}} - {escape_latex_special_chars(project['description'])}\n"

            # Details line: \textit{Tech} | Date | \href{link}{Link}
            details_line = f"          \\textit{{{escape_latex_special_chars(project['tech'])}}} | {escape_latex_special_chars(project['date'])}"
            if project.get('link'):
                details_line += f" | \\href{{{project['link']}}}{{Link}}"  # Keep raw for href

            projects_text += details_line + "\n\n"

    # FIX: Using {{PROJECT_ITEMS}} to match the placeholder in resume_template.tex
    template = template.replace('{{PROJECT_ITEMS}}', projects_text)

    # Write the filled content to the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)

    return output_path


def compile_latex_to_pdf(tex_path, output_dir='./../generated'):
    """Compiles a .tex file to PDF using pdflatex."""
    try:
        # We need to run pdflatex multiple times for cross-references (like hyperref)
        command = [
            'lualatex',
            '-output-directory', output_dir,
            '-interaction=nonstopmode',  # Do not stop on minor errors
            tex_path
        ]

        # Run the compilation command twice for safety
        print("Running pdflatex (Pass 1)...")
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Running pdflatex (Pass 2)...")
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Assuming successful compilation, the PDF will have the same name as the TEX file
        pdf_name = os.path.splitext(os.path.basename(tex_path))[0] + '.pdf'
        return os.path.join(output_dir, pdf_name)

    except subprocess.CalledProcessError as e:
        # The compilation error is now expected, but we need to suppress the Python error
        # so the user can see the LaTeX log instead of the Python traceback.
        print(f"Error during PDF compilation:")
        # Print the relevant parts of the log for debugging
        print(f"Stdout (Last 10 lines of log):")
        log_lines = e.stdout.decode().split('\n')
        print('\n'.join(log_lines[-10:]))

        # We don't print the full stderr, as it's often empty or redundant with stdout
        return None
    except FileNotFoundError:
        print(
            "Error: 'pdflatex' command not found. Ensure MiKTeX or TeX Live is installed and added to your system PATH.")
        return None


if __name__ == '__main__':
    # Load data from JSON
    try:
        with open('resume_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: 'resume_data.json' not found. Please ensure it is in the same directory.")
        exit()
    except json.JSONDecodeError:
        print("Error: 'resume_data.json' is improperly formatted JSON.")
        exit()

    # Define the resume content sections based on the profile you want
    selected_companies = [
        {
            "id": "slice",
            "bullets": [
                "Designed core architecture for the UPI payment system using Clean Architecture and MVI, serving 1.5 million users per day as of Feb 2024.",
                "Analyzed, profiled, and reduced network latency by ~18-20%, resulting in faster transaction completion time across the fintech app.",
                "Ensured quality of deliverables by mentoring Junior developers, doing extensive code reviews and walkthroughs and by helping to adhere to best coding practices.",
                "Optimized CI/CD settings in AWS Codebuild and Gradle files to reduce build times by 40% and cost by a huge 70%",
                "Adopted unit tests for modules under the UPI project, achieving 90% code coverage.",
                "Designed a library to create statistical graphs in Jetpack Compose seamlessly and refactored code to achieve minimal re-compositions."
            ]
        },
        {
            "id": "slice2",
            "bullets": [
                "Designed core architecture for the UPI payment system using Clean Architecture and MVI, serving 1.5 million users per day as of Feb 2024.",
                "Analyzed, profiled, and reduced network latency by ~18-20%, resulting in faster transaction completion time across the fintech app.",
                "Ensured quality of deliverables by mentoring Junior developers, doing extensive code reviews and walkthroughs and by helping to adhere to best coding practices.",
                "Optimized CI/CD settings in AWS Codebuild and Gradle files to reduce build times by 40% and cost by a huge 70%",
                "Adopted unit tests for modules under the UPI project, achieving 90% code coverage.",
                "Designed a library to create statistical graphs in Jetpack Compose seamlessly and refactored code to achieve minimal re-compositions."
            ]
        },
        {
            "id": "greedygame",
            "bullets": [
                "Developed core Android library, which other developers can integrate to show native ads. Handling ~5 million ad requests/day.",
                "Refactored a single monolithic codebase into multiple modules following facade, adapter, mediator design patterns, and more, applying good coding standards, reducing development time and cross team conflicts.",
                "Integrated Admob, Mopub and Facebook Ads and wrote wrappers for Unity Game Engine and Cocos-2dx using JNI, C#, and C++, facilitating the Android library to inject ads into games and apps.",
                "Created a Unity game engine plugin that reduced developers' initial integration time from 1-2 days to less than 10 minutes.",
                "Initiated development of the iOS plugin from scratch as a personal project by learning swift and iOS app development which was later incorporated as a separate product line in the organization attracting iOS app and game development companies into the business.",
                "Refactored the monolithic Backend written in NodeJS to microservices based architecture using Golang, which helped streamline the development and reduced overall development time, time for debugging issues, and time for deployment."
            ]
        },
        {
            "id": "greedygame2",
            "bullets": [
                "Developed core Android library, which other developers can integrate to show native ads. Handling ~5 million ad requests/day.",
                "Refactored a single monolithic codebase into multiple modules following facade, adapter, mediator design patterns, and more, applying good coding standards, reducing development time and cross team conflicts.",
                "Integrated Admob, Mopub and Facebook Ads and wrote wrappers for Unity Game Engine and Cocos-2dx using JNI, C#, and C++, facilitating the Android library to inject ads into games and apps.",
                "Created a Unity game engine plugin that reduced developers' initial integration time from 1-2 days to less than 10 minutes.",
                "Initiated development of the iOS plugin from scratch as a personal project by learning swift and iOS app development which was later incorporated as a separate product line in the organization attracting iOS app and game development companies into the business.",
                "Refactored the monolithic Backend written in NodeJS to microservices based architecture using Golang, which helped streamline the development and reduced overall development time, time for debugging issues, and time for deployment."
            ]
        }
    ]

    selected_projects = ['aingel', 'fanfight', 'phifactory']

    # Fill template
    print("Filling LaTeX template...")
    filled_tex = fill_latex_template(
        template_path='resume_template.tex',
        data=data,
        selected_summary_type='android',
        selected_companies=selected_companies,
        selected_projects=selected_projects,
        output_path='./../generated/resume_filled.tex'
    )

    print(f"✅ LaTeX file generated: {filled_tex}")
    print("📄 Open 'resume_filled.tex' in TeXWorks to compile to PDF manually")

    # Try to compile to PDF (optional)
    print("\nAttempting PDF compilation...")
    pdf_path = compile_latex_to_pdf(filled_tex, output_dir='./../generated')

    if pdf_path:
        print(f"✅ Resume PDF generated: {pdf_path}")
    else:
        print("❌ PDF compilation failed - please compile manually in TeXWorks and check the log for specific errors.")
