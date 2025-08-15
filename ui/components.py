"""
UI functions from app_final.py - EXACT COPIES
"""

import streamlit as st
import datetime
from config.loader import SKILLS_LIST, PLE_LIST, FORM_OPTIONS
from database.operations import get_latest_incumbent_values, get_latest_successor_values

def load_css():
    """Applies custom CSS for styling elements like cards."""
    st.markdown("""
        <style>
            .name-card {
                background-color: #002E4D;
                border-radius: 10px;
                padding: 10px;
                margin: 5px 0px;
                box-shadow: 0 2px 4px 0 rgba(0,0,0,0.1);
            }
            .name-card-sidebar {
                background-color: #4C6C2D;
                border-radius: 8px;
                padding: 8px;
                margin: 4px 0px;
            }
            /* Hide the X button on dialogs */
            div[aria-label="dialog"]>button[aria-label="Close"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

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

def display_selected_incumbent_card(incumbent, show_button=True):
    person = incumbent['metadata']
    plan = incumbent['plan_details']
    full_name = f"{person['PREFERRED_NAME_FIRST_NAME']} {person['PREFERRED_NAME_LAST_NAME']}"

    if show_button:
        st.subheader("Selected Incumbent")

    with st.container(border=True):
        c1, c2 = st.columns([1, 5])
        with c1:
            st.image(f"https://rostr.disney.com/api/v2/people/{person['EMPLOYEE_ID']}/avatars/thumbnail_large?locale=en&token=abc4fc58f30914f6d99faa8a31f4d44c", width=100)
        with c2:
            st.markdown(f"### {full_name}")
            st.markdown(f"**Position:** {person['POSITION_NBR_DESCRIPTION']}")
            critical_text = "Yes" if plan.get('critical_role') else "No"
            st.markdown(f"**Critical Role?** `{critical_text}` | **Sourcing Strategy:** `{plan.get('sourcing_strategy', 'N/A')}`")
            st.markdown(f"**Scenario:** `{plan.get('scenario_plan', 'N/A')}`")

            with st.expander("View Additional Plan Details"):
                # 1. Critical Role
                st.markdown(f"**Critical Role:** {critical_text}")
                
                # 2. Contract End Date (Optional)
                if plan.get('contract_end_date'):
                    st.markdown(f"**Contract End Date:** {plan.get('contract_end_date')}")
                else:
                    st.markdown(f"**Contract End Date:** Not specified")
                
                # 4. Top Demonstrated People Leader Expectation
                st.markdown(f"**Top Demonstrated People Leader Expectation:**")
                st.info(plan.get('top_ple', 'Not specified.'))
                
                # 5. Top Leadership Skills
                st.markdown(f"**Top Leadership Skills:**")
                st.info(", ".join(plan.get('top_skills', ['Not specified.'])))
                
                # 6. Talent Sourcing Strategy
                st.markdown(f"**Talent Sourcing Strategy:** {plan.get('sourcing_strategy', 'Not specified')}")
                
                # 7. Scenario Plan
                st.markdown(f"**Scenario Plan:** {plan.get('scenario_plan', 'Not specified')}")
                
                # 8. Type of Role (optional)
                if plan.get('role_type') and plan.get('role_type') != 'Not Applicable':
                    st.markdown(f"**Type of Role:** {plan.get('role_type')}")

    if show_button:
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            if st.button("Change Incumbent", use_container_width=True, help="Select a different incumbent."):
                st.session_state.app_data['incumbent'] = None
                st.session_state.selected_person = None
                st.session_state.search_term = ""
                st.session_state.editing_incumbent = False
                st.session_state.editing_successor_index = None
                st.rerun()
        with b_col2:
            if st.button("Edit Details", use_container_width=True, help="Edit the plan details for the current incumbent."):
                st.session_state.editing_incumbent = True
                st.rerun()

@st.dialog("Incumbent Plan Details", width="large")
def display_incumbent_form():
    is_editing = st.session_state.get("editing_incumbent", False)
    
    if is_editing:
        person = st.session_state.app_data['incumbent']['metadata']
        plan_details = st.session_state.app_data['incumbent']['plan_details']
        st.subheader(f"✏️ Edit: {person['PREFERRED_NAME_FIRST_NAME']} {person['PREFERRED_NAME_LAST_NAME']}")
    else: 
        person = st.session_state.selected_person
        plan_details = {}
        st.subheader(f"📝 New Plan: {person['PREFERRED_NAME_FIRST_NAME']} {person['PREFERRED_NAME_LAST_NAME']}")
        
        # Try to get previous values for this person
        previous_values = get_latest_incumbent_values(person['EMPLOYEE_ID'])
        if previous_values:
            st.info(f"💡 Found previous submission. Fields pre-filled with latest values.")
            plan_details = previous_values

    with st.form("incumbent_form"):
        # 1. Critical Role
        critical_role = st.radio("Critical Role?", ["Yes", "No"], horizontal=True, index=0 if plan_details.get("critical_role") else 1 if 'critical_role' in plan_details else None)
        
        # 2. Contract End Date (Optional)
        contract_end_date_str = plan_details.get("contract_end_date")
        contract_end_date_val = datetime.datetime.strptime(contract_end_date_str, "%Y-%m-%d").date() if contract_end_date_str else None
        contract_end_date = st.date_input("Contract End Date (optional):", value=contract_end_date_val)
        
        # 3. Role Responsibilities & Key Attributes
        responsibilities = st.text_area("Role Responsibilities & Key Attributes:", value=plan_details.get("responsibilities", ""))
        
        # 4. Top Demonstrated People Leader Expectation
        top_ple = st.selectbox("Top Demonstrated People Leader Expectation:", PLE_LIST, index=PLE_LIST.index(plan_details.get("top_ple")) if plan_details.get("top_ple") in PLE_LIST else 0)
        
        # 5. Top Leadership Skills (select three)
        # Safety check for top_skills
        default_skills = plan_details.get("top_skills", [])
        if isinstance(default_skills, str):
            default_skills = [skill.strip() for skill in default_skills.split(',') if skill.strip()]
        valid_default_skills = [skill for skill in default_skills if skill in SKILLS_LIST]
        
        top_skills = st.multiselect("Top Leadership Skills (select three):", SKILLS_LIST, default=valid_default_skills, max_selections=3)
        
        # 6. Talent Sourcing Strategy
        sourcing_options = FORM_OPTIONS.get('sourcing_strategy', ["-- Select an Option --", "Build (Internal hire)", "External"])
        sourcing_strategy = st.selectbox("Talent Sourcing Strategy:", sourcing_options, index=sourcing_options.index(plan_details.get("sourcing_strategy")) if plan_details.get("sourcing_strategy") in sourcing_options else 0)
        
        # 7. Scenario Plan
        scenario_options = FORM_OPTIONS.get('scenario_plan', ["-- Select an Option --", "Direct Backfill", "Split Position/New Position"])
        scenario_plan = st.selectbox("Scenario Plan:", scenario_options, index=scenario_options.index(plan_details.get("scenario_plan")) if plan_details.get("scenario_plan") in scenario_options else 0)
        
        # 8. Type of Role (optional)
        role_type_options = FORM_OPTIONS.get('role_type', ["Not Applicable", "Succession Plan", "External"])
        role_type = st.selectbox("Type of Role (optional):", role_type_options, index=role_type_options.index(plan_details.get("role_type")) if plan_details.get("role_type") in role_type_options else 0)
        
        new_position_title = ""
        if scenario_plan == 'Split Position/New Position':
            new_position_title = st.text_input("New Position Title:", value=plan_details.get("new_position_title", ""))
        
        col1, col2 = st.columns(2)
        with col1:
            button_label = "Update Plan" if is_editing else "Save Plan"
            if st.form_submit_button(button_label, type="primary", use_container_width=True):
                errors = []
                if critical_role is None: errors.append("Please select if this is a Critical Role.")
                if not responsibilities: errors.append("Please enter Role Responsibilities.")
                if not top_skills: errors.append("Please select at least 1 Top Skill (up to 3).")
                if top_ple == "-- Select an Option --": errors.append("Please select a Top Demonstrated PLE.")
                if sourcing_strategy == "-- Select an Option --": errors.append("Please select a Talent Sourcing Strategy.")
                if scenario_plan == "-- Select an Option --": errors.append("Please select a Scenario Plan.")
                
                if errors:
                    for error in errors:
                        st.error(error)
                    return

                updated_plan = {
                    "critical_role": True if critical_role == "Yes" else False,
                    "responsibilities": responsibilities,
                    "top_skills": top_skills,
                    "top_ple": top_ple,
                    "contract_end_date": contract_end_date.strftime("%Y-%m-%d") if contract_end_date else None,
                    "sourcing_strategy": sourcing_strategy,
                    "role_type": role_type if role_type != "Not Applicable" else None,
                    "scenario_plan": scenario_plan,
                    "new_position_title": new_position_title if scenario_plan == 'Split Position/New Position' else None
                }
                st.session_state.app_data['incumbent'] = {"metadata": person, "plan_details": updated_plan}
                
                st.session_state.selected_person = None
                st.session_state.editing_incumbent = False
                st.success("Incumbent plan saved!")
                st.rerun()
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.selected_person = None
                st.session_state.editing_incumbent = False
                st.rerun()

@st.dialog("Successor Plan", width="large")
def display_successor_form():
    is_editing = st.session_state.editing_successor_index is not None
    
    if is_editing:
        person = st.session_state.app_data['successors'][st.session_state.editing_successor_index]['metadata']
        assessment = st.session_state.app_data['successors'][st.session_state.editing_successor_index]['assessment']
        st.subheader(f"✏️ Edit: {person['PREFERRED_NAME_FIRST_NAME']} {person['PREFERRED_NAME_LAST_NAME']}")
    else:
        person = st.session_state.selected_person
        assessment = {} 
        st.subheader(f"Add: {person['PREFERRED_NAME_FIRST_NAME']} {person['PREFERRED_NAME_LAST_NAME']}")
        
        # Try to get previous values for this person
        previous_values = get_latest_successor_values(person['EMPLOYEE_ID'])
        if previous_values:
            st.info(f"💡 Found previous submission. Fields pre-filled with latest values.")
            assessment = previous_values

    with st.form("successor_form"):
        # 1. Contract End Date (optional)
        contract_end_date_str = assessment.get("contract_end_date")
        contract_end_date_val = datetime.datetime.strptime(contract_end_date_str, "%Y-%m-%d").date() if contract_end_date_str else None
        contract_end_date = st.date_input("Contract End Date (optional):", value=contract_end_date_val)
        
        # 2. Readiness Level
        readiness_options = FORM_OPTIONS.get('readiness_level', ["-- Select an Option --", "Ready Now", "Ready Future"])
        readiness = st.selectbox("Readiness Level:", readiness_options, index=readiness_options.index(assessment.get("readiness")) if assessment.get("readiness") in readiness_options else 0)
        
        # 3. Future Readiness Timing (optional)
        future_readiness_timing = None
        if readiness == "Ready Future":
            timing_options = FORM_OPTIONS.get('future_readiness_timing', ["-- Select an Option --", "+1 to < 2 years", "+2 to < 3 years", "+3 to < 5 years"])
            future_readiness_timing = st.selectbox("Future Readiness Timing (optional):", timing_options, index=timing_options.index(assessment.get("future_readiness_timing")) if assessment.get("future_readiness_timing") in timing_options else 0)

        # 4. Strengths
        strengths = st.text_area("Strengths:", value=assessment.get("strengths", ""))
        
        # 5. Top Demonstrated People Leader Expectations
        top_ple = st.selectbox("Top Demonstrated People Leader Expectations:", PLE_LIST, index=PLE_LIST.index(assessment.get("top_ple")) if assessment.get("top_ple") in PLE_LIST else 0)
        
        # 6. Top Leadership Skills
        # Safety check for top_skills
        default_skills = assessment.get("top_skills", [])
        if isinstance(default_skills, str):
            default_skills = [skill.strip() for skill in default_skills.split(',') if skill.strip()]
        valid_default_skills = [skill for skill in default_skills if skill in SKILLS_LIST]
        
        top_skills = st.multiselect("Top Leadership Skills:", SKILLS_LIST, default=valid_default_skills, max_selections=3)
        
        # 7. Development Focus & Opportunities
        development_focus = st.text_area("Development Focus & Opportunities:", value=assessment.get("development_focus", ""))
        
        # 8. Talent Development Actions
        talent_actions = st.text_area("Talent Development Actions:", value=assessment.get("talent_actions", ""))

        col1, col2 = st.columns(2)
        with col1:
            button_label = "Update Successor" if is_editing else "Add Successor"
            if st.form_submit_button(button_label, type="primary", use_container_width=True):
                errors = []
                if readiness == "-- Select an Option --": errors.append("Please select a Readiness Level.")
                if readiness == "Ready Future" and (future_readiness_timing is None or future_readiness_timing == "-- Select an Option --"): errors.append("Please select a Future Readiness Timing.")
                if not strengths: errors.append("Please enter Successor Strengths.")
                if not top_skills: errors.append("Please select at least 1 Top Leadership Skill for the Successor.")
                if top_ple == "-- Select an Option --": errors.append("Please select a Top Demonstrated People Leader Expectation for the Successor.")
                if not development_focus: errors.append("Please enter Development Focus & Opportunities.")
                if not talent_actions: errors.append("Please enter Talent Development Actions.")
                
                if errors:
                    for error in errors:
                        st.error(error)
                    return

                successor_data = {
                    "readiness": readiness,
                    "future_readiness_timing": future_readiness_timing if readiness == "Ready Future" else None,
                    "contract_end_date": contract_end_date.strftime("%Y-%m-%d") if contract_end_date else None,
                    "strengths": strengths,
                    "top_skills": top_skills,
                    "top_ple": top_ple,
                    "development_focus": development_focus,
                    "talent_actions": talent_actions
                }
                if is_editing:
                    st.session_state.app_data['successors'][st.session_state.editing_successor_index]['assessment'] = successor_data
                    st.success(f"{person['PREFERRED_NAME_FIRST_NAME']}'s details have been updated.")
                else:
                    st.session_state.app_data['successors'].append({"metadata": person, "assessment": successor_data})
                    st.success(f"{person['PREFERRED_NAME_FIRST_NAME']} has been added as a successor.")
                
                st.session_state.selected_person = None
                st.session_state.editing_successor_index = None
                st.rerun()
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.selected_person = None
                st.session_state.editing_successor_index = None
                st.rerun()
