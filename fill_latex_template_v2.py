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


# ============= SECTION BUILDER FUNCTIONS =============

def build_summary_section(trimmed_resume_data, sections):
    """Build Professional Summary section"""
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
                summary_section += escape_latex_special_chars(summary_text) + "\n"

    return summary_section


def build_experience_section(trimmed_resume_data, sections):
    """Build Professional Experience section"""
    experience_section = ""
    if sections.get('experience', {}).get('enabled', True):
        companies = trimmed_resume_data.get('companies', [])
        if companies:
            experience_title = sections['experience'].get('title', 'Professional Experience')
            experience_section = f"%----------{experience_title.upper()}----------\n"
            experience_section += f"\\section{{{experience_title}}}\n"
            experience_section += "\\begin{itemize}[leftmargin=0.0in, label={}]\n"

            for company in companies:
                title = escape_latex_special_chars(company['position'])
                dates = escape_latex_special_chars(company['dates'])
                company_name = escape_latex_special_chars(company['name'])
                location = escape_latex_special_chars(company['location'])

                experience_section += f"\\resumeSubheading\n"
                experience_section += f"  {{{title}}}{{{dates}}}\n"
                experience_section += f"  {{{company_name}}}{{{location}}}\n"
                experience_section += f"\\begin{{itemize}}[leftmargin=0.15in]\n"

                for bullet in company.get('bullets', []):
                    escaped_bullet = escape_latex_special_chars(bullet['text'])
                    experience_section += f"  \\resumeItem{{{escaped_bullet}}}\n"

                experience_section += f"\\end{{itemize}}\n\n"

            experience_section += "\\end{itemize}\n"

    return experience_section


def build_skills_section(trimmed_resume_data, sections):
    """Build Technical Skills section"""
    skills_section = ""
    if sections.get('skills', {}).get('enabled', True):
        skills_content = trimmed_resume_data.get('skills', {})
        if skills_content:
            skills_title = sections['skills'].get('title', 'Technical Skills')

            skills_section = f"%----------{skills_title.upper()}----------\n"
            skills_section += f"\\section{{{skills_title}}}\n"
            skills_section += "\\begin{itemize}[leftmargin=0.0in, label={}]\n"
            skills_section += "    \\normalfont{\\item{\n"

            # Build skill category lines dynamically
            skill_lines = []

            # Handle both v1.0 (dict) and v2.0 (array) formats
            if isinstance(skills_content, list):
                # New v2.0 format - array of skill sections
                for skill_section_data in skills_content:
                    title = skill_section_data.get('title', '')
                    items = skill_section_data.get('items', [])

                    if items:  # Only add if there's content
                        if isinstance(items, list):
                            value_str = ", ".join(items)
                        else:
                            value_str = items
                        skill_lines.append(f"     \\textbf{{{title}: }}{{{escape_latex_special_chars(value_str)}}}")
            else:
                # Old v1.0 format - dict with hardcoded categories (backward compatibility)
                categories = sections['skills'].get('categories',
                    ["Languages", "Platforms", "Skills", "Frameworks", "Tools", "Database"])
                skill_keys = ['languages', 'platforms', 'skills', 'frameworks', 'tools', 'database']

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

    return skills_section


def build_projects_section(trimmed_resume_data, sections):
    """Build Personal Projects section"""
    projects_section = ""
    if sections.get('projects', {}).get('enabled', True):
        projects = trimmed_resume_data.get('projects', [])
        if projects:
            projects_title = sections['projects'].get('title', 'Personal Projects')
            projects_section = f"%----------{projects_title.upper()}----------\n"
            projects_section += f"\\section{{{projects_title}}}\n"
            projects_section += "\\begin{itemize}[leftmargin=0.0in, label={}]\n"

            for project in projects:
                projects_section += f"    \\item \\textbf{{{escape_latex_special_chars(project['name'])}}} - {escape_latex_special_chars(project['description'])}\n"

                details_line = f"          \\textit{{{escape_latex_special_chars(project['tech'])}}} | {escape_latex_special_chars(project['date'])}"
                if project.get('link'):
                    details_line += f" | \\href{{{project['link']}}}{{Link}}"

                projects_section += details_line + "\n\n"

            projects_section += "\\end{itemize}\n"

    return projects_section


def build_education_section(trimmed_resume_data, sections):
    """Build Education section"""
    education_section = ""
    if sections.get('education', {}).get('enabled', True):
        education_data = trimmed_resume_data.get('education', [])
        if education_data:
            education_title = sections['education'].get('title', 'Education')
            education_section = f"%----------{education_title.upper()}----------\n"
            education_section += f"\\section{{{education_title}}}\n"
            education_section += "\\begin{itemize}[leftmargin=0in, label={}]\n"

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

    return education_section


def build_custom_section(section_key, section_data, trimmed_resume_data):
    """
    Build custom section based on template type

    Template types:
    - custom_section_template_1: Simple (title, optional subtitle, content)
    - custom_section_template_2: Subsections (no bullets)
    - custom_section_template_3: Subsections with bullets
    """
    custom_section = ""

    if not section_data:
        return custom_section

    template_type = section_data.get('type', '')
    title = escape_latex_special_chars(section_data.get('title', section_key))
    subtitle = escape_latex_special_chars(section_data.get('subtitle', ''))

    # Template 1: Simple section (like summary)
    if template_type == 'custom_section_template_1':
        subtitle_right = escape_latex_special_chars(section_data.get('subtitle_right', ''))
        content = escape_latex_special_chars(section_data.get('content', ''))
        custom_section = f"%----------{title.upper()}----------\n"
        custom_section += f"\\customSectionTemplateOne{{{title}}}{{{subtitle}}}{{{subtitle_right}}}{{{content}}}\n"

    # Template 2: Subsections without bullets
    elif template_type == 'custom_section_template_2':
        sections_list = section_data.get('sections', [])
        if sections_list:
            custom_section = f"%----------{title.upper()}----------\n"
            custom_section += f"\\customSectionTemplateTwo{{{title}}}\n"

            for subsection in sections_list:
                sub_title = escape_latex_special_chars(subsection.get('title', ''))
                sub_subtitle = escape_latex_special_chars(subsection.get('subtitle', ''))
                sub_subtitle_right = escape_latex_special_chars(subsection.get('subtitle_right', ''))
                sub_content = escape_latex_special_chars(subsection.get('content', ''))
                custom_section += f"  \\customSubsectionItemTwo{{{sub_title}}}{{{sub_subtitle}}}{{{sub_subtitle_right}}}{{{sub_content}}}\n"

            custom_section += "\\customSectionTemplateTwoEnd\n"

    # Template 3: Subsections with bullets
    elif template_type == 'custom_section_template_3':
        sections_list = section_data.get('sections', [])
        if sections_list:
            custom_section = f"%----------{title.upper()}----------\n"
            custom_section += f"\\customSectionTemplateThree{{{title}}}\n"

            for subsection in sections_list:
                sub_title = escape_latex_special_chars(subsection.get('title', ''))
                sub_subtitle = escape_latex_special_chars(subsection.get('subtitle', ''))
                sub_subtitle_right = escape_latex_special_chars(subsection.get('subtitle_right', ''))
                custom_section += f"  \\customSubsectionItemThree{{{sub_title}}}{{{sub_subtitle}}}{{{sub_subtitle_right}}}\n"

                # Add bullet points
                content = subsection.get('content', [])
                if isinstance(content, list):
                    for bullet in content:
                        escaped_bullet = escape_latex_special_chars(bullet)
                        custom_section += f"    \\customBulletItem{{{escaped_bullet}}}\n"

                custom_section += "  \\customSubsectionItemThreeEnd\n"

            custom_section += "\\customSectionTemplateThreeEnd\n"

    return custom_section


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

    # --- 1.1 Fill font settings ---
    # Default font settings if not provided
    default_font_settings = {
        "family": "Lato",
        "sizes": {
            "title": 12,
            "subtitle": 10,
            "content": 11
        }
    }

    font_settings = trimmed_resume_data.get('font_settings', default_font_settings)
    font_family = font_settings.get('family', 'Lato')
    sizes = font_settings.get('sizes', default_font_settings['sizes'])

    title_size = sizes.get('title', 12)
    subtitle_size = sizes.get('subtitle', 10)
    content_size = sizes.get('content', 11)

    # Calculate leading (line spacing) - typically 1.2x font size (keep float precision)
    title_leading = title_size * 1.2
    subtitle_leading = subtitle_size * 1.2
    content_leading = content_size * 1.2

    # For documentclass, round to nearest integer (LaTeX only accepts standard sizes like 10pt, 11pt, 12pt)
    content_size_rounded = round(content_size)

    template = template.replace('{{FONT_FAMILY}}', font_family)
    template = template.replace('{{CONTENT_FONTSIZE_ROUNDED}}', str(content_size_rounded))
    template = template.replace('{{CONTENT_FONTSIZE}}', str(content_size))
    template = template.replace('{{CONTENT_FONTSIZE_LEADING}}', str(content_leading))
    template = template.replace('{{TITLE_FONTSIZE}}', str(title_size))
    template = template.replace('{{TITLE_FONTSIZE_LEADING}}', str(title_leading))
    template = template.replace('{{SUBTITLE_FONTSIZE}}', str(subtitle_size))
    template = template.replace('{{SUBTITLE_FONTSIZE_LEADING}}', str(subtitle_leading))

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

    # --- 2. Build sections dynamically based on section_order ---

    # Get section_order from data, or use default order
    default_section_order = ['summary', 'skills', 'experience', 'projects', 'education']
    section_order = trimmed_resume_data.get('section_order', default_section_order)

    # Standard section names
    standard_sections = ['summary', 'experience', 'skills', 'projects', 'education']

    # Map section names to their builder functions
    section_builders = {
        'summary': build_summary_section,
        'experience': build_experience_section,
        'skills': build_skills_section,
        'projects': build_projects_section,
        'education': build_education_section
    }

    # Build sections in the order specified
    all_sections_latex = []

    for section_key in section_order:
        if section_key in standard_sections:
            # Standard section - use builder function
            section_latex = section_builders[section_key](trimmed_resume_data, sections)
            if section_latex:
                all_sections_latex.append(section_latex)
        else:
            # Custom section - check if it exists in data
            if section_key in trimmed_resume_data:
                section_data = trimmed_resume_data[section_key]
                section_latex = build_custom_section(section_key, section_data, trimmed_resume_data)
                if section_latex:
                    all_sections_latex.append(section_latex)

    # Join all sections with newlines
    all_sections_content = "\n".join(all_sections_latex)

    # Replace old placeholders with empty strings (for backward compatibility)
    template = template.replace('{{SUMMARY_SECTION}}', '')
    template = template.replace('{{EXPERIENCE_SECTION}}', '')
    template = template.replace('{{SKILLS_SECTION}}', '')
    template = template.replace('{{EDUCATION_SECTION}}', '')
    template = template.replace('{{PROJECTS_SECTION}}', '')

    # Insert all sections before \end{document}
    template = template.replace('\\end{document}', all_sections_content + '\n\\end{document}')

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
    Example usage with resume data.
    """

    # Load the FULL data from JSON
    try:
        with open('resume_data_enhanced.json', 'r') as f:
            full_data = json.load(f)
    except FileNotFoundError:
        print("Error: 'resume_data_enhanced.json' not found.")
        exit()
    except json.JSONDecodeError:
        print("Error: 'resume_data_enhanced.json' is improperly formatted JSON.")
        exit()

    # Use the full data (for testing section ordering)
    trimmed_resume_data = full_data

    # Fill template with the data
    print("Filling LaTeX template with resume data...")
    filled_tex = fill_latex_template(
        template_path='resume_template.tex',
        trimmed_resume_data=trimmed_resume_data,
        output_path='./generated/resume_filled.tex'
    )

    print(f"[OK] LaTeX file generated: {filled_tex}")

    # Try to compile to PDF (optional)
    print("\nAttempting PDF compilation...")
    pdf_path = compile_latex_to_pdf(filled_tex, output_dir='./generated')

    if pdf_path:
        print(f"[OK] Resume PDF generated: {pdf_path}")
    else:
        print("[ERROR] PDF compilation failed - please check the LaTeX log for errors.")