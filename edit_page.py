import streamlit as st
import json
import shutil
from pathlib import Path
from datetime import datetime
import config_manager

# Template type descriptions
TEMPLATE_OPTIONS = {
    "custom_section_template_1": "📄 Simple (Title + Subtitle + Content)",
    "custom_section_template_2": "📑 Subsections (No Bullets)",
    "custom_section_template_3": "📋 Subsections with Bullets"
}


def show():
    """Edit Resume Data Page"""

    # Title
    st.markdown("<h1 class='main-header'>✏️ Edit Resume Data</h1>", unsafe_allow_html=True)
    st.markdown("Manage your resume data with an easy-to-use interface")

    # Get current user paths
    user_paths = config_manager.get_current_user_paths()
    if not user_paths:
        st.error("❌ No user configured. Please go to Settings to set up your profile.")
        st.stop()

    # File paths - use user-specific paths
    resume_data_path = Path(user_paths['resume_data'])
    backup_dir = Path(user_paths['content_dir']) / 'backups'
    backup_dir.mkdir(exist_ok=True)
    default_backup_path = backup_dir / "resume_data_enhanced_DEFAULT.json"

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
                    backup_path = backup_dir / f"resume_data_enhanced_backup_{timestamp}.json"
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
            ["Static Info", "Summaries", "Companies", "Skills", "Projects", "Education", "Custom Sections", "Template Settings", "Configuration", "Display Settings"],
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

        # Update button for basic info
        if st.button("💾 Update Basic Info", type="primary"):
            # Preserve existing links if present
            updated_static = {
                'name': new_name,
                'address': new_address,
                'phone': new_phone,
                'email': new_email
            }

            # Keep links if they exist
            if 'links' in static:
                updated_static['links'] = static['links']

            data['static_info'] = updated_static
            st.session_state.modified = True
            st.success("✅ Basic info updated! Remember to save changes.")

        st.markdown("---")
        st.markdown("### 🔗 Profile Links")
        st.markdown("Manage links that appear on your resume (LinkedIn, GitHub, Portfolio, etc.)")

        # Get or initialize links
        links = static.get('links', [])

        # Display existing links
        if links:
            st.markdown("#### Current Links")
            links_to_delete = []

            for idx, link in enumerate(links):
                col1, col2, col3 = st.columns([2, 4, 1])

                with col1:
                    link['title'] = st.text_input(
                        "Title",
                        value=link.get('title', ''),
                        key=f"link_title_{idx}",
                        label_visibility="collapsed",
                        placeholder="e.g., LinkedIn"
                    )

                with col2:
                    link['url'] = st.text_input(
                        "URL",
                        value=link.get('url', ''),
                        key=f"link_url_{idx}",
                        label_visibility="collapsed",
                        placeholder="https://..."
                    )

                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"delete_link_{idx}", help="Delete link"):
                        links_to_delete.append(idx)

            # Delete marked links
            for idx in sorted(links_to_delete, reverse=True):
                links.pop(idx)
                st.session_state.modified = True
                st.rerun()

        # Add new link
        st.markdown("#### Add New Link")
        col1, col2, col3 = st.columns([2, 4, 1])

        with col1:
            new_link_title = st.text_input("Title", key="new_link_title", placeholder="e.g., GitHub")

        with col2:
            new_link_url = st.text_input("URL", key="new_link_url", placeholder="https://...")

        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add", key="add_link"):
                if new_link_title and new_link_url:
                    links.append({'title': new_link_title, 'url': new_link_url})
                    static['links'] = links
                    st.session_state.modified = True
                    st.rerun()
                else:
                    st.error("Both title and URL required")

        # Save links button
        if st.button("💾 Save Links", type="secondary"):
            static['links'] = links
            data['static_info'] = static
            st.session_state.modified = True
            st.success("✅ Links saved! Remember to save all changes.")

    # Section: Summaries
    elif section == "Summaries":
        st.header("📝 Professional Summaries")
        st.markdown("Manage your professional summary options. The AI will select the most appropriate one for each job.")

        # Initialize summaries as array if it's not
        summaries = data.get('summaries', [])
        if isinstance(summaries, dict):
            # Convert old format to new format
            summaries = [
                {"id": f"summary_{i+1}", "label": f"Option {i+1}", "text": text}
                for i, text in enumerate(summaries.values())
            ]
            data['summaries'] = summaries

        # Ensure it's a list
        if not isinstance(summaries, list):
            summaries = []

        # Add New Summary button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("➕ Add New Summary", use_container_width=True):
                next_id = len(summaries) + 1
                summaries.append({
                    "id": f"summary_{next_id}",
                    "label": f"Option {next_id}",
                    "text": ""
                })
                st.session_state.modified = True
                st.rerun()

        st.markdown("---")

        # Display each summary with delete option
        summaries_to_delete = []

        for idx, summary in enumerate(summaries):
            st.markdown(f"### Summary {idx + 1}")

            col1, col2 = st.columns([3, 1])

            with col1:
                # Label input
                new_label = st.text_input(
                    "Label",
                    value=summary.get('label', f"Option {idx+1}"),
                    key=f"summary_label_{idx}",
                    help="This helps you identify the summary (e.g., 'Android Focus', 'ML Focus')"
                )
                summary['label'] = new_label

            with col2:
                # Delete button
                st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                if st.button(f"🗑️ Delete", key=f"delete_summary_{idx}", use_container_width=True):
                    summaries_to_delete.append(idx)

            # Text area for summary
            new_text = st.text_area(
                "Summary Text",
                value=summary.get('text', ''),
                height=120,
                key=f"summary_text_{idx}",
                label_visibility="collapsed"
            )
            summary['text'] = new_text

            # Update ID if not present
            if 'id' not in summary:
                summary['id'] = f"summary_{idx+1}"

            st.markdown("---")

        # Delete summaries marked for deletion
        if summaries_to_delete:
            for idx in sorted(summaries_to_delete, reverse=True):
                summaries.pop(idx)
            st.session_state.modified = True
            st.rerun()

        # Update button
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

        skills = data.get('skills', [])

        # Handle both v1.0 (dict) and v2.0 (array) formats
        if isinstance(skills, dict):
            st.warning("⚠️ Your resume JSON is using the old v1.0 format. Please migrate to v2.0 format for flexible skill management.")

            col1, col2 = st.columns([2, 1])
            with col1:
                st.info("💡 **What will migration do?**\n\n- Convert hardcoded categories to flexible sections\n- Add min/max constraints per section\n- Create a backup file: `resume_data_enhanced_v1.0_backup.json`")

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Migrate to v2.0", type="primary", use_container_width=True):
                    with st.spinner("Migrating..."):
                        from migrate_resume_json import migrate_with_backup

                        success, message, backup_path = migrate_with_backup(resume_data_path, '_v1.0_backup')

                        if success:
                            st.success(f"✅ {message}")
                            if backup_path:
                                st.info(f"📁 Backup saved: `{backup_path}`")

                            # Reload data
                            with open(resume_data_path, 'r') as f:
                                st.session_state.resume_data = json.load(f)
                            st.session_state.modified = False
                            st.success("✅ Data reloaded. Refresh the page to see changes!")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
            st.stop()

        # New v2.0 format - array of skill sections
        if not skills:
            st.info("No skill sections found. Add your first skill section below.")

        # Display existing skill sections
        for idx, skill_section in enumerate(skills):
            with st.expander(f"📁 {skill_section.get('title', f'Section {idx+1}')}", expanded=True):
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Title
                    title = st.text_input(
                        "Section Title",
                        value=skill_section.get('title', ''),
                        key=f"skill_title_{idx}"
                    )
                    skills[idx]['title'] = title

                    # Items
                    items_text = st.text_area(
                        "Items (comma-separated)",
                        value=", ".join(skill_section.get('items', [])),
                        height=100,
                        key=f"skill_items_{idx}"
                    )
                    skills[idx]['items'] = [s.strip() for s in items_text.split(',') if s.strip()]

                with col2:
                    # Min/Max
                    min_val = st.number_input(
                        "Min",
                        min_value=0,
                        value=skill_section.get('min', 5),
                        key=f"skill_min_{idx}"
                    )
                    skills[idx]['min'] = min_val

                    max_val = st.number_input(
                        "Max",
                        min_value=min_val,
                        value=skill_section.get('max', 10),
                        key=f"skill_max_{idx}"
                    )
                    skills[idx]['max'] = max_val

                    # Mandatory items
                    mandatory_text = st.text_area(
                        "Mandatory Items",
                        value=", ".join(skill_section.get('mandatoryItems', [])),
                        height=100,
                        key=f"skill_mandatory_{idx}"
                    )
                    skills[idx]['mandatoryItems'] = [s.strip() for s in mandatory_text.split(',') if s.strip()]

                # Remove button
                if st.button(f"🗑️ Remove {title}", key=f"remove_skill_{idx}"):
                    skills.pop(idx)
                    st.session_state.modified = True
                    st.rerun()

        # Add new skill section
        st.markdown("---")
        with st.expander("➕ Add New Skill Section"):
            new_title = st.text_input("Section Title", key="new_skill_title")
            new_items = st.text_area("Items (comma-separated)", key="new_skill_items")
            col1, col2 = st.columns(2)
            with col1:
                new_min = st.number_input("Min", min_value=0, value=5, key="new_skill_min")
            with col2:
                new_max = st.number_input("Max", min_value=new_min, value=10, key="new_skill_max")
            new_mandatory = st.text_area("Mandatory Items (comma-separated)", key="new_skill_mandatory")

            if st.button("➕ Add Skill Section", type="primary"):
                if new_title and new_items:
                    new_section = {
                        "title": new_title,
                        "items": [s.strip() for s in new_items.split(',') if s.strip()],
                        "mandatoryItems": [s.strip() for s in new_mandatory.split(',') if s.strip()],
                        "min": new_min,
                        "max": new_max
                    }
                    skills.append(new_section)
                    data['skills'] = skills
                    st.session_state.modified = True
                    st.success(f"✅ Added new skill section: {new_title}")
                    st.rerun()
                else:
                    st.error("Please provide a title and at least one item.")

        if st.button("💾 Update Skills", type="primary", key="update_skills_btn"):
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

    # Section: Display Settings
    elif section == "Display Settings":
        st.header("🎨 Display Settings")
        st.markdown("Customize section titles and visibility in your resume")

        # Initialize display_settings if not present
        if 'display_settings' not in data:
            data['display_settings'] = {
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

        display_settings = data.get('display_settings', {})
        sections_config = display_settings.get('sections', {})

        # Summary Section
        st.markdown("### 📝 Summary Section")
        col1, col2 = st.columns([1, 3])
        with col1:
            summary_enabled = st.checkbox(
                "Enabled",
                value=sections_config.get('summary', {}).get('enabled', True),
                key="summary_enabled"
            )
        with col2:
            summary_title = st.text_input(
                "Section Title",
                value=sections_config.get('summary', {}).get('title', 'Professional Summary'),
                key="summary_title"
            )
        sections_config['summary'] = {"enabled": summary_enabled, "title": summary_title}

        st.markdown("---")

        # Experience Section
        st.markdown("### 💼 Experience Section")
        col1, col2 = st.columns([1, 3])
        with col1:
            experience_enabled = st.checkbox(
                "Enabled",
                value=sections_config.get('experience', {}).get('enabled', True),
                key="experience_enabled"
            )
        with col2:
            experience_title = st.text_input(
                "Section Title",
                value=sections_config.get('experience', {}).get('title', 'Professional Experience'),
                key="experience_title"
            )
        sections_config['experience'] = {"enabled": experience_enabled, "title": experience_title}

        st.markdown("---")

        # Skills Section
        st.markdown("### 🛠️ Skills Section")
        col1, col2 = st.columns([1, 3])
        with col1:
            skills_enabled = st.checkbox(
                "Enabled",
                value=sections_config.get('skills', {}).get('enabled', True),
                key="skills_enabled"
            )
        with col2:
            skills_title = st.text_input(
                "Section Title",
                value=sections_config.get('skills', {}).get('title', 'Technical Skills'),
                key="skills_title"
            )

        st.markdown("**Skill Category Names** (in order: Languages, Platforms, Skills, Frameworks, Tools, Database)")
        default_categories = ["Languages", "Platforms", "Skills", "Frameworks", "Tools", "Database"]
        current_categories = sections_config.get('skills', {}).get('categories', default_categories)

        col1, col2, col3 = st.columns(3)
        with col1:
            cat1 = st.text_input("Category 1 (languages)", value=current_categories[0] if len(current_categories) > 0 else "Languages", key="cat1")
            cat2 = st.text_input("Category 2 (platforms)", value=current_categories[1] if len(current_categories) > 1 else "Platforms", key="cat2")
        with col2:
            cat3 = st.text_input("Category 3 (skills)", value=current_categories[2] if len(current_categories) > 2 else "Skills", key="cat3")
            cat4 = st.text_input("Category 4 (frameworks)", value=current_categories[3] if len(current_categories) > 3 else "Frameworks", key="cat4")
        with col3:
            cat5 = st.text_input("Category 5 (tools)", value=current_categories[4] if len(current_categories) > 4 else "Tools", key="cat5")
            cat6 = st.text_input("Category 6 (database)", value=current_categories[5] if len(current_categories) > 5 else "Database", key="cat6")

        sections_config['skills'] = {
            "enabled": skills_enabled,
            "title": skills_title,
            "categories": [cat1, cat2, cat3, cat4, cat5, cat6]
        }

        st.markdown("---")

        # Education Section
        st.markdown("### 🎓 Education Section")
        col1, col2 = st.columns([1, 3])
        with col1:
            education_enabled = st.checkbox(
                "Enabled",
                value=sections_config.get('education', {}).get('enabled', True),
                key="education_enabled"
            )
        with col2:
            education_title = st.text_input(
                "Section Title",
                value=sections_config.get('education', {}).get('title', 'Education'),
                key="education_title"
            )
        sections_config['education'] = {"enabled": education_enabled, "title": education_title}

        st.markdown("---")

        # Projects Section
        st.markdown("### 🚀 Projects Section")
        col1, col2 = st.columns([1, 3])
        with col1:
            projects_enabled = st.checkbox(
                "Enabled",
                value=sections_config.get('projects', {}).get('enabled', True),
                key="projects_enabled"
            )
        with col2:
            projects_title = st.text_input(
                "Section Title",
                value=sections_config.get('projects', {}).get('title', 'Personal Projects'),
                key="projects_title"
            )
        sections_config['projects'] = {"enabled": projects_enabled, "title": projects_title}

        # Update display_settings
        display_settings['sections'] = sections_config

        if st.button("💾 Update Display Settings", type="primary"):
            data['display_settings'] = display_settings
            st.session_state.modified = True
            st.success("✅ Display settings updated! Remember to save changes.")

    # Section: Custom Sections
    elif section == "Custom Sections":
        st.header("📄 Custom Resume Sections")
        st.markdown("Create custom sections like Publications, Certifications, Awards, etc.")

        # Get all custom sections (non-standard sections with 'type' field)
        standard_sections = ['summary', 'summaries', 'experience', 'companies', 'skills', 'projects', 'education',
                            'static_info', 'config', 'display_settings', 'version', 'section_order', 'font_settings']

        custom_sections = {}
        for key, value in data.items():
            if key not in standard_sections and isinstance(value, dict) and 'type' in value:
                custom_sections[key] = value

        # Display existing custom sections
        if custom_sections:
            st.markdown("### Existing Custom Sections")

            for section_key in list(custom_sections.keys()):
                section_data = custom_sections[section_key]

                with st.expander(f"📋 {section_data.get('title', section_key)}", expanded=False):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        # Title
                        new_title = st.text_input(
                            "Section Title",
                            value=section_data.get('title', ''),
                            key=f"custom_title_{section_key}"
                        )
                        section_data['title'] = new_title

                        # Template type
                        current_type = section_data.get('type', 'custom_section_template_1')
                        template_display = st.selectbox(
                            "Template Type",
                            options=list(TEMPLATE_OPTIONS.values()),
                            index=list(TEMPLATE_OPTIONS.keys()).index(current_type),
                            key=f"custom_type_{section_key}",
                            help="Choose the layout format for this custom section"
                        )
                        # Convert display name back to template key
                        section_data['type'] = list(TEMPLATE_OPTIONS.keys())[list(TEMPLATE_OPTIONS.values()).index(template_display)]

                    with col2:
                        # Mandatory checkbox
                        mandatory = st.checkbox(
                            "Mandatory",
                            value=section_data.get('mandatory', False),
                            key=f"custom_mandatory_{section_key}",
                            help="If checked, this section will always be included"
                        )
                        section_data['mandatory'] = mandatory

                        # Rewrite checkbox
                        rewrite = st.checkbox(
                            "Allow Rewrite",
                            value=section_data.get('rewrite', False),
                            key=f"custom_rewrite_{section_key}",
                            help="If checked, AI can rewrite this section's content to match job description"
                        )
                        section_data['rewrite'] = rewrite

                    # Template 1: Simple section
                    if template_type == 'custom_section_template_1':
                        subtitle = st.text_input(
                            "Subtitle (optional)",
                            value=section_data.get('subtitle', ''),
                            key=f"custom_subtitle_{section_key}"
                        )
                        section_data['subtitle'] = subtitle

                        content = st.text_area(
                            "Content",
                            value=section_data.get('content', ''),
                            height=150,
                            key=f"custom_content_{section_key}"
                        )
                        section_data['content'] = content

                    # Template 2 & 3: Subsections
                    elif template_type in ['custom_section_template_2', 'custom_section_template_3']:
                        st.markdown("#### Subsections")

                        sections_list = section_data.get('sections', [])

                        # Display existing subsections
                        for sub_idx, subsection in enumerate(sections_list):
                            st.markdown(f"**Subsection {sub_idx + 1}**")

                            col1, col2 = st.columns([3, 1])
                            with col1:
                                subsection['title'] = st.text_input(
                                    "Subsection Title",
                                    value=subsection.get('title', ''),
                                    key=f"custom_sub_title_{section_key}_{sub_idx}"
                                )
                                subsection['subtitle'] = st.text_input(
                                    "Subsection Subtitle",
                                    value=subsection.get('subtitle', ''),
                                    key=f"custom_sub_subtitle_{section_key}_{sub_idx}"
                                )

                            with col2:
                                st.markdown("<br>", unsafe_allow_html=True)
                                if st.button("🗑️", key=f"custom_sub_delete_{section_key}_{sub_idx}", help="Delete subsection"):
                                    sections_list.pop(sub_idx)
                                    st.session_state.modified = True
                                    st.rerun()

                            # Content (text for template 2, bullets for template 3)
                            if template_type == 'custom_section_template_2':
                                subsection['content'] = st.text_area(
                                    "Content",
                                    value=subsection.get('content', ''),
                                    height=100,
                                    key=f"custom_sub_content_{section_key}_{sub_idx}"
                                )
                            else:  # template 3 - bullets
                                bullets = subsection.get('content', [])
                                if not isinstance(bullets, list):
                                    bullets = []

                                bullets_text = st.text_area(
                                    "Bullets (one per line)",
                                    value="\n".join(bullets),
                                    height=100,
                                    key=f"custom_sub_bullets_{section_key}_{sub_idx}"
                                )
                                subsection['content'] = [b.strip() for b in bullets_text.split('\n') if b.strip()]

                            st.markdown("---")

                        # Add subsection button
                        if st.button(f"➕ Add Subsection", key=f"custom_add_sub_{section_key}"):
                            new_subsection = {
                                "title": "Subsection Title",
                                "subtitle": "Subtitle",
                                "content": [] if template_type == 'custom_section_template_3' else ""
                            }
                            sections_list.append(new_subsection)
                            st.session_state.modified = True
                            st.rerun()

                        section_data['sections'] = sections_list

                    # Delete section button
                    st.markdown("---")
                    if st.button(f"🗑️ Delete Section: {new_title}", key=f"custom_delete_{section_key}", type="secondary"):
                        del data[section_key]
                        st.session_state.modified = True
                        st.success(f"✅ Deleted {new_title}")
                        st.rerun()

                    # Update data
                    data[section_key] = section_data

        else:
            st.info("No custom sections found. Create your first custom section below.")

        # Add new custom section
        st.markdown("---")
        st.markdown("### ➕ Add New Custom Section")

        with st.expander("Create New Section"):
            new_section_key = st.text_input(
                "Section Key (unique identifier, no spaces)",
                key="new_custom_key",
                help="e.g., 'Publications', 'Certifications', 'Awards'"
            )

            new_section_title = st.text_input(
                "Section Title",
                key="new_custom_title"
            )

            new_template_display = st.selectbox(
                "Template Type",
                options=list(TEMPLATE_OPTIONS.values()),
                key="new_custom_type",
                help="Choose the layout format for this custom section"
            )
            # Convert display name to template key
            new_template_type = list(TEMPLATE_OPTIONS.keys())[list(TEMPLATE_OPTIONS.values()).index(new_template_display)]

            col1, col2 = st.columns(2)
            with col1:
                new_mandatory = st.checkbox("Mandatory", key="new_custom_mandatory")
            with col2:
                new_rewrite = st.checkbox("Allow Rewrite", key="new_custom_rewrite")

            if st.button("➕ Create Custom Section", type="primary"):
                if new_section_key and new_section_title:
                    # Check if key already exists
                    if new_section_key in data:
                        st.error(f"❌ Section key '{new_section_key}' already exists!")
                    else:
                        # Create new section based on template type
                        if new_template_type == 'custom_section_template_1':
                            new_section = {
                                "title": new_section_title,
                                "subtitle": "",
                                "content": "Add your content here",
                                "rewrite": new_rewrite,
                                "mandatory": new_mandatory,
                                "type": new_template_type
                            }
                        else:
                            new_section = {
                                "title": new_section_title,
                                "rewrite": new_rewrite,
                                "mandatory": new_mandatory,
                                "type": new_template_type,
                                "sections": [
                                    {
                                        "title": "Subsection 1",
                                        "subtitle": "Subtitle",
                                        "content": [] if new_template_type == 'custom_section_template_3' else "Content"
                                    }
                                ]
                            }

                        data[new_section_key] = new_section
                        st.session_state.modified = True
                        st.success(f"✅ Created new custom section: {new_section_title}")
                        st.rerun()
                else:
                    st.error("Please provide both section key and title.")

    # Section: Template Settings
    elif section == "Template Settings":
        st.header("🎨 Template Settings")
        st.markdown("Configure section ordering and font settings for your resume")

        # Initialize if not present
        if 'section_order' not in data:
            data['section_order'] = ['summary', 'skills', 'experience', 'projects', 'education']

        if 'font_settings' not in data:
            data['font_settings'] = {
                "family": "Lato",
                "sizes": {
                    "title": 12,
                    "subtitle": 10,
                    "content": 11
                }
            }

        # Section Ordering
        st.markdown("### 📋 Section Ordering")
        st.markdown("Drag sections to reorder how they appear in your resume")

        section_order = data.get('section_order', [])

        # Get all available sections (standard + custom)
        standard_section_names = ['summary', 'skills', 'experience', 'projects', 'education']
        custom_section_keys = []

        for key, value in data.items():
            if key not in ['summary', 'summaries', 'experience', 'companies', 'skills', 'projects', 'education',
                          'static_info', 'config', 'display_settings', 'version', 'section_order', 'font_settings']:
                if isinstance(value, dict) and 'type' in value:
                    custom_section_keys.append(key)

        all_sections = standard_section_names + custom_section_keys

        # Display current order with move up/down buttons
        st.markdown("#### Current Order:")
        for idx, section_name in enumerate(section_order):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.text(f"{idx + 1}. {section_name}")

            with col2:
                if idx > 0 and st.button("⬆️", key=f"move_up_{idx}"):
                    section_order[idx], section_order[idx-1] = section_order[idx-1], section_order[idx]
                    st.session_state.modified = True
                    st.rerun()

            with col3:
                if idx < len(section_order) - 1 and st.button("⬇️", key=f"move_down_{idx}"):
                    section_order[idx], section_order[idx+1] = section_order[idx+1], section_order[idx]
                    st.session_state.modified = True
                    st.rerun()

            with col4:
                if st.button("🗑️", key=f"remove_section_{idx}"):
                    section_order.pop(idx)
                    st.session_state.modified = True
                    st.rerun()

        # Add section to order
        st.markdown("#### Add Section")
        available_sections = [s for s in all_sections if s not in section_order]

        if available_sections:
            new_section = st.selectbox(
                "Section to add",
                available_sections,
                key="add_section_select"
            )

            if st.button("➕ Add Section to Order"):
                section_order.append(new_section)
                st.session_state.modified = True
                st.rerun()
        else:
            st.info("All sections are already in the order list")

        data['section_order'] = section_order

        st.markdown("---")

        # Font Settings
        st.markdown("### 🔤 Font Settings")

        font_settings = data.get('font_settings', {})

        # Font Family
        font_family = st.text_input(
            "Font Family",
            value=font_settings.get('family', 'Lato'),
            help="e.g., Lato, Arial, Times New Roman, Helvetica"
        )
        font_settings['family'] = font_family

        # Font Sizes
        st.markdown("#### Font Sizes (in points)")
        col1, col2, col3 = st.columns(3)

        sizes = font_settings.get('sizes', {})

        with col1:
            title_size = st.number_input(
                "Title Size (Section Headings)",
                min_value=8,
                max_value=18,
                value=sizes.get('title', 12),
                key="font_title_size"
            )
            sizes['title'] = title_size

        with col2:
            subtitle_size = st.number_input(
                "Subtitle Size (Subsections)",
                min_value=8,
                max_value=14,
                value=sizes.get('subtitle', 10),
                key="font_subtitle_size"
            )
            sizes['subtitle'] = subtitle_size

        with col3:
            content_size = st.number_input(
                "Content Size (Body Text)",
                min_value=8,
                max_value=14,
                value=sizes.get('content', 11),
                key="font_content_size"
            )
            sizes['content'] = content_size

        font_settings['sizes'] = sizes
        data['font_settings'] = font_settings

        # Preview
        st.markdown("---")
        st.markdown("### 👁️ Preview")
        st.info(f"**Font Family:** {font_family}\n\n**Sizes:** Title: {title_size}pt | Subtitle: {subtitle_size}pt | Content: {content_size}pt")

        # Save button
        if st.button("💾 Update Template Settings", type="primary"):
            st.session_state.modified = True
            st.success("✅ Template settings updated! Remember to save changes.")

    # JSON Preview
    with st.expander("🔍 Preview JSON"):
        st.json(st.session_state.resume_data)