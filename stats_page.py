import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import math
import config_manager


def get_applications_file():
    """Get the path to applications tracking file for current user"""
    user_paths = config_manager.get_current_user_paths()
    if user_paths:
        return user_paths['tracking_file']
    return "applications_tracking.json"  # Fallback


def load_applications():
    """Load applications from JSON file"""
    applications_file = get_applications_file()
    if Path(applications_file).exists():
        with open(applications_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_applications(applications):
    """Save applications to JSON file"""
    applications_file = get_applications_file()
    with open(applications_file, 'w', encoding='utf-8') as f:
        json.dump(applications, f, indent=2)


def add_application(company_name, job_description, date=None):
    """Add a new application to tracking"""
    applications = load_applications()

    new_application = {
        "id": len(applications) + 1,
        "company_name": company_name,
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "job_description": job_description,
        "heard_back": False
    }

    applications.append(new_application)
    save_applications(applications)
    return new_application


def update_heard_back(app_id, heard_back_status):
    """Update heard_back status for an application"""
    applications = load_applications()

    for app in applications:
        if app['id'] == app_id:
            app['heard_back'] = heard_back_status
            break

    save_applications(applications)


def calculate_stats(applications):
    """Calculate statistics from applications"""
    if not applications:
        return {
            'total': 0,
            'avg_per_day': 0,
            'avg_per_week': 0,
            'heard_back_count': 0,
            'heard_back_rate': 0
        }

    # Parse dates
    dates = [datetime.strptime(app['date'], "%Y-%m-%d") for app in applications]
    earliest = min(dates)
    latest = max(dates)

    # Calculate days span
    days_span = (latest - earliest).days + 1
    weeks_span = days_span / 7

    total = len(applications)
    heard_back_count = sum(1 for app in applications if app['heard_back'])

    return {
        'total': total,
        'avg_per_day': round(total / days_span, 2) if days_span > 0 else total,
        'avg_per_week': round(total / weeks_span, 2) if weeks_span > 0 else total,
        'heard_back_count': heard_back_count,
        'heard_back_rate': round((heard_back_count / total) * 100, 1) if total > 0 else 0
    }


def show():
    """Stats Page - Track job applications"""

    st.markdown("<h1 class='main-header'>📊 Application Stats</h1>", unsafe_allow_html=True)
    st.markdown("Track your job applications and responses")

    # Load applications
    applications = load_applications()

    # Calculate stats
    stats = calculate_stats(applications)

    # --- STATS METRICS ---
    st.markdown("---")
    st.markdown("### 📈 Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Applications", stats['total'])

    with col2:
        st.metric("Avg per Day", stats['avg_per_day'])

    with col3:
        st.metric("Avg per Week", stats['avg_per_week'])

    with col4:
        st.metric("Response Rate", f"{stats['heard_back_rate']}%",
                 delta=f"{stats['heard_back_count']}/{stats['total']}")

    st.markdown("---")

    # --- SEARCH AND FILTER ---
    st.markdown("### 🔍 Search Applications")

    col_search, col_filter = st.columns([3, 1])

    with col_search:
        search_query = st.text_input(
            "Search by company name or job description",
            placeholder="e.g., Google, Android Developer...",
            key="search_applications"
        )

    with col_filter:
        filter_option = st.selectbox(
            "Filter by Response",
            options=["All", "Heard Back", "No Response"],
            key="filter_heard_back"
        )

    # Filter applications based on search and filter
    filtered_apps = applications.copy()

    if search_query:
        search_lower = search_query.lower()
        filtered_apps = [
            app for app in filtered_apps
            if search_lower in app['company_name'].lower() or
               search_lower in app['job_description'].lower()
        ]

    if filter_option == "Heard Back":
        filtered_apps = [app for app in filtered_apps if app['heard_back']]
    elif filter_option == "No Response":
        filtered_apps = [app for app in filtered_apps if not app['heard_back']]

    # Sort by date (most recent first)
    filtered_apps.sort(key=lambda x: x['date'], reverse=True)

    st.markdown(f"**Showing {len(filtered_apps)} application(s)**")

    # --- PAGINATION ---
    items_per_page = 20
    total_pages = math.ceil(len(filtered_apps) / items_per_page) if filtered_apps else 1

    # Initialize page number in session state
    if 'stats_page_number' not in st.session_state:
        st.session_state.stats_page_number = 1

    # Ensure page number is within bounds
    if st.session_state.stats_page_number > total_pages:
        st.session_state.stats_page_number = total_pages
    if st.session_state.stats_page_number < 1:
        st.session_state.stats_page_number = 1

    # Pagination controls
    col_prev, col_page_info, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.button("⬅️ Previous", disabled=(st.session_state.stats_page_number == 1)):
            st.session_state.stats_page_number -= 1
            st.rerun()

    with col_page_info:
        st.markdown(f"<div style='text-align: center; padding: 8px;'>Page {st.session_state.stats_page_number} of {total_pages}</div>",
                   unsafe_allow_html=True)

    with col_next:
        if st.button("Next ➡️", disabled=(st.session_state.stats_page_number >= total_pages)):
            st.session_state.stats_page_number += 1
            st.rerun()

    # Calculate slice for current page
    start_idx = (st.session_state.stats_page_number - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_apps = filtered_apps[start_idx:end_idx]

    # --- APPLICATIONS LIST ---
    st.markdown("---")
    st.markdown("### 📋 Applications")

    if not page_apps:
        st.info("No applications found. Start applying and they'll show up here!")
    else:
        # Table header
        header_cols = st.columns([0.5, 2, 1.5, 4, 1])
        with header_cols[0]:
            st.markdown("**#**")
        with header_cols[1]:
            st.markdown("**Company**")
        with header_cols[2]:
            st.markdown("**Date**")
        with header_cols[3]:
            st.markdown("**Job Description**")
        with header_cols[4]:
            st.markdown("**Response**")

        st.markdown("---")

        # Display applications
        for idx, app in enumerate(page_apps, start=start_idx + 1):
            cols = st.columns([0.5, 2, 1.5, 4, 1])

            with cols[0]:
                st.text(f"{idx}")

            with cols[1]:
                st.text(app['company_name'])

            with cols[2]:
                st.text(app['date'])

            with cols[3]:
                # Show job description with expander for long text
                job_desc = app['job_description']
                if len(job_desc) > 100:
                    # Show truncated with expander
                    with st.expander(f"{job_desc[:100]}..."):
                        st.text_area(
                            "Full Job Description",
                            value=job_desc,
                            height=200,
                            disabled=True,
                            key=f"job_desc_full_{app['id']}",
                            label_visibility="collapsed"
                        )
                else:
                    st.text(job_desc)

            with cols[4]:
                # Checkbox for heard_back - immediately updates on change
                heard_back = st.checkbox(
                    "✓",
                    value=app['heard_back'],
                    key=f"heard_back_{app['id']}",
                    label_visibility="collapsed"
                )

                # Update if changed
                if heard_back != app['heard_back']:
                    update_heard_back(app['id'], heard_back)
                    st.rerun()

            st.markdown("---")

    # Export functionality
    st.markdown("### 📥 Export Data")

    if applications:
        # Convert to DataFrame for export
        df = pd.DataFrame(applications)

        col_export1, col_export2 = st.columns(2)

        with col_export1:
            # Export as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📄 Download as CSV",
                data=csv,
                file_name=f"applications_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_export2:
            # Export as JSON
            json_str = json.dumps(applications, indent=2)
            st.download_button(
                label="📋 Download as JSON",
                data=json_str,
                file_name=f"applications_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.info("No data to export yet.")


if __name__ == "__main__":
    show()
