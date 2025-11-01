"""
Setup Wizard for SyncedIn Resume Generator
Shown on first run to configure the system
"""

import streamlit as st
import config_manager


def show():
    """Display the setup wizard for first-time configuration"""

    # Center the content
    st.markdown("""
        <style>
        .setup-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 2rem;
        }
        .setup-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .setup-title {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .setup-subtitle {
            font-size: 1.1rem;
            color: #666;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="setup-container">', unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="setup-header">
            <div class="setup-title">Welcome to SyncedIn Resume Generator!</div>
            <div class="setup-subtitle">Let's set up your account in just a few seconds</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Instructions
    st.markdown("""
    This quick setup will:
    - Configure your AI settings
    - Create your user profile
    - Set up your resume workspace
    """)

    st.markdown("---")

    # Form
    with st.form("setup_form"):
        st.markdown("### Step 1: AI Configuration")

        # API Key input
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            help="Get your API key from https://console.anthropic.com/",
            placeholder="sk-ant-..."
        )

        st.markdown("""
        <small>Don't have an API key? <a href="https://console.anthropic.com/" target="_blank">Get one here</a></small>
        """, unsafe_allow_html=True)

        st.markdown("")  # spacing

        # Model selection
        model = st.selectbox(
            "Select AI Model",
            options=config_manager.AVAILABLE_MODELS,
            index=0,
            help="Claude Sonnet 4.5 is recommended for best results"
        )

        st.markdown("### Step 2: Create Your Profile")

        # Username input
        username = st.text_input(
            "Your Name",
            help="This will be used to organize your resumes. You can create multiple profiles later.",
            placeholder="e.g., John, Sarah, etc."
        )

        st.markdown("")  # spacing

        # Submit button
        submitted = st.form_submit_button(
            "Get Started",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            # Validation
            errors = []

            if not api_key or not api_key.strip():
                errors.append("API Key is required")
            elif not api_key.startswith("sk-ant-"):
                errors.append("API Key should start with 'sk-ant-'")

            if not username or not username.strip():
                errors.append("Name is required")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Initialize the system
                try:
                    with st.spinner("Setting up your workspace..."):
                        config_manager.initialize_first_user(
                            username=username.strip(),
                            api_key=api_key.strip(),
                            model=model
                        )

                    st.success("✅ Setup complete! Redirecting...")

                    # Clear session state and redirect
                    if 'setup_complete' in st.session_state:
                        del st.session_state['setup_complete']

                    # Small delay for user to see success message
                    import time
                    time.sleep(1)

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Setup failed: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            Your data is stored locally in Documents/SyncedIn on your computer
        </div>
    """, unsafe_allow_html=True)
