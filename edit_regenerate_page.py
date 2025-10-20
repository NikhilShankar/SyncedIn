import streamlit as st
import json
import subprocess
import base64
from pathlib import Path
from fill_latex_template_v2 import fill_latex_template


def show():
    """Edit & Regenerate Resume Page - Enhanced with chip-based UI"""

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

    template_path = st.session_state.get('template_path', 'resume_template.tex')
    company_output_dir = st.session_state.get('company_output_dir', './output')
    current_version = st.session_state.get('latest_saved_version', 1)

    # --- PDF PREVIEW AT TOP ---
    st.markdown("---")
    st.markdown("### 📄 PDF Preview")

    current_pdf_path = st.session_state.get('current_pdf_path')
    if current_pdf_path and Path(current_pdf_path).exists():
        # Display PDF in full width
        with open(current_pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

        # Smaller preview height since it's at top
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
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
        st.info("⚠️ No PDF available. Make changes below and click 'Generate New PDF'")

    st.markdown("---")
    st.markdown("### 📝 Edit Resume Content")
    st.markdown("**Click on chips to select/unselect content. Selected items are highlighted in blue.**")

    # Working directly with session state
    data = st.session_state.trimmed_data

    # --- SECTION 1: Professional Summary ---
    st.markdown("---")
    st.markdown("#### 📋 Professional Summary")

    # Get current summary
    current_summaries = data.get('summaries', {})
    current_summary_type = list(current_summaries.keys())[0] if current_summaries else None
    current_summary_text = current_summaries.get(current_summary_type, '') if current_summary_type else ''

    # Get all summary types from full data
    full_summaries = full_resume_data.get('summaries', {})
    summary_types = list(full_summaries.keys())

    # Render summary chips
    st.markdown("**Select Summary Type:**")
    cols = st.columns(len(summary_types))

    for idx, sum_type in enumerate(summary_types):
        with cols[idx]:
            is_selected = (sum_type == current_summary_type)
            button_type = "primary" if is_selected else "secondary"
            label = f"✓ {sum_type.title()}" if is_selected else sum_type.title()

            if st.button(label, key=f"summary_{sum_type}", type=button_type, use_container_width=True):
                # Replace with new summary from full data
                st.session_state.trimmed_data['summaries'] = {sum_type: full_summaries[sum_type]}
                st.rerun()

    # Editable summary text area - user can edit any selected summary
    if current_summary_type and current_summary_text:
        st.markdown("**Edit Selected Summary:**")
        edited_summary = st.text_area(
            f"Editing: {current_summary_type.title()} Summary",
            value=current_summary_text,
            height=150,
            key="editable_summary"
        )

        # Update the summary in session state if it changed
        if edited_summary != current_summary_text:
            st.session_state.trimmed_data['summaries'][current_summary_type] = edited_summary

    # --- SECTION 2: Technical Skills ---
    st.markdown("---")
    st.markdown("#### 🛠️ Technical Skills")

    skills = data.get('skills', {})
    full_skills = full_resume_data.get('skills', {})
    skill_categories = ['languages', 'platforms', 'skills', 'frameworks', 'tools', 'database']

    for category in skill_categories:
        st.markdown(f"**{category.title()}:**")

        current_skills = skills.get(category, [])
        full_category_skills = full_skills.get(category, [])

        # Combine and deduplicate
        all_skills = []
        seen = set()

        # Add selected first
        for skill in current_skills:
            if skill not in seen:
                all_skills.append(skill)
                seen.add(skill)

        # Add unselected
        for skill in full_category_skills:
            if skill not in seen:
                all_skills.append(skill)
                seen.add(skill)

        # Render chips in rows of 6
        num_cols = 6
        for i in range(0, len(all_skills), num_cols):
            cols = st.columns(num_cols)
            for j, skill in enumerate(all_skills[i:i+num_cols]):
                with cols[j]:
                    is_selected = skill in current_skills
                    button_type = "primary" if is_selected else "secondary"
                    label = f"✓ {skill}" if is_selected else skill

                    if st.button(label, key=f"skill_{category}_{i}_{j}_{skill.replace(' ', '_')[:20]}",
                               type=button_type, use_container_width=True):
                        # Toggle selection
                        if is_selected:
                            st.session_state.trimmed_data['skills'][category].remove(skill)
                        else:
                            if category not in st.session_state.trimmed_data['skills']:
                                st.session_state.trimmed_data['skills'][category] = []
                            st.session_state.trimmed_data['skills'][category].append(skill)
                        st.rerun()

        # Custom skills button
        if st.button(f"✏️ Add Custom {category.title()}", key=f"custom_{category}_btn"):
            st.session_state[f'show_custom_{category}'] = True

        if st.session_state.get(f'show_custom_{category}', False):
            custom_input = st.text_input(
                f"Add custom {category} (comma-separated)",
                key=f"custom_{category}_input",
                placeholder="e.g., React, Vue.js, Angular"
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Add", key=f"save_custom_{category}"):
                    if custom_input.strip():
                        new_items = [s.strip() for s in custom_input.split(',') if s.strip()]
                        if category not in st.session_state.trimmed_data['skills']:
                            st.session_state.trimmed_data['skills'][category] = []
                        st.session_state.trimmed_data['skills'][category].extend(new_items)
                        st.session_state.trimmed_data['skills'][category] = list(set(st.session_state.trimmed_data['skills'][category]))
                        st.session_state[f'show_custom_{category}'] = False
                        st.rerun()
            with col2:
                if st.button("❌ Cancel", key=f"cancel_custom_{category}"):
                    st.session_state[f'show_custom_{category}'] = False
                    st.rerun()

    # --- SECTION 3: Professional Experience ---
    st.markdown("---")
    st.markdown("#### 💼 Professional Experience")

    current_companies = data.get('companies', [])
    current_company_ids = {c.get('id') for c in current_companies}
    full_companies = full_resume_data.get('companies', [])

    # Show all companies as chips
    st.markdown("**Select Companies:**")

    num_cols = 4
    for i in range(0, len(full_companies), num_cols):
        cols = st.columns(num_cols)
        for j, company in enumerate(full_companies[i:i+num_cols]):
            with cols[j]:
                comp_id = company.get('id')
                is_selected = comp_id in current_company_ids
                button_type = "primary" if is_selected else "secondary"
                label = f"✓ {comp_id}" if is_selected else comp_id

                if st.button(label, key=f"company_{i}_{j}_{comp_id}",
                           type=button_type, use_container_width=True):
                    # Toggle company selection
                    if is_selected:
                        st.session_state.trimmed_data['companies'] = [
                            c for c in st.session_state.trimmed_data['companies']
                            if c.get('id') != comp_id
                        ]
                    else:
                        st.session_state.trimmed_data['companies'].append(company)
                    st.rerun()

    # Edit selected companies
    if current_companies:
        st.markdown("**Edit Selected Companies:**")
        companies_to_remove = []

        for comp_idx, company in enumerate(current_companies):
            with st.expander(f"**{company.get('name', 'Unknown')}** - {company.get('position', 'Unknown')}", expanded=False):
                # Edit company details
                col1, col2 = st.columns(2)
                with col1:
                    company['name'] = st.text_input("Company Name", value=company.get('name', ''), key=f"comp_name_{comp_idx}")
                    company['position'] = st.text_input("Position", value=company.get('position', ''), key=f"comp_pos_{comp_idx}")
                with col2:
                    company['dates'] = st.text_input("Dates", value=company.get('dates', ''), key=f"comp_dates_{comp_idx}")
                    company['location'] = st.text_input("Location", value=company.get('location', ''), key=f"comp_loc_{comp_idx}")

                # Get bullets from full data for this company
                full_company = next((c for c in full_companies if c.get('id') == company.get('id')), None)
                full_bullets = [b.get('text') for b in full_company.get('bullets', [])] if full_company else []
                current_bullets = [b.get('text') for b in company.get('bullets', [])]

                # Combine all bullets
                all_bullets = []
                seen_bullets = set()
                for b in current_bullets:
                    if b not in seen_bullets:
                        all_bullets.append(b)
                        seen_bullets.add(b)
                for b in full_bullets:
                    if b not in seen_bullets:
                        all_bullets.append(b)
                        seen_bullets.add(b)

                st.markdown("**Select Bullet Points:**")
                for bullet_idx, bullet_text in enumerate(all_bullets):
                    col_bullet, col_select = st.columns([9, 1])
                    with col_bullet:
                        # Show truncated bullet
                        display_text = bullet_text[:100] + "..." if len(bullet_text) > 100 else bullet_text
                        st.text(display_text)
                    with col_select:
                        is_selected = bullet_text in current_bullets
                        if is_selected:
                            if st.button("✓", key=f"bullet_{comp_idx}_{bullet_idx}", type="primary"):
                                # Remove bullet
                                st.session_state.trimmed_data['companies'][comp_idx]['bullets'] = [
                                    b for b in company['bullets'] if b.get('text') != bullet_text
                                ]
                                st.rerun()
                        else:
                            if st.button("○", key=f"bullet_{comp_idx}_{bullet_idx}"):
                                # Add bullet
                                st.session_state.trimmed_data['companies'][comp_idx]['bullets'].append(
                                    {'text': bullet_text, 'mandatory': False}
                                )
                                st.rerun()

                # Custom bullet button
                if st.button(f"✏️ Add Custom Bullet", key=f"custom_bullet_btn_{comp_idx}"):
                    st.session_state[f'show_custom_bullet_{comp_idx}'] = True

                if st.session_state.get(f'show_custom_bullet_{comp_idx}', False):
                    custom_bullet = st.text_area(
                        "Custom Bullet Point",
                        key=f"custom_bullet_input_{comp_idx}",
                        height=100
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Add Bullet", key=f"save_custom_bullet_{comp_idx}"):
                            if custom_bullet.strip():
                                st.session_state.trimmed_data['companies'][comp_idx]['bullets'].append(
                                    {'text': custom_bullet.strip(), 'mandatory': False}
                                )
                                st.session_state[f'show_custom_bullet_{comp_idx}'] = False
                                st.rerun()
                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_custom_bullet_{comp_idx}"):
                            st.session_state[f'show_custom_bullet_{comp_idx}'] = False
                            st.rerun()

    # Custom company button
    if st.button("✏️ Add Custom Company", key="custom_company_btn"):
        st.session_state.show_custom_company = True

    if st.session_state.get('show_custom_company', False):
        st.markdown("**Add New Company:**")
        col1, col2 = st.columns(2)
        with col1:
            new_comp_name = st.text_input("Company Name", key="new_comp_name")
            new_comp_position = st.text_input("Position", key="new_comp_position")
        with col2:
            new_comp_dates = st.text_input("Dates", key="new_comp_dates")
            new_comp_location = st.text_input("Location", key="new_comp_location")

        new_comp_bullets = st.text_area(
            "Bullet Points (one per line)",
            key="new_comp_bullets",
            height=150
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Add Company", key="save_custom_company"):
                if new_comp_name.strip():
                    bullets = [{'text': b.strip(), 'mandatory': False}
                              for b in new_comp_bullets.split('\n') if b.strip()]
                    new_company = {
                        'id': f"custom_comp_{len(data['companies'])}",
                        'name': new_comp_name.strip(),
                        'position': new_comp_position.strip(),
                        'dates': new_comp_dates.strip(),
                        'location': new_comp_location.strip(),
                        'bullets': bullets,
                        'mandatory': False
                    }
                    st.session_state.trimmed_data['companies'].append(new_company)
                    st.session_state.show_custom_company = False
                    st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_custom_company"):
                st.session_state.show_custom_company = False
                st.rerun()

    # --- SECTION 4: Personal Projects ---
    st.markdown("---")
    st.markdown("#### 🚀 Personal Projects")

    current_projects = data.get('projects', [])
    current_project_ids = {p.get('id') for p in current_projects}
    full_projects = full_resume_data.get('projects', [])

    # Show all projects as chips
    st.markdown("**Select Projects:**")

    num_cols = 4
    for i in range(0, len(full_projects), num_cols):
        cols = st.columns(num_cols)
        for j, project in enumerate(full_projects[i:i+num_cols]):
            with cols[j]:
                proj_id = project.get('id')
                is_selected = proj_id in current_project_ids
                button_type = "primary" if is_selected else "secondary"
                label = f"✓ {proj_id}" if is_selected else proj_id

                if st.button(label, key=f"project_{i}_{j}_{proj_id}",
                           type=button_type, use_container_width=True):
                    # Toggle project selection
                    if is_selected:
                        st.session_state.trimmed_data['projects'] = [
                            p for p in st.session_state.trimmed_data['projects']
                            if p.get('id') != proj_id
                        ]
                    else:
                        st.session_state.trimmed_data['projects'].append(project)
                    st.rerun()

    # Edit selected projects
    if current_projects:
        st.markdown("**Edit Selected Projects:**")
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

    # Custom project button
    if st.button("✏️ Add Custom Project", key="custom_project_btn"):
        st.session_state.show_custom_project = True

    if st.session_state.get('show_custom_project', False):
        st.markdown("**Add New Project:**")
        col1, col2 = st.columns(2)
        with col1:
            new_proj_name = st.text_input("Project Name", key="new_proj_name")
            new_proj_tech = st.text_input("Technologies", key="new_proj_tech")
        with col2:
            new_proj_date = st.text_input("Date", key="new_proj_date")
            new_proj_link = st.text_input("Link (optional)", key="new_proj_link")

        new_proj_desc = st.text_area(
            "Description",
            key="new_proj_desc",
            height=100
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Add Project", key="save_custom_project"):
                if new_proj_name.strip():
                    new_project = {
                        'id': f"custom_proj_{len(data['projects'])}",
                        'name': new_proj_name.strip(),
                        'tech': new_proj_tech.strip(),
                        'description': new_proj_desc.strip(),
                        'date': new_proj_date.strip(),
                        'link': new_proj_link.strip(),
                        'mandatory': False
                    }
                    st.session_state.trimmed_data['projects'].append(new_project)
                    st.session_state.show_custom_project = False
                    st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_custom_project"):
                st.session_state.show_custom_project = False
                st.rerun()

    # --- SECTION 5: Education ---
    st.markdown("---")
    st.markdown("#### 🎓 Education")

    current_education = data.get('education', [])
    full_education = full_resume_data.get('education', [])

    # Create identifiers for education
    def education_id(edu):
        return f"{edu.get('degree', '')}_{edu.get('institution', '')}"

    current_edu_ids = {education_id(e) for e in current_education}

    st.markdown("**Select Education:**")

    num_cols = 3
    for i in range(0, len(full_education), num_cols):
        cols = st.columns(num_cols)
        for j, edu in enumerate(full_education[i:i+num_cols]):
            with cols[j]:
                edu_id = education_id(edu)
                is_selected = edu_id in current_edu_ids
                button_type = "primary" if is_selected else "secondary"
                label = f"✓ {edu_id}" if is_selected else edu_id

                if st.button(label, key=f"education_{i}_{j}_{edu_id[:20]}",
                           type=button_type, use_container_width=True):
                    # Toggle education selection
                    if is_selected:
                        st.session_state.trimmed_data['education'] = [
                            e for e in st.session_state.trimmed_data['education']
                            if education_id(e) != edu_id
                        ]
                    else:
                        st.session_state.trimmed_data['education'].append(edu)
                    st.rerun()

    # Edit selected education
    if current_education:
        st.markdown("**Edit Selected Education:**")
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

    # Custom education button
    if st.button("✏️ Add Custom Education", key="custom_education_btn"):
        st.session_state.show_custom_education = True

    if st.session_state.get('show_custom_education', False):
        st.markdown("**Add New Education:**")
        col1, col2 = st.columns(2)
        with col1:
            new_edu_degree = st.text_input("Degree", key="new_edu_degree")
            new_edu_course = st.text_input("Course/Major", key="new_edu_course")
            new_edu_institution = st.text_input("Institution", key="new_edu_institution")
        with col2:
            new_edu_dates = st.text_input("Dates", key="new_edu_dates")
            new_edu_location = st.text_input("Location", key="new_edu_location")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Add Education", key="save_custom_education"):
                if new_edu_degree.strip():
                    new_edu = {
                        'degree': new_edu_degree.strip(),
                        'course': new_edu_course.strip(),
                        'institution': new_edu_institution.strip(),
                        'dates': new_edu_dates.strip(),
                        'location': new_edu_location.strip()
                    }
                    st.session_state.trimmed_data['education'].append(new_edu)
                    st.session_state.show_custom_education = False
                    st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_custom_education"):
                st.session_state.show_custom_education = False
                st.rerun()

    # --- GENERATE BUTTON ---
    st.markdown("---")
    if st.button("🔄 Generate New PDF", type="primary", use_container_width=True):
        # Generate PDF
        with st.spinner("Generating PDF..."):
            try:
                # Create output directory
                output_dir = Path("./generated")
                output_dir.mkdir(exist_ok=True)

                # Fill LaTeX template
                filled_tex = output_dir / "resume_filled.tex"
                fill_latex_template(
                    str(template_path),
                    st.session_state.trimmed_data,
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
                    json.dump(st.session_state.trimmed_data, f, indent=2)

                # Update session state
                st.session_state.current_pdf_path = str(pdf_path)
                st.session_state.latest_saved_version = version

                st.success(f"✅ PDF regenerated and saved as version {version}!")
                st.info(f"📂 Saved to: `{versioned_pdf}`")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
