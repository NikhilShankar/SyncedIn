import streamlit as st
from pathlib import Path

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="AI Resume Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .nav-link {
        font-size: 1.1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'generate'

# Sidebar Navigation
with st.sidebar:
    st.markdown("## 🎯 Navigation")

    # Generate Resume button
    if st.button("📄 Generate Resume", use_container_width=True,
                 type="primary" if st.session_state.current_page == 'generate' else "secondary"):
        st.session_state.current_page = 'generate'
        st.rerun()

    # Edit Resume Data button
    if st.button("✏️ Edit Resume Data", use_container_width=True,
                 type="primary" if st.session_state.current_page == 'edit' else "secondary"):
        st.session_state.current_page = 'edit'
        st.rerun()

    # Edit & Regenerate button (only show if trimmed_data exists)
    if 'trimmed_data' in st.session_state and st.session_state.trimmed_data:
        if st.button("🔄 Edit & Regenerate", use_container_width=True,
                     type="primary" if st.session_state.current_page == 'edit_regenerate' else "secondary"):
            st.session_state.current_page = 'edit_regenerate'
            st.rerun()

    # Stats button
    if st.button("📊 Application Stats", use_container_width=True,
                 type="primary" if st.session_state.current_page == 'stats' else "secondary"):
        st.session_state.current_page = 'stats'
        st.rerun()

    st.markdown("---")

    # Info section
    st.markdown("### ℹ️ About")
    st.markdown("""
    **AI Resume Generator**
    - Generate tailored resumes
    - Edit resume data easily
    - Powered by Claude AI
    """)

    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit")

# Route to appropriate page
if st.session_state.current_page == 'generate':
    import generate_page
    generate_page.show()
elif st.session_state.current_page == 'edit':
    import edit_page
    edit_page.show()
elif st.session_state.current_page == 'edit_regenerate':
    import edit_regenerate_page
    edit_regenerate_page.show()
elif st.session_state.current_page == 'stats':
    import stats_page
    stats_page.show()