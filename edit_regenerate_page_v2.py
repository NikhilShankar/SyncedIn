import streamlit as st
import json
import subprocess
import base64
from pathlib import Path
from fill_latex_template_v2 import fill_latex_template


def show():
    """Edit & Regenerate Resume Page - Enhanced with three-part UI"""

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

    # Load full resume data for reference
    resume_data_path = "resume_data_enhanced.json"
    try:
        with open(resume_data_path, 'r', encoding='utf-8') as f:
            full_resume_data = json.load(f)
    except FileNotFoundError:
        st.error(f"❌ Could not find {resume_data_path}")
        st.stop()

    # Get data from session state
    data = st.session_state.trimmed_data.copy()
    template_path = st.session_state.get('template_path', 'resume_template.tex')
    company_output_dir = st.session_state.get('company_output_dir', './output')
    current_version = st.session_state.get('latest_saved_version', 1)

    # Create two columns: Left (Editor) and Right (PDF Preview)
    col_edit, col_preview = st.columns([1, 1])

    with col_edit:
        st.markdown("### 📝 Edit Resume Content")
        st.markdown("Select content from your full resume or add custom content:")

        # --- SECTION 1: Professional Summary ---
        st.markdown("---")
        st.markdown("#### 📋 Professional Summary")

        # Get current summary from trimmed data
        current_summaries = data.get('summaries', {})
        current_summary_text = ""
        current_summary_type = None

        if current_summaries:
            # Get the first summary (the one currently selected)
            current_summary_type = list(current_summaries.keys())[0]
            current_summary_text = current_summaries[current_summary_type]

        # Available summaries from full data (that are NOT currently selected)
        full_summaries = full_resume_data.get('summaries', {})
        available_summaries = {k: v for k, v in full_summaries.items() if k != current_summary_type}

        # Show current summary
        if current_summary_text:
            st.markdown("**Currently Selected:**")
            col_sum, col_remove = st.columns([10, 1])
            with col_sum:
                st.info(f"**{current_summary_type.title()}:** {current_summary_text[:150]}...")
            with col_remove:
                if st.button("❌", key="remove_current_summary"):
                    data['summaries'] = {}
                    st.rerun()

        # Show available summaries from original JSON
        if available_summaries:
            st.markdown("**Available from Original Resume:**")
            for sum_type, sum_text in available_summaries.items():
                col_sum_avail, col_add = st.columns([10, 1])
                with col_sum_avail:
                    st.text_area(
                        f"{sum_type.title()} Summary",
                        value=sum_text,
                        height=100,
                        key=f"available_summary_{sum_type}",
                        disabled=True
                    )
                with col_add:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("➕", key=f"add_summary_{sum_type}"):
                        data['summaries'] = {sum_type: sum_text}
                        st.rerun()

        # Custom summary input
        st.markdown("**Or Write Custom Summary:**")
        custom_summary = st.text_area(
            "Custom Professional Summary",
            value="",
            height=150,
            key="custom_summary",
            placeholder="Write your own professional summary here..."
        )
        if st.button("✅ Use Custom Summary"):
            if custom_summary.strip():
                data['summaries'] = {'custom': custom_summary.strip()}
                st.rerun()
            else:
                st.warning("Please enter a summary first")

        # Allow editing current summary
        if current_summary_text:
            st.markdown("**Edit Current Summary:**")
            edited_summary = st.text_area(
                "Edit Summary",
                value=current_summary_text,
                height=150,
                key="edit_current_summary"
            )
            if edited_summary != current_summary_text:
                data['summaries'][current_summary_type] = edited_summary

        # --- SECTION 2: Professional Experience ---
        st.markdown("---")
        st.markdown("#### 💼 Professional Experience")

        # Get current companies
        current_companies = data.get('companies', [])
        current_company_ids = {c.get('id') for c in current_companies}

        # Get available companies from full data
        full_companies = full_resume_data.get('companies', [])
        available_companies = [c for c in full_companies if c.get('id') not in current_company_ids]

        # Show currently selected companies (editable)
        if current_companies:
            st.markdown("**Currently Selected Companies:**")
            companies_to_delete = []

            for comp_idx, company in enumerate(current_companies):
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
                    if st.button(f"➕ Add Custom Bullet Point", key=f"add_bullet_{comp_idx}"):
                        bullets.append({"text": "New bullet point - edit me!", "mandatory": False})
                        st.rerun()

                    # Delete company button
                    if st.button(f"🗑️ Remove Company", key=f"delete_comp_{comp_idx}"):
                        companies_to_delete.append(comp_idx)

            # Remove deleted companies
            for idx in sorted(companies_to_delete, reverse=True):
                current_companies.pop(idx)
                st.rerun()

        # Show available companies from original JSON
        if available_companies:
            st.markdown("**Available Companies from Original Resume:**")
            for avail_comp in available_companies:
                col_comp, col_add = st.columns([10, 1])
                with col_comp:
                    bullets_preview = "\n".join([f"• {b.get('text', '')[:100]}..." for b in avail_comp.get('bullets', [])[:3]])
                    st.text_area(
                        f"{avail_comp.get('name')} - {avail_comp.get('position')}",
                        value=f"Dates: {avail_comp.get('dates')}\nLocation: {avail_comp.get('location')}\n\n{bullets_preview}",
                        height=150,
                        key=f"available_comp_{avail_comp.get('id')}",
                        disabled=True
                    )
                with col_add:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if st.button("➕", key=f"add_comp_{avail_comp.get('id')}"):
                        current_companies.append(avail_comp)
                        st.rerun()

        # --- SECTION 3: Technical Skills ---
        st.markdown("---")
        st.markdown("#### 🛠️ Technical Skills")

        skills = data.get('skills', {})
        full_skills = full_resume_data.get('skills', {})
        skill_categories = ['languages', 'platforms', 'skills', 'frameworks', 'tools', 'database']

        for category in skill_categories:
            st.markdown(f"**{category.title()}:**")

            current_skills = skills.get(category, [])
            full_category_skills = full_skills.get(category, [])
            available_skills = [s for s in full_category_skills if s not in current_skills]

            # Current skills (editable)
            col_curr, col_custom = st.columns(2)
            with col_curr:
                st.markdown("*Currently Selected:*")
                skills_text = st.text_input(
                    f"Current {category}",
                    value=", ".join(current_skills),
                    key=f"edit_skills_{category}",
                    label_visibility="collapsed"
                )
                skills[category] = [s.strip() for s in skills_text.split(',') if s.strip()]

            # Custom skills
            with col_custom:
                st.markdown("*Add Custom:*")
                custom_skills = st.text_input(
                    f"Custom {category}",
                    value="",
                    key=f"custom_skills_{category}",
                    placeholder="Add new skills (comma-separated)",
                    label_visibility="collapsed"
                )
                if st.button(f"➕ Add", key=f"add_custom_skills_{category}"):
                    if custom_skills.strip():
                        new_skills = [s.strip() for s in custom_skills.split(',') if s.strip()]
                        skills[category] = list(set(skills[category] + new_skills))
                        st.rerun()

            # Available skills from original
            if available_skills:
                with st.expander(f"Available {category.title()} from Original Resume"):
                    for skill in available_skills:
                        col_skill, col_add_skill = st.columns([10, 1])
                        with col_skill:
                            st.text(skill)
                        with col_add_skill:
                            if st.button("➕", key=f"add_skill_{category}_{skill}"):
                                skills[category].append(skill)
                                st.rerun()

        # --- SECTION 4: Education ---
        st.markdown("---")
        st.markdown("#### 🎓 Education")

        current_education = data.get('education', [])
        full_education = full_resume_data.get('education', [])

        # Helper to check if education is in current list
        def is_education_in_list(edu, edu_list):
            for e in edu_list:
                if (e.get('degree') == edu.get('degree') and
                    e.get('institution') == edu.get('institution')):
                    return True
            return False

        available_education = [e for e in full_education if not is_education_in_list(e, current_education)]

        # Current education (editable)
        if current_education:
            st.markdown("**Currently Selected:**")
            education_to_delete = []

            for edu_idx, edu in enumerate(current_education):
                with st.expander(f"**{edu.get('degree', 'Unknown')}** at {edu.get('institution', 'Unknown')}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        edu['degree'] = st.text_input("Degree", value=edu.get('degree', ''), key=f"edu_degree_{edu_idx}")
                        edu['course'] = st.text_input("Course/Major", value=edu.get('course', ''), key=f"edu_course_{edu_idx}")
                        edu['institution'] = st.text_input("Institution", value=edu.get('institution', ''), key=f"edu_inst_{edu_idx}")
                    with col2:
                        edu['dates'] = st.text_input("Dates", value=edu.get('dates', ''), key=f"edu_dates_{edu_idx}")
                        edu['location'] = st.text_input("Location", value=edu.get('location', ''), key=f"edu_loc_{edu_idx}")

                    if st.button(f"🗑️ Remove", key=f"delete_edu_{edu_idx}"):
                        education_to_delete.append(edu_idx)

            # Remove deleted education
            for idx in sorted(education_to_delete, reverse=True):
                current_education.pop(idx)
                st.rerun()

        # Available education from original
        if available_education:
            st.markdown("**Available from Original Resume:**")
            for avail_edu in available_education:
                col_edu, col_add = st.columns([10, 1])
                with col_edu:
                    st.text_area(
                        f"{avail_edu.get('degree')}",
                        value=f"{avail_edu.get('course')}\n{avail_edu.get('institution')}\n{avail_edu.get('dates')} | {avail_edu.get('location')}",
                        height=100,
                        key=f"available_edu_{avail_edu.get('degree')}",
                        disabled=True
                    )
                with col_add:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("➕", key=f"add_edu_{avail_edu.get('degree')}"):
                        current_education.append(avail_edu)
                        st.rerun()

        # --- SECTION 5: Personal Projects ---
        st.markdown("---")
        st.markdown("#### 🚀 Personal Projects")

        current_projects = data.get('projects', [])
        current_project_ids = {p.get('id') for p in current_projects}

        full_projects = full_resume_data.get('projects', [])
        available_projects = [p for p in full_projects if p.get('id') not in current_project_ids]

        # Current projects (editable)
        if current_projects:
            st.markdown("**Currently Selected:**")
            projects_to_delete = []

            for proj_idx, project in enumerate(current_projects):
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

                    if st.button(f"🗑️ Remove", key=f"delete_proj_{proj_idx}"):
                        projects_to_delete.append(proj_idx)

            # Remove deleted projects
            for idx in sorted(projects_to_delete, reverse=True):
                current_projects.pop(idx)
                st.rerun()

        # Available projects from original
        if available_projects:
            st.markdown("**Available from Original Resume:**")
            for avail_proj in available_projects:
                col_proj, col_add = st.columns([10, 1])
                with col_proj:
                    st.text_area(
                        f"{avail_proj.get('name')}",
                        value=f"Tech: {avail_proj.get('tech')}\nDate: {avail_proj.get('date')}\n\n{avail_proj.get('description', '')[:150]}...",
                        height=150,
                        key=f"available_proj_{avail_proj.get('id')}",
                        disabled=True
                    )
                with col_add:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if st.button("➕", key=f"add_proj_{avail_proj.get('id')}"):
                        current_projects.append(avail_proj)
                        st.rerun()

        # Add new custom project
        st.markdown("**Add Custom Project:**")
        if st.button("➕ Add New Custom Project"):
            current_projects.append({
                "id": f"custom_project_{len(current_projects) + 1}",
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
