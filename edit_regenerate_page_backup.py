import streamlit as st
import json
import subprocess
import base64
from pathlib import Path
from fill_latex_template_v2 import fill_latex_template


def show():
    """Edit & Regenerate Resume Page - Vertical layout with PDF preview"""

    # Check if we have the required data in session state
    if 'trimmed_data' not in st.session_state or not st.session_state.trimmed_data:
        st.warning("⚠️ No resume data available. Please generate a resume first.")
        if st.button("← Go to Generate Page"):
            st.session_state.current_page = 'generate'
            st.rerun()
        st.stop()

    # Title
    st.markdown("<h1 class='main-header'>✏️ Edit & Regenerate Resume</h1>", unsafe_allow_html=True)
    company_name = st.session_state.get('company_name', 'Unknown Company')
    st.markdown(f"**Company:** {company_name}")

    # Get data from session state
    data = st.session_state.trimmed_data.copy()
    template_path = st.session_state.get('template_path', 'resume_template.tex')
    company_output_dir = st.session_state.get('company_output_dir', './output')
    current_version = st.session_state.get('latest_saved_version', 1)

    # Create two columns: Left (Editor) and Right (PDF Preview)
    col_edit, col_preview = st.columns([1, 1])

    with col_edit:
        st.markdown("### 📝 Edit Resume Content")
        st.markdown("Edit the content below in the exact order it appears in your resume:")

        # --- SECTION 1: Professional Summary ---
        st.markdown("---")
        st.markdown("#### 📋 Professional Summary")
        summary_text = st.text_area(
            "Summary",
            value=data.get('summary', ''),
            height=150,
            key="edit_summary",
            label_visibility="collapsed"
        )
        data['summary'] = summary_text

        # --- SECTION 2: Professional Experience ---
        st.markdown("---")
        st.markdown("#### 💼 Professional Experience")

        companies = data.get('companies', [])
        companies_to_delete = []

        for comp_idx, company in enumerate(companies):
            with st.expander(f"**{company.get('name', 'Unknown')}** - {company.get('position', 'Unknown')}", expanded=False):
                # Company metadata
                col1, col2 = st.columns(2)
                with col1:
                    company['name'] = st.text_input("Company Name", value=company.get('name', ''), key=f"comp_name_{comp_idx}")
                    company['position'] = st.text_input("Position", value=company.get('position', ''), key=f"comp_pos_{comp_idx}")
                with col2:
                    company['dates'] = st.text_input("Dates", value=company.get('dates', ''), key=f"comp_dates_{comp_idx}")
                    company['location'] = st.text_input("Location", value=company.get('location', ''), key=f"comp_loc_{comp_idx}")

                # Bullet points
                st.markdown("**Bullet Points:**")
                bullets = company.get('bullets', [])
                bullets_to_delete = []

                for bullet_idx, bullet in enumerate(bullets):
                    col_bullet, col_delete = st.columns([8, 1])
                    with col_bullet:
                        new_text = st.text_area(
                            f"Bullet {bullet_idx + 1}",
                            value=bullet.get('text', ''),
                            height=80,
                            key=f"bullet_{comp_idx}_{bullet_idx}",
                            label_visibility="collapsed"
                        )
                        bullet['text'] = new_text
                    with col_delete:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("❌", key=f"delete_bullet_{comp_idx}_{bullet_idx}"):
                            bullets_to_delete.append(bullet_idx)

                # Remove deleted bullets
                for idx in sorted(bullets_to_delete, reverse=True):
                    bullets.pop(idx)
                    st.rerun()

                # Add new bullet
                if st.button(f"➕ Add Bullet Point", key=f"add_bullet_{comp_idx}"):
                    bullets.append({"text": "New bullet point - edit me!", "mandatory": False})
                    st.rerun()

                # Delete company button
                if st.button(f"🗑️ Delete Company: {company.get('name')}", key=f"delete_comp_{comp_idx}"):
                    companies_to_delete.append(comp_idx)

        # Remove deleted companies
        for idx in sorted(companies_to_delete, reverse=True):
            companies.pop(idx)
            st.rerun()

        # --- SECTION 3: Technical Skills ---
        st.markdown("---")
        st.markdown("#### 🛠️ Technical Skills")

        skills = data.get('skills', {})
        skill_categories = ['languages', 'platforms', 'skills', 'frameworks', 'tools', 'database']

        for category in skill_categories:
            current_skills = skills.get(category, [])
            skills_text = st.text_input(
                f"{category.title()} (comma-separated)",
                value=", ".join(current_skills),
                key=f"edit_skills_{category}"
            )
            skills[category] = [s.strip() for s in skills_text.split(',') if s.strip()]

        # --- SECTION 4: Education ---
        st.markdown("---")
        st.markdown("#### 🎓 Education")

        education = data.get('education', [])
        education_to_delete = []

        for edu_idx, edu in enumerate(education):
            with st.expander(f"**{edu.get('degree', 'Unknown')}** at {edu.get('institution', 'Unknown')}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    edu['degree'] = st.text_input("Degree", value=edu.get('degree', ''), key=f"edu_degree_{edu_idx}")
                    edu['course'] = st.text_input("Course/Major", value=edu.get('course', ''), key=f"edu_course_{edu_idx}")
                    edu['institution'] = st.text_input("Institution", value=edu.get('institution', ''), key=f"edu_inst_{edu_idx}")
                with col2:
                    edu['dates'] = st.text_input("Dates", value=edu.get('dates', ''), key=f"edu_dates_{edu_idx}")
                    edu['location'] = st.text_input("Location", value=edu.get('location', ''), key=f"edu_loc_{edu_idx}")

                if st.button(f"🗑️ Delete Education", key=f"delete_edu_{edu_idx}"):
                    education_to_delete.append(edu_idx)

        # Remove deleted education
        for idx in sorted(education_to_delete, reverse=True):
            education.pop(idx)
            st.rerun()

        # --- SECTION 5: Personal Projects ---
        st.markdown("---")
        st.markdown("#### 🚀 Personal Projects")

        projects = data.get('projects', [])
        projects_to_delete = []

        for proj_idx, project in enumerate(projects):
            with st.expander(f"**{project.get('name', 'Unknown')}**", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    project['name'] = st.text_input("Project Name", value=project.get('name', ''), key=f"proj_name_{proj_idx}")
                    project['tech'] = st.text_input("Technologies", value=project.get('tech', ''), key=f"proj_tech_{proj_idx}")
                with col2:
                    project['date'] = st.text_input("Date", value=project.get('date', ''), key=f"proj_date_{proj_idx}")
                    project['link'] = st.text_input("Link", value=project.get('link', ''), key=f"proj_link_{proj_idx}")

                project['description'] = st.text_area(
                    "Description",
                    value=project.get('description', ''),
                    height=100,
                    key=f"proj_desc_{proj_idx}"
                )

                if st.button(f"🗑️ Delete Project", key=f"delete_proj_{proj_idx}"):
                    projects_to_delete.append(proj_idx)

        # Remove deleted projects
        for idx in sorted(projects_to_delete, reverse=True):
            projects.pop(idx)
            st.rerun()

        # Add new project
        if st.button("➕ Add New Project"):
            projects.append({
                "id": f"project_{len(projects) + 1}",
                "mandatory": False,
                "name": "New Project",
                "tech": "Technologies",
                "description": "Project description",
                "date": "Month Year",
                "link": ""
            })
            st.rerun()

        # --- GENERATE BUTTON ---
        st.markdown("---")
        if st.button("🔄 Generate New PDF", type="primary", use_container_width=True):
            # Save updated data to session state
            st.session_state.trimmed_data = data

            # Generate PDF without calling LLM
            with st.spinner("Generating PDF..."):
                try:
                    # Create output directory
                    output_dir = Path("./generated")
                    output_dir.mkdir(exist_ok=True)

                    # Fill LaTeX template
                    filled_tex = output_dir / "resume_filled.tex"
                    fill_latex_template(
                        str(template_path),
                        data,
                        str(filled_tex)
                    )

                    # Compile to PDF
                    pdf_path = output_dir / "resume_filled.pdf"
                    result = subprocess.run(
                        ['lualatex', '-interaction=nonstopmode', '-output-directory', str(output_dir), str(filled_tex)],
                        capture_output=True,
                        text=True,
                        cwd=str(output_dir.parent)
                    )

                    if result.returncode != 0:
                        st.error("❌ LaTeX compilation failed")
                        st.code(result.stdout[-1000:], language="text")
                        st.stop()

                    # Save to company folder with incremented version
                    import shutil
                    safe_company = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in company_name)
                    safe_company = safe_company.replace(' ', '-')

                    company_dir = Path(company_output_dir)

                    # Find next version number
                    version = current_version + 1
                    while (company_dir / f"{safe_company}_{version}.pdf").exists():
                        version += 1

                    # Save versioned files
                    versioned_pdf = company_dir / f"{safe_company}_{version}.pdf"
                    shutil.copy(pdf_path, versioned_pdf)

                    versioned_json = company_dir / f"{safe_company}_{version}-Json.json"
                    with open(versioned_json, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)

                    # Update session state
                    st.session_state.current_pdf_path = str(pdf_path)
                    st.session_state.latest_saved_version = version

                    st.success(f"✅ PDF regenerated and saved as version {version}!")
                    st.info(f"📂 Saved to: `{versioned_pdf}`")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    with col_preview:
        st.markdown("### 📄 PDF Preview")

        # Check if PDF exists
        current_pdf_path = st.session_state.get('current_pdf_path')
        if current_pdf_path and Path(current_pdf_path).exists():
            # Display PDF
            with open(current_pdf_path, 'rb') as f:
                pdf_bytes = f.read()
                base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

            # Download button
            st.download_button(
                label="📥 Download Current PDF",
                data=pdf_bytes,
                file_name=f"resume_{company_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.warning("⚠️ No PDF available for preview")
