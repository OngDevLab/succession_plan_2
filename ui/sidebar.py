"""
Sidebar display components
"""

import streamlit as st

def display_sidebar_summary():
    """Displays a summary of the current plan in the sidebar."""
    if st.session_state.app_data['incumbent']:
        st.sidebar.divider()
        st.sidebar.subheader("Plan Summary")

        incumbent_meta = st.session_state.app_data['incumbent']['metadata']
        incumbent_name = f"{incumbent_meta['PREFERRED_NAME_FIRST_NAME']} {incumbent_meta['PREFERRED_NAME_LAST_NAME']}"
        st.sidebar.markdown("💼 **Incumbent**")
        st.sidebar.markdown(f'<div class="name-card-sidebar">{incumbent_name}</div>', unsafe_allow_html=True)

        st.sidebar.markdown("🔄 **Successors**")
        successors = st.session_state.app_data['successors']
        if successors:
            for succ in successors:
                succ_meta = succ['metadata']
                succ_name = f"{succ_meta['PREFERRED_NAME_FIRST_NAME']} {succ_meta['PREFERRED_NAME_LAST_NAME']}"
                st.sidebar.markdown(f'<div class="name-card-sidebar">{succ_name}</div>', unsafe_allow_html=True)
        else:
            st.sidebar.caption("No successors added yet.")
    
    # Display warnings in sidebar
    if not st.session_state.app_data['incumbent']:
        st.sidebar.warning("⚠️ Please select an Incumbent first")
    elif not st.session_state.app_data['successors']:
        st.sidebar.warning("⚠️ Please add at least one Successor")
    elif not st.session_state.app_data['incumbent'] or not st.session_state.app_data['successors']:
        st.sidebar.error("❌ A plan requires both an Incumbent and at least one Successor")
    else:
        st.sidebar.success("✅ Plan ready for submission")
