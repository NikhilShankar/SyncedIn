import streamlit as st
import os
import json
from pathlib import Path
from llm_selector import ResumeSelector
from fill_latex_template_v2 import fill_latex_template
import subprocess
import base64


def show():
    """Generate Resume Page"""

    # Title
    st.markdown("<h1 class='main-header'>🤖 Generate Tailored Resume</h1>", unsafe_allow_html=True)
    st.markdown("Generate tailored resumes using Claude AI")

    # Settings in sidebar
    with st.sidebar:
        st.markdown("---")
        st.header("⚙️ Settings")

        # API Key input
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=os.getenv('ANTHROPIC_API_KEY', ''),
            help="Your Anthropic API key (starts with sk-ant-)"
        )

        # Model selection
        model = st.selectbox(
            "Claude Model",
            options=[
                "claude-3-5-haiku-20241022",
                "claude-sonnet-4-20250514",
                "claude-3-5-sonnet-20241022"
            ],
            index=0,
            help="Haiku: Fast & cheap | Sonnet: Better quality"
        )

        # Rewrite mode
        should_rewrite = st.checkbox(
            "Enable Rewrite Mode",
            value=True,
            help="Rephrase bullets to match job (use with caution)"
        )

        # Organized saving
        save_organized = st.checkbox(
            "Save to Organized Folders",
            value=True,
            help="Save PDFs in Month/Company/Name structure"
        )

        # Output folder path
        output_base_path = st.text_input(
            "Output Folder Path",
            value=os.getenv('OUTPUT_BASE_PATH', './output'),
            help="Base folder for organized PDFs (e.g., D:/Resumes/output)"
        )

        # Resume data path
        resume_data_path = st.text_input(
            "Resume Data Path",
            value="resume_data_enhanced.json",
            help="Path to your resume JSON file"
        )

        # Template path
        template_path = st.text_input(
            "LaTeX Template Path",
            value="resume_template.tex",
            help="Path to your LaTeX template"
        )

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📝 Input")

        # Company name
        company_name = st.text_input(
            "Company Name *",
            placeholder="e.g., Google, Meta, Apple",
            help="The company you're applying to"
        )

        # Job description
        job_description = st.text_area(
            "Job Description *",
            height=400,
            placeholder="""Paste the job description here...

Example:
Senior Android Developer

We are looking for an experienced Android developer...

Requirements:
- 5+ years of Android development
- Expert in Kotlin and Java
- Experience with Jetpack Compose
""",
            help="Paste the full job description"
        )

    with col2:
        st.header("📊 Output")

        # Status container
        status_container = st.empty()

        # Output display
        output_container = st.container()

    # Generate button
    if st.button("🚀 Generate Resume", type="primary", use_container_width=True):

        # Validation
        if not company_name:
            st.error("❌ Please enter a company name")
            st.stop()

        if not job_description:
            st.error("❌ Please enter a job description")
            st.stop()

        if not api_key:
            st.error("❌ Please enter your Anthropic API key in the sidebar")
            st.stop()

        if not os.path.exists(resume_data_path):
            st.error(f"❌ Resume data file not found: {resume_data_path}")
            st.stop()

        if not os.path.exists(template_path):
            st.error(f"❌ LaTeX template not found: {template_path}")
            st.stop()

        # Save to session state for later use
        st.session_state.company_name = company_name
        st.session_state.job_description = job_description
        st.session_state.template_path = template_path

        # Create output directory
        output_dir = Path("./generated")
        output_dir.mkdir(exist_ok=True)

        try:
            with status_container:
                # Step 1: Load resume data
                with st.status("🔄 Processing...", expanded=True) as status:
                    st.write("📂 Loading resume data...")
                    with open(resume_data_path, 'r') as f:
                        full_resume_data = json.load(f)

                    # Step 2: LLM Selection
                    st.write(f"🤖 Using {model} to select content...")
                    st.write(f"{'✏️ Rewrite mode ENABLED' if should_rewrite else '📋 Exact mode (no rewriting)'}")

                    selector = ResumeSelector(api_key=api_key, model=model)
                    trimmed_data, (is_valid, validation_message) = selector.select_resume_content(
                        full_resume_data,
                        job_description,
                        should_rewrite_selected=should_rewrite
                    )

                    # Show validation result
                    if is_valid:
                        st.write("✅ Validation passed")
                    else:
                        st.warning(f"⚠️ Validation warnings:\n{validation_message}")

                    # Save trimmed data to session state
                    st.session_state.trimmed_data = trimmed_data

                    # Save trimmed data to file
                    trimmed_json_path = output_dir / "resume_data_trimmed.json"
                    with open(trimmed_json_path, 'w') as f:
                        json.dump(trimmed_data, f, indent=2)
                    st.write(f"💾 Saved trimmed data: {trimmed_json_path}")

                    # Step 3: Fill LaTeX template
                    st.write("📝 Filling LaTeX template...")
                    filled_tex = output_dir / "resume_filled.tex"

                    # Pass the data dict, not the file path
                    fill_latex_template(
                        str(template_path),
                        trimmed_data,
                        str(filled_tex)
                    )
                    st.write(f"✅ LaTeX file created: {filled_tex}")

                    # Step 4: Compile to PDF
                    st.write("🔨 Compiling LaTeX to PDF...")
                    pdf_path = output_dir / "resume_filled.pdf"

                    result = subprocess.run(
                        ['lualatex', '-interaction=nonstopmode', '-output-directory', str(output_dir), str(filled_tex)],
                        capture_output=True,
                        text=True,
                        cwd=str(output_dir.parent)
                    )

                    if result.returncode != 0:
                        st.error("❌ LaTeX compilation failed. Check logs below.")
                        st.code(result.stdout[-1000:], language="text")
                        st.stop()

                    st.write(f"✅ PDF generated: {pdf_path}")

                    # Save PDF path to session state
                    st.session_state.current_pdf_path = str(pdf_path)

                    # Step 5: Save to organized folder structure with versioning
                    st.write("📁 Saving to organized output folder...")

                    from datetime import datetime
                    import shutil

                    # Clean company name for folder
                    safe_company = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in company_name)
                    safe_company = safe_company.replace(' ', '-')

                    # Create company folder: output_base_path/CompanyName/
                    company_dir = Path(output_base_path) / safe_company
                    company_dir.mkdir(parents=True, exist_ok=True)

                    # Find next version number by checking existing files
                    version = 1
                    while (company_dir / f"{safe_company}_{version}.pdf").exists():
                        version += 1

                    # Save PDF with version number
                    versioned_pdf = company_dir / f"{safe_company}_{version}.pdf"
                    shutil.copy(pdf_path, versioned_pdf)
                    st.write(f"✅ PDF saved: {versioned_pdf}")

                    # Save Job Description (only once, not versioned)
                    job_desc_file = company_dir / f"{safe_company}-JobDescription.txt"
                    if not job_desc_file.exists():
                        with open(job_desc_file, 'w', encoding='utf-8') as f:
                            f.write(job_description)
                        st.write(f"✅ Job description saved: {job_desc_file}")

                    # Save trimmed JSON with version number
                    versioned_json = company_dir / f"{safe_company}_{version}-Json.json"
                    with open(versioned_json, 'w', encoding='utf-8') as f:
                        json.dump(trimmed_data, f, indent=2)
                    st.write(f"✅ JSON saved: {versioned_json}")

                    organized_path = versioned_pdf
                    st.session_state.latest_saved_version = version
                    st.session_state.company_output_dir = str(company_dir)

                    # Track application in stats
                    from stats_page import add_application
                    add_application(company_name, job_description)
                    st.write("✅ Application tracked in stats")

                    # Update status
                    status.update(label="✅ Resume Generated Successfully!", state="complete", expanded=False)

            # Automatically redirect to edit & regenerate page
            st.session_state.current_page = 'edit_regenerate'
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)