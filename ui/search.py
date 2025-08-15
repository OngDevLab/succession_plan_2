"""
Search and employee selection components
"""

import streamlit as st

def display_search_box(role):
    with st.form(key=f"{role}_search_form"):
        col1, col2 = st.columns([4, 1])
        with col1:
            search_input = st.text_input("Search by Last Name", value="", label_visibility="collapsed", placeholder="Search by Last Name")
        with col2:
            if st.form_submit_button("Search") and search_input:
                st.session_state.search_term = search_input
                st.rerun()

def display_search_results(results, role):
    st.markdown("#### Search Results")
    for i, person in enumerate(results):
        cols = st.columns([1, 6, 2])
        full_name = f"{person['PREFERRED_NAME_FIRST_NAME']} {person['PREFERRED_NAME_LAST_NAME']}"
        with cols[0]:
            st.image(f"https://rostr.disney.com/api/v2/people/{person['EMPLOYEE_ID']}/avatars/thumbnail_large?locale=en&token=abc4fc58f30914f6d99faa8a31f4d44c", width=50)
        with cols[1]:
            st.markdown(f"<div style='padding-top: 5px;'><strong>{full_name}</strong><br><span style='font-size: 0.9em; color: gray;'>{person['EMAIL_PRIMARY_WORK']}</span></div>", unsafe_allow_html=True)
        with cols[2]:
            st.write("")
            # Check if person is already selected
            is_already_selected = False
            button_text = "Select"
            if role == "successor":
                # Check if same as incumbent
                if st.session_state.app_data['incumbent'] and person['EMPLOYEE_ID'] == st.session_state.app_data['incumbent']['metadata']['EMPLOYEE_ID']:
                    is_already_selected = True
                    button_text = "Incumbent"
                # Check if already a successor
                for succ in st.session_state.app_data['successors']:
                    if person['EMPLOYEE_ID'] == succ['metadata']['EMPLOYEE_ID']:
                        is_already_selected = True
                        button_text = "Already Selected"
                        break
            
            if is_already_selected:
                st.button(button_text, key=f"select_{role}_{i}", disabled=True)
            elif st.button("Select", key=f"select_{role}_{i}"):
                st.session_state.selected_person = person
                st.session_state.search_term = ""
                st.rerun()
        st.divider()
