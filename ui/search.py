"""
Search and employee selection components with enhanced search types
"""

import streamlit as st
from utils.rostr_avatar import get_rostr_avatar
from config.loader import CONFIG

def display_search_box(role):
    """Display search box with toggle selector for search type"""
    
    # Get search configuration
    search_config = CONFIG.get('search', {})
    available_types = search_config.get('available_types', [
        {"name": "last_name", "display_name": "Last Name", "placeholder": "Enter last name..."},
        {"name": "full_name", "display_name": "Full Name", "placeholder": "Enter full name..."}
    ])
    default_type = search_config.get('default_type', 'last_name')
    
    # Initialize search type in session state
    search_type_key = f"search_type_{role}"
    if search_type_key not in st.session_state:
        st.session_state[search_type_key] = default_type
    
    # Toggle selector above the search form
    st.markdown("**Search Type:**")
    
    # Create toggle buttons
    col1, col2, col_spacer = st.columns([1, 1, 2])
    
    current_type = st.session_state[search_type_key]
    
    with col1:
        if st.button(
            "Last Name", 
            key=f"toggle_last_name_{role}",
            type="primary" if current_type == "last_name" else "secondary",
            use_container_width=True
        ):
            if current_type != "last_name":
                st.session_state[search_type_key] = "last_name"
                st.session_state.search_term = ""  # Clear search when switching
                st.rerun()
    
    with col2:
        if st.button(
            "Full Name", 
            key=f"toggle_full_name_{role}",
            type="primary" if current_type == "full_name" else "secondary",
            use_container_width=True
        ):
            if current_type != "full_name":
                st.session_state[search_type_key] = "full_name"
                st.session_state.search_term = ""  # Clear search when switching
                st.rerun()
    
    # Get current type configuration for placeholder
    current_type_config = next((t for t in available_types if t['name'] == current_type), available_types[0])
    
    # Search form with proper alignment
    with st.form(key=f"{role}_search_form"):
        col_search, col_button = st.columns([4, 1])
        
        with col_search:
            # Get placeholder text for current search type
            current_type_config = next((t for t in available_types if t['name'] == current_type), available_types[0])
            placeholder = current_type_config.get('placeholder', 'Enter search term...')
            
            search_input = st.text_input(
                "Search Term", 
                value="", 
                label_visibility="collapsed", 
                placeholder=placeholder,
                help=f"Current mode: {current_type_config['display_name']} - {current_type_config.get('placeholder', '')}"
            )
        
        with col_button:
            search_clicked = st.form_submit_button("Search", use_container_width=True)
        
        if search_clicked and search_input:
            st.session_state.search_term = search_input
            st.session_state.current_search_type = current_type
            st.rerun()
    
    # Display current search mode info
    #if current_type == "full_name":
    #    st.info("**Full Name Search**: Enter first and last name together (e.g., 'John Smith', 'Smith John', or just 'John')")
    #else:
    #    st.info("**Last Name Search**: Enter last name only (e.g., 'Smith', 'Johnson')")

def display_search_results(results, role):
    """Display search results with current search type information"""
    
    # Display results count and search type
    search_type = st.session_state.get('current_search_type', 'last_name')
    search_type_display = "Full Name" if search_type == "full_name" else "Last Name"
    
    st.markdown(f"#### Search Results")
    
    # Show search type badge
    if search_type == "full_name":
        st.success(f"Found {len(results)} results using **Full Name** search")
    else:
        st.success(f"Found {len(results)} results using **Last Name** search")
    
    for i, person in enumerate(results):
        cols = st.columns([1, 6, 2])
        full_name = f"{person['PREFERRED_FIRST_NAME']} {person['PREFERRED_LAST_NAME']}"
        with cols[0]:
            try:
                st.image(get_rostr_avatar(person['EMPLOYEE_ID']))
            except:
                pass
        with cols[1]:
            # Display name, position title, and manager name
            position_title = person.get('POSITION_TITLE', 'N/A')
            manager_name = person.get('LEADER_NAME', 'N/A')
            st.markdown(f"<div style='padding-top: 5px;'><strong>{full_name}</strong><br><span style='font-size: 0.9em; color: gray;'>{position_title}</span><br><span style='font-size: 0.8em; color: #666;'>Manager: {manager_name}</span></div>", unsafe_allow_html=True)
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
