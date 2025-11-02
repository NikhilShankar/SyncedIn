"""
Settings Page for SyncedIn Resume Generator
Allows users to manage API keys, models, and user profiles
"""

import streamlit as st
import config_manager


def show():
    """Display the settings page"""

    st.markdown("<h1 class='main-header'>⚙️ Settings</h1>", unsafe_allow_html=True)

    # Load current config
    config = config_manager.load_global_config()
    current_user = config_manager.get_current_user()
    all_users = config_manager.get_all_users()

    # Create tabs for different settings sections
    tab1, tab2, tab3 = st.tabs(["🔑 API & Model", "👤 User Management", "🔗 Profile Links"])

    # ===== TAB 1: API & MODEL SETTINGS =====
    with tab1:
        st.markdown("### API Configuration")

        with st.form("api_settings_form"):
            # API Key
            current_key = config.get('anthropic_api_key', '')
            masked_key = f"{'•' * 20}{current_key[-8:]}" if len(current_key) > 8 else "Not set"

            st.markdown(f"**Current API Key:** `{masked_key}`")

            new_api_key = st.text_input(
                "Update API Key",
                type="password",
                help="Enter a new API key to update, or leave blank to keep current",
                placeholder="sk-ant-..."
            )

            st.markdown("---")
            st.markdown("### Model Selection")

            current_model = config.get('selected_model', 'claude-sonnet-4-5')
            new_model = st.selectbox(
                "AI Model",
                options=config_manager.AVAILABLE_MODELS,
                index=config_manager.AVAILABLE_MODELS.index(current_model) if current_model in config_manager.AVAILABLE_MODELS else 0,
                help="Select the Claude model to use for resume generation"
            )

            # Model descriptions
            st.markdown("""
            <small>
            - **Claude Sonnet 4.5**: Best balance of speed and quality (Recommended)
            - **Claude Sonnet 3.5**: Previous generation, fast and reliable
            - **Claude Opus 4**: Highest quality, slower and more expensive
            - **Claude Haiku 3.5**: Fastest and cheapest, good for quick edits
            </small>
            """, unsafe_allow_html=True)

            st.markdown("---")

            submitted = st.form_submit_button("💾 Save API Settings", use_container_width=True, type="primary")

            if submitted:
                try:
                    updated = False

                    # Update API key if provided
                    if new_api_key and new_api_key.strip():
                        if not new_api_key.startswith("sk-ant-"):
                            st.error("❌ API Key should start with 'sk-ant-'")
                        else:
                            config_manager.update_api_key(new_api_key.strip())
                            updated = True
                            st.success("✅ API Key updated successfully")

                    # Update model if changed
                    if new_model != current_model:
                        config_manager.update_selected_model(new_model)
                        updated = True
                        st.success(f"✅ Model updated to {new_model}")

                    if not updated and not new_api_key:
                        st.info("ℹ️ No changes made")

                    if updated:
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Error updating settings: {str(e)}")

    # ===== TAB 2: USER MANAGEMENT =====
    with tab2:
        st.markdown("### User Management")

        # Show current user
        st.markdown(f"**Current User:** `{current_user}`")
        st.markdown(f"**Total Users:** {len(all_users)}")

        st.markdown("---")

        # User selection/switching
        st.markdown("#### Switch User or Create New")

        col1, col2 = st.columns([3, 1])

        with col1:
            # Dropdown with existing users + "Create New" option
            user_options = all_users + ["+ Create New User"]
            default_index = all_users.index(current_user) if current_user in all_users else 0

            selected_option = st.selectbox(
                "Select User",
                options=user_options,
                index=default_index,
                help="Switch to an existing user or create a new one"
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Align button with selectbox
            if st.button("Switch", use_container_width=True, type="primary"):
                if selected_option == "+ Create New User":
                    st.session_state['show_create_user_form'] = True
                    st.rerun()
                elif selected_option != current_user:
                    # Switch user
                    if config_manager.switch_user(selected_option):
                        # Clear session state
                        keys_to_clear = ['trimmed_data', 'company_name', 'current_pdf_path', 'company_output_dir', 'latest_saved_version']
                        for key in keys_to_clear:
                            if key in st.session_state:
                                del st.session_state[key]

                        st.success(f"✅ Switched to user: {selected_option}")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to switch to user: {selected_option}")
                else:
                    st.info("ℹ️ Already on this user")

        # Create new user form (shown when "+ Create New User" is clicked)
        if st.session_state.get('show_create_user_form', False):
            st.markdown("---")
            st.markdown("#### Create New User")

            with st.form("create_user_form"):
                new_username = st.text_input(
                    "New User Name",
                    help="Enter a name for the new user profile",
                    placeholder="e.g., Sarah, Mike, etc."
                )

                col1, col2 = st.columns(2)

                with col1:
                    create_submitted = st.form_submit_button("Create User", use_container_width=True, type="primary")

                with col2:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)

                if cancel:
                    st.session_state['show_create_user_form'] = False
                    st.rerun()

                if create_submitted:
                    if not new_username or not new_username.strip():
                        st.error("❌ User name is required")
                    else:
                        try:
                            # Create new user
                            success = config_manager.create_user(new_username.strip())

                            if success:
                                # Switch to new user
                                config_manager.switch_user(new_username.strip().replace(' ', '_'))

                                # Clear session state
                                keys_to_clear = ['trimmed_data', 'company_name', 'current_pdf_path', 'company_output_dir', 'latest_saved_version']
                                for key in keys_to_clear:
                                    if key in st.session_state:
                                        del st.session_state[key]

                                st.session_state['show_create_user_form'] = False
                                st.success(f"✅ Created and switched to new user: {new_username}")
                                st.rerun()
                            else:
                                st.error(f"❌ User '{new_username}' already exists")

                        except Exception as e:
                            st.error(f"❌ Error creating user: {str(e)}")

        st.markdown("---")

        # Display all users
        st.markdown("#### All Users")

        for idx, user in enumerate(all_users, 1):
            if user == current_user:
                st.markdown(f"{idx}. **{user}** ✓ (Current)")
            else:
                st.markdown(f"{idx}. {user}")

        # User data location info
        st.markdown("---")
        st.markdown("#### Data Location")

        if current_user:
            paths = config_manager.get_user_paths(current_user)
            st.markdown(f"""
            Your resume files are stored at:
            - **Resumes**: `{paths['resumes_dir']}`
            - **Content**: `{paths['content_dir']}`
            - **Stats**: `{paths['stats_dir']}`
            """)

            st.info("""
            💡 **Tip**: On your host machine, these are in:
            - Windows: `Documents\\SyncedIn\\{username}\\`
            - Linux/Mac: `~/Documents/SyncedIn/{username}/`
            """.format(username=current_user))

    # ===== TAB 3: PROFILE LINKS MANAGEMENT =====
    with tab3:
        st.markdown("### Manage Profile Links")
        st.markdown("Add, edit, or remove links that appear on your resume (LinkedIn, GitHub, Portfolio, etc.)")

        if not current_user:
            st.warning("⚠️ Please create a user first in the User Management tab")
            st.stop()

        # Get current user's resume data
        user_paths = config_manager.get_user_paths(current_user)
        resume_data_path = user_paths['resume_data']

        try:
            import json
            import os
            from pathlib import Path

            # Load resume data
            if os.path.exists(resume_data_path):
                with open(resume_data_path, 'r', encoding='utf-8') as f:
                    resume_data = json.load(f)
            else:
                st.info(f"📄 Resume data file not found. It will be created when you generate your first resume.")
                st.stop()

            # Get static info
            static_info = resume_data.get('static_info', {})

            # Handle both old and new formats
            if 'links' not in static_info or not isinstance(static_info.get('links'), list):
                # Migrate from old format
                st.info("🔄 Converting to new links format...")
                links = []

                if static_info.get('linkedin'):
                    links.append({"title": "LinkedIn", "url": static_info['linkedin']})
                if static_info.get('github'):
                    links.append({"title": "GitHub", "url": static_info['github']})
                if static_info.get('portfolio'):
                    links.append({"title": "Portfolio", "url": static_info['portfolio']})
                if static_info.get('leetcode'):
                    links.append({"title": "LeetCode", "url": static_info['leetcode']})

                static_info['links'] = links
                resume_data['static_info'] = static_info

                # Save
                with open(resume_data_path, 'w', encoding='utf-8') as f:
                    json.dump(resume_data, f, indent=2, ensure_ascii=False)

                st.success("✅ Converted to new format!")
                st.rerun()

            links = static_info.get('links', [])

            # Display current links
            st.markdown("#### Current Links")

            if links:
                for idx, link in enumerate(links):
                    col1, col2, col3 = st.columns([2, 4, 1])

                    with col1:
                        st.text_input(
                            "Title",
                            value=link.get('title', ''),
                            key=f"link_title_{idx}",
                            label_visibility="collapsed"
                        )

                    with col2:
                        st.text_input(
                            "URL",
                            value=link.get('url', ''),
                            key=f"link_url_{idx}",
                            label_visibility="collapsed"
                        )

                    with col3:
                        if st.button("🗑️", key=f"delete_link_{idx}", help="Delete this link"):
                            links.pop(idx)
                            static_info['links'] = links
                            resume_data['static_info'] = static_info

                            with open(resume_data_path, 'w', encoding='utf-8') as f:
                                json.dump(resume_data, f, indent=2, ensure_ascii=False)

                            st.success("✅ Link deleted!")
                            st.rerun()
            else:
                st.info("No links added yet. Add your first link below!")

            st.markdown("---")

            # Add new link
            st.markdown("#### Add New Link")

            with st.form("add_link_form"):
                col1, col2 = st.columns(2)

                with col1:
                    new_link_title = st.text_input(
                        "Link Title",
                        placeholder="e.g., LinkedIn, GitHub, Portfolio",
                        help="Display title for this link"
                    )

                with col2:
                    new_link_url = st.text_input(
                        "URL",
                        placeholder="https://...",
                        help="Full URL including https://"
                    )

                add_button = st.form_submit_button("➕ Add Link", use_container_width=True, type="primary")

                if add_button:
                    if not new_link_title or not new_link_url:
                        st.error("❌ Please provide both title and URL")
                    elif not new_link_url.startswith(('http://', 'https://')):
                        st.error("❌ URL must start with http:// or https://")
                    else:
                        # Add new link
                        new_link = {
                            "title": new_link_title.strip(),
                            "url": new_link_url.strip()
                        }

                        links.append(new_link)
                        static_info['links'] = links
                        resume_data['static_info'] = static_info

                        with open(resume_data_path, 'w', encoding='utf-8') as f:
                            json.dump(resume_data, f, indent=2, ensure_ascii=False)

                        st.success(f"✅ Added {new_link_title}!")
                        st.rerun()

            # Save changes button
            st.markdown("---")
            if st.button("💾 Save All Changes", use_container_width=True, type="primary"):
                # Update links with current values from text inputs
                updated_links = []
                for idx in range(len(links)):
                    title_key = f"link_title_{idx}"
                    url_key = f"link_url_{idx}"

                    if title_key in st.session_state and url_key in st.session_state:
                        updated_links.append({
                            "title": st.session_state[title_key],
                            "url": st.session_state[url_key]
                        })

                static_info['links'] = updated_links
                resume_data['static_info'] = static_info

                with open(resume_data_path, 'w', encoding='utf-8') as f:
                    json.dump(resume_data, f, indent=2, ensure_ascii=False)

                st.success("✅ All changes saved!")
                st.rerun()

        except Exception as e:
            st.error(f"❌ Error managing links: {str(e)}")
            st.exception(e)
