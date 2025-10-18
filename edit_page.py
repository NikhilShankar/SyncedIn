import streamlit as st
import json
import shutil
from pathlib import Path
from datetime import datetime


def show():
    """Edit Resume Data Page"""

    # Title
    st.markdown("<h1 class='main-header'>✏️ Edit Resume Data</h1>", unsafe_allow_html=True)
    st.markdown("Manage your resume data with an easy-to-use interface")

    # File paths
    resume_data_path = Path("resume_data_enhanced_default.json")
    default_backup_path = Path("resume_data_enhanced_DEFAULT.json")

    # Initialize session state
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = None
        st.session_state.data_loaded = False
        st.session_state.modified = False

    # Create default backup if it doesn't exist
    if not default_backup_path.exists() and resume_data_path.exists():
        shutil.copy(resume_data_path, default_backup_path)
        st.success("✅ Created default backup: resume_data_enhanced_DEFAULT.json")

    # Top action buttons
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

    with col1:
        if st.button("📂 Load Resume Data", use_container_width=True):
            try:
                with open(resume_data_path, 'r') as f:
                    st.session_state.resume_data = json.load(f)
                    st.session_state.data_loaded = True
                    st.session_state.modified = False
                st.success("✅ Resume data loaded successfully!")
                st.rerun()
            except FileNotFoundError:
                st.error(f"❌ File not found: {resume_data_path}")
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {e}")

    with col2:
        if st.button("💾 Save Changes", use_container_width=True, type="primary"):
            if st.session_state.resume_data:
                try:
                    # Create backup before saving
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = Path(f"./resume_backups/resume_data_enhanced_backup_{timestamp}.json")
                    shutil.copy(resume_data_path, backup_path)

                    # Save changes
                    with open(resume_data_path, 'w') as f:
                        json.dump(st.session_state.resume_data, f, indent=2)

                    st.success(f"✅ Saved! Backup created: {backup_path}")
                    st.session_state.modified = False
                except Exception as e:
                    st.error(f"❌ Error saving: {e}")
            else:
                st.warning("⚠️ No data to save. Load data first.")

    with col3:
        if st.button("↩️ Revert to Default", use_container_width=True):
            if default_backup_path.exists():
                try:
                    # Load default backup
                    with open(default_backup_path, 'r') as f:
                        st.session_state.resume_data = json.load(f)
                    st.success("✅ Reverted to default version!")
                    st.session_state.modified = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error reverting: {e}")
            else:
                st.error("❌ Default backup not found!")

    with col4:
        if st.button("🔄 Reload", use_container_width=True):
            if st.session_state.data_loaded:
                st.session_state.data_loaded = False
                st.session_state.resume_data = None
                st.session_state.modified = False
                st.rerun()

    # Show modification status
    if st.session_state.modified:
        st.warning("⚠️ You have unsaved changes!")

    st.markdown("---")

    # Only show editor if data is loaded
    if not st.session_state.data_loaded or not st.session_state.resume_data:
        st.info("👆 Click 'Load Resume Data' to start editing")
        st.stop()

    data = st.session_state.resume_data

    # Sidebar navigation for sections
    with st.sidebar:
        st.markdown("---")
        st.markdown("## 📑 Sections")
        section = st.radio(
            "Navigate to:",
            ["Static Info", "Summaries", "Companies", "Skills", "Projects", "Education", "Configuration"],
            label_visibility="collapsed"
        )

    # Section: Static Info
    if section == "Static Info":
        st.header("📋 Static Information")

        static = data.get('static_info', {})

        col1, col2 = st.columns(2)

        with col1:
            new_name = st.text_input("Full Name", value=static.get('name', ''))
            new_phone = st.text_input("Phone", value=static.get('phone', ''))
            new_email = st.text_input("Email", value=static.get('email', ''))

        with col2:
            new_address = st.text_input("Address", value=static.get('address', ''))
            new_linkedin = st.text_input("LinkedIn URL", value=static.get('linkedin', ''))
            new_portfolio = st.text_input("Portfolio URL", value=static.get('portfolio', ''))

        new_leetcode = st.text_input("LeetCode URL", value=static.get('leetcode', ''))

        # Update button
        if st.button("💾 Update Static Info", type="primary"):
            data['static_info'] = {
                'name': new_name,
                'address': new_address,
                'phone': new_phone,
                'email': new_email,
                'linkedin': new_linkedin,
                'portfolio': new_portfolio,
                'leetcode': new_leetcode
            }
            st.session_state.modified = True
            st.success("✅ Static info updated! Remember to save changes.")

    # Section: Summaries
    elif section == "Summaries":
        st.header("📝 Professional Summaries")
        st.markdown("Edit your professional summaries for different job types")

        summaries = data.get('summaries', {})

        for key in ['android', 'fullstack', 'ml', 'general']:
            new_summary = st.text_area(
                f"{key.upper()} Summary",
                value=summaries.get(key, ''),
                height=100,
                key=f"summary_{key}"
            )
            summaries[key] = new_summary

        if st.button("💾 Update Summaries", type="primary"):
            data['summaries'] = summaries
            st.session_state.modified = True
            st.success("✅ Summaries updated! Remember to save changes.")

    # Section: Companies
    elif section == "Companies":
        st.header("💼 Work Experience")

        companies = data.get('companies', [])

        # Company selector
        company_names = [f"{c.get('name', 'Unknown')} - {c.get('position', 'Unknown')}" for c in companies]

        if not companies:
            st.info("No companies found. Add your first company below.")
        else:
            selected_company_idx = st.selectbox(
                "Select Company to Edit",
                range(len(companies)),
                format_func=lambda x: company_names[x]
            )

            company = companies[selected_company_idx]

            st.markdown(f"### Editing: {company.get('name', 'Unknown')}")

            # Company details
            col1, col2 = st.columns(2)

            with col1:
                company['name'] = st.text_input("Company Name", value=company.get('name', ''))
                company['position'] = st.text_input("Position", value=company.get('position', ''))
                company['dates'] = st.text_input("Dates", value=company.get('dates', ''))

            with col2:
                company['location'] = st.text_input("Location", value=company.get('location', ''))
                company['id'] = st.text_input("ID (unique)", value=company.get('id', ''))
                company['mandatory'] = st.checkbox("Mandatory", value=company.get('mandatory', True))

            # Bullet constraints
            st.markdown("#### Bullet Constraints")
            col1, col2 = st.columns(2)
            with col1:
                min_bullets = st.number_input(
                    "Minimum Bullets",
                    min_value=1,
                    max_value=10,
                    value=company.get('bullet_constraints', {}).get('min', 4)
                )
            with col2:
                max_bullets = st.number_input(
                    "Maximum Bullets",
                    min_value=1,
                    max_value=10,
                    value=company.get('bullet_constraints', {}).get('max', 6)
                )

            company['bullet_constraints'] = {'min': min_bullets, 'max': max_bullets}

            # Bullets
            st.markdown("#### Bullet Points")
            bullets = company.get('bullets', [])

            # Display existing bullets
            bullets_to_delete = []
            for i, bullet in enumerate(bullets):
                col1, col2 = st.columns([5, 1])
                with col1:
                    new_text = st.text_area(
                        f"Bullet {i + 1}",
                        value=bullet.get('text', ''),
                        height=100,
                        key=f"bullet_{selected_company_idx}_{i}"
                    )
                    bullet['text'] = new_text
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"delete_bullet_{selected_company_idx}_{i}"):
                        bullets_to_delete.append(i)

            # Remove deleted bullets
            for idx in sorted(bullets_to_delete, reverse=True):
                bullets.pop(idx)

            # Add new bullet
            if st.button("➕ Add New Bullet"):
                bullets.append({"text": "New bullet point - edit me!", "mandatory": False})
                st.session_state.modified = True
                st.rerun()

            # Delete company button
            st.markdown("---")
            if st.button(f"🗑️ Delete Company: {company.get('name')}", type="secondary"):
                companies.pop(selected_company_idx)
                st.session_state.modified = True
                st.success(f"✅ Deleted {company.get('name')}")
                st.rerun()

        # Add new company
        st.markdown("---")
        if st.button("➕ Add New Company", type="primary"):
            new_company = {
                "id": f"company_{len(companies) + 1}",
                "mandatory": True,
                "name": "New Company",
                "position": "Position Title",
                "dates": "Start - End",
                "location": "City, Country",
                "bullet_constraints": {"min": 4, "max": 6},
                "bullets": [
                    {"text": "First achievement", "mandatory": False}
                ]
            }
            companies.append(new_company)
            st.session_state.modified = True
            st.success("✅ New company added!")
            st.rerun()

    # Section: Skills
    elif section == "Skills":
        st.header("🛠️ Technical Skills")

        skills = data.get('skills', {})

        skill_categories = ['languages', 'platforms', 'skills', 'frameworks', 'tools', 'database']

        for category in skill_categories:
            st.markdown(f"### {category.title()}")

            # Get current skills
            current_skills = skills.get(category, [])
            mandatory_skills = skills.get(f"{category}_mandatory", [])

            col1, col2 = st.columns([3, 1])

            with col1:
                # Text area for skills (comma-separated)
                skills_text = st.text_area(
                    f"{category.title()} (comma-separated)",
                    value=", ".join(current_skills),
                    height=100,
                    key=f"skills_{category}"
                )
                # Update skills
                skills[category] = [s.strip() for s in skills_text.split(',') if s.strip()]

            with col2:
                # Mandatory skills
                mandatory_text = st.text_area(
                    "Mandatory",
                    value=", ".join(mandatory_skills),
                    height=100,
                    key=f"mandatory_{category}"
                )
                skills[f"{category}_mandatory"] = [s.strip() for s in mandatory_text.split(',') if s.strip()]

        if st.button("💾 Update Skills", type="primary"):
            data['skills'] = skills
            st.session_state.modified = True
            st.success("✅ Skills updated! Remember to save changes.")

    # Section: Projects
    elif section == "Projects":
        st.header("🚀 Personal Projects")

        projects = data.get('projects', [])

        if not projects:
            st.info("No projects found. Add your first project below.")
        else:
            # Project selector
            project_names = [p.get('name', 'Unknown') for p in projects]
            selected_project_idx = st.selectbox(
                "Select Project to Edit",
                range(len(projects)),
                format_func=lambda x: project_names[x]
            )

            project = projects[selected_project_idx]

            st.markdown(f"### Editing: {project.get('name', 'Unknown')}")

            col1, col2 = st.columns(2)

            with col1:
                project['name'] = st.text_input("Project Name", value=project.get('name', ''))
                project['tech'] = st.text_input("Technologies", value=project.get('tech', ''))
                project['date'] = st.text_input("Date", value=project.get('date', ''))

            with col2:
                project['id'] = st.text_input("ID (unique)", value=project.get('id', ''))
                project['link'] = st.text_input("Link/URL", value=project.get('link', ''))
                project['mandatory'] = st.checkbox("Mandatory", value=project.get('mandatory', False))

            project['description'] = st.text_area(
                "Description",
                value=project.get('description', ''),
                height=150
            )

            # Delete project button
            st.markdown("---")
            if st.button(f"🗑️ Delete Project: {project.get('name')}", type="secondary"):
                projects.pop(selected_project_idx)
                st.session_state.modified = True
                st.success(f"✅ Deleted {project.get('name')}")
                st.rerun()

        # Add new project
        st.markdown("---")
        if st.button("➕ Add New Project", type="primary"):
            new_project = {
                "id": f"project_{len(projects) + 1}",
                "mandatory": False,
                "name": "New Project",
                "tech": "Technologies used",
                "description": "Project description here",
                "date": "Month Year",
                "link": ""
            }
            projects.append(new_project)
            st.session_state.modified = True
            st.success("✅ New project added!")
            st.rerun()

    # Section: Education
    elif section == "Education":
        st.header("🎓 Education")

        education = data.get('education', [])

        if not education:
            st.info("No education entries found.")
        else:
            for i, edu in enumerate(education):
                st.markdown(f"### Education {i + 1}")

                col1, col2 = st.columns(2)

                with col1:
                    edu['degree'] = st.text_input("Degree", value=edu.get('degree', ''), key=f"edu_degree_{i}")
                    edu['course'] = st.text_input("Course/Major", value=edu.get('course', ''), key=f"edu_course_{i}")
                    edu['institution'] = st.text_input("Institution", value=edu.get('institution', ''),
                                                       key=f"edu_inst_{i}")

                with col2:
                    edu['dates'] = st.text_input("Dates", value=edu.get('dates', ''), key=f"edu_dates_{i}")
                    edu['location'] = st.text_input("Location", value=edu.get('location', ''), key=f"edu_loc_{i}")

                if st.button(f"🗑️ Delete Education {i + 1}", key=f"delete_edu_{i}"):
                    education.pop(i)
                    st.session_state.modified = True
                    st.rerun()

                st.markdown("---")

        if st.button("➕ Add Education Entry", type="primary"):
            new_edu = {
                "degree": "Degree Type",
                "course": "Course Name",
                "institution": "Institution Name",
                "dates": "Start - End",
                "location": "City, Country"
            }
            education.append(new_edu)
            st.session_state.modified = True
            st.success("✅ New education entry added!")
            st.rerun()

    # Section: Configuration
    elif section == "Configuration":
        st.header("⚙️ Configuration")

        config = data.get('config', {})

        st.markdown("### Page Settings")
        config['page_limit'] = st.number_input(
            "Page Limit",
            min_value=1,
            max_value=5,
            value=config.get('page_limit', 2)
        )

        st.markdown("### Bullet Constraints")
        col1, col2 = st.columns(2)
        with col1:
            bullets_min = st.number_input(
                "Total Minimum Bullets",
                min_value=10,
                max_value=30,
                value=config.get('bullets', {}).get('total_min', 16)
            )
        with col2:
            bullets_max = st.number_input(
                "Total Maximum Bullets",
                min_value=10,
                max_value=30,
                value=config.get('bullets', {}).get('total_max', 20)
            )

        config['bullets'] = {'total_min': bullets_min, 'total_max': bullets_max}

        st.markdown("### Project Constraints")
        col1, col2 = st.columns(2)
        with col1:
            projects_min = st.number_input(
                "Minimum Projects",
                min_value=0,
                max_value=10,
                value=config.get('projects', {}).get('min', 2)
            )
        with col2:
            projects_max = st.number_input(
                "Maximum Projects",
                min_value=0,
                max_value=10,
                value=config.get('projects', {}).get('max', 3)
            )

        config['projects'] = {
            'min': projects_min,
            'max': projects_max,
            'note': config.get('projects', {}).get('note', 'Space-dependent')
        }

        st.markdown("### Skills Per Category")

        skills_config = config.get('skills_per_category', {})

        for category in ['languages', 'platforms', 'skills', 'frameworks', 'tools', 'database']:
            st.markdown(f"#### {category.title()}")
            col1, col2 = st.columns(2)

            with col1:
                min_val = st.number_input(
                    f"Min {category}",
                    min_value=0,
                    max_value=20,
                    value=skills_config.get(category, {}).get('min', 5),
                    key=f"config_min_{category}"
                )
            with col2:
                max_val = st.number_input(
                    f"Max {category}",
                    min_value=0,
                    max_value=30,
                    value=skills_config.get(category, {}).get('max', 10),
                    key=f"config_max_{category}"
                )

            skills_config[category] = {'min': min_val, 'max': max_val}

        config['skills_per_category'] = skills_config

        if st.button("💾 Update Configuration", type="primary"):
            data['config'] = config
            st.session_state.modified = True
            st.success("✅ Configuration updated! Remember to save changes.")

    # JSON Preview
    with st.expander("🔍 Preview JSON"):
        st.json(st.session_state.resume_data)