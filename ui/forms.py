"""
Form components for incumbent and successor data entry
"""

import streamlit as st
import datetime
import json
from config.loader import SKILLS_LIST, PLE_LIST, FORM_OPTIONS
from database.operations import get_latest_incumbent_values, get_latest_successor_values

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

    # Custom form without st.form for dynamic behavior and persistent cancel button
    # 1. Critical Role
    critical_role = st.radio("Critical Role?", ["Yes", "No"], horizontal=True, index=0 if plan_details.get("critical_role") else 1 if 'critical_role' in plan_details else None)
    
    # 2. Contract End Date (Optional) with clear option
    contract_end_date_str = plan_details.get("contract_end_date")
    contract_end_date_val = datetime.datetime.strptime(contract_end_date_str, "%Y-%m-%d").date() if contract_end_date_str else None
    
    # Use session state to manage contract date clearing
    contract_date_key = f"inc_contract_date_{person['EMPLOYEE_ID']}_{is_editing}"
    if contract_date_key not in st.session_state:
        st.session_state[contract_date_key] = contract_end_date_val
    
    col_date, col_clear = st.columns([4, 1])
    with col_date:
        contract_end_date = st.date_input("Contract End Date (optional):", value=st.session_state[contract_date_key], key=f"inc_date_input_{contract_date_key}")
        # Update session state when date changes
        st.session_state[contract_date_key] = contract_end_date
    
    with col_clear:
        st.write("")  # Add some spacing
        if st.button("✕", help="Clear contract end date", key=f"inc_clear_date_{contract_date_key}"):
            st.session_state[contract_date_key] = None
            st.rerun()
    
    # Use the session state value for the actual contract date
    contract_end_date = st.session_state[contract_date_key]
    
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
    
    # 6. Talent Sourcing Strategy (multiselect)
    sourcing_options = FORM_OPTIONS.get('sourcing_strategy', ["Build (Internal hire)", "External"])
    # Handle existing data - convert string to list if needed
    default_sourcing = plan_details.get("sourcing_strategy", [])
    if isinstance(default_sourcing, str):
        # Handle old single-value data or JSON string
        try:
            default_sourcing = json.loads(default_sourcing) if default_sourcing.startswith('[') else [default_sourcing]
        except:
            default_sourcing = [default_sourcing] if default_sourcing and default_sourcing != "-- Select an Option --" else []
    elif not isinstance(default_sourcing, list):
        default_sourcing = []
    # Ensure default values are in the options list
    valid_default_sourcing = [strategy for strategy in default_sourcing if strategy in sourcing_options]
    
    sourcing_strategy = st.multiselect("Talent Sourcing Strategy:", sourcing_options, default=valid_default_sourcing)
    
    # 7. Scenario Plan
    scenario_options = FORM_OPTIONS.get('scenario_plan', ["-- Select an Option --", "Direct Backfill", "Split Position/New Position"])
    scenario_plan = st.selectbox("Scenario Plan:", scenario_options, index=scenario_options.index(plan_details.get("scenario_plan")) if plan_details.get("scenario_plan") in scenario_options else 0)
    
    # 8. Type of Role (optional)
    role_type_options = FORM_OPTIONS.get('role_type', ["Not Applicable", "Succession Plan", "External"])
    role_type = st.selectbox("Type of Role (optional):", role_type_options, index=role_type_options.index(plan_details.get("role_type")) if plan_details.get("role_type") in role_type_options else 0)
    
    # New Position Title (conditional)
    new_position_title = ""
    if scenario_plan == 'Split Position/New Position':
        new_position_title = st.text_input("New Position Title:", value=plan_details.get("new_position_title", ""))

    # Custom Submit/Cancel buttons - always visible
    col1, col2 = st.columns(2)
    with col1:
        button_label = "Update Plan" if is_editing else "Save Plan"
        if st.button(button_label, type="primary", use_container_width=True, key=f"inc_submit_{person['EMPLOYEE_ID']}_{is_editing}"):
            errors = []
            if critical_role is None: errors.append("Please select if this is a Critical Role.")
            if not responsibilities: errors.append("Please enter Role Responsibilities.")
            if not top_skills: errors.append("Please select exactly 3 Top Leadership Skills.")
            elif len(top_skills) != 3: errors.append("Please select exactly 3 Top Leadership Skills.")
            if top_ple == "-- Select an Option --": errors.append("Please select a Top Demonstrated People Leader Expectation.")
            if not sourcing_strategy: errors.append("Please select at least one Talent Sourcing Strategy.")
            if scenario_plan == "-- Select an Option --": errors.append("Please select a Scenario Plan.")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                updated_plan = {
                    "critical_role": True if critical_role == "Yes" else False,
                    "responsibilities": responsibilities,
                    "top_skills": top_skills,
                    "top_ple": top_ple,
                    "contract_end_date": contract_end_date.strftime("%Y-%m-%d") if contract_end_date else None,
                    "sourcing_strategy": sourcing_strategy,  # Now stores as list
                    "role_type": role_type if role_type != "Not Applicable" else None,
                    "scenario_plan": scenario_plan,
                    "new_position_title": new_position_title if scenario_plan == 'Split Position/New Position' else None
                }
                st.session_state.app_data['incumbent'] = {"metadata": person, "plan_details": updated_plan}
                
                # Clean up session state
                if contract_date_key in st.session_state:
                    del st.session_state[contract_date_key]
                
                st.session_state.selected_person = None
                st.session_state.editing_incumbent = False
                st.success("Incumbent plan saved!")
                st.rerun()
    
    with col2:
        if st.button("Cancel", use_container_width=True, key=f"inc_cancel_{person['EMPLOYEE_ID']}_{is_editing}"):
            # Clean up session state
            if contract_date_key in st.session_state:
                del st.session_state[contract_date_key]
            
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

    # Custom form without st.form for dynamic behavior
    # 1. Contract End Date (optional) with clear option
    contract_end_date_str = assessment.get("contract_end_date")
    contract_end_date_val = datetime.datetime.strptime(contract_end_date_str, "%Y-%m-%d").date() if contract_end_date_str else None
    
    # Use session state to manage contract date clearing
    contract_date_key = f"contract_date_{person['EMPLOYEE_ID']}_{is_editing}"
    if contract_date_key not in st.session_state:
        st.session_state[contract_date_key] = contract_end_date_val
    
    col_date, col_clear = st.columns([4, 1])
    with col_date:
        contract_end_date = st.date_input("Contract End Date (optional):", value=st.session_state[contract_date_key], key=f"date_input_{contract_date_key}")
        # Update session state when date changes
        st.session_state[contract_date_key] = contract_end_date
    
    with col_clear:
        st.write("")  # Add some spacing
        if st.button("✕", help="Clear contract end date", key=f"clear_date_{contract_date_key}"):
            st.session_state[contract_date_key] = None
            st.rerun()
    
    # Use the session state value for the actual contract date
    contract_end_date = st.session_state[contract_date_key]
    
    # 2. Readiness Level
    readiness_options = FORM_OPTIONS.get('readiness_level', ["-- Select an Option --", "Ready Now", "Ready Future"])
    readiness = st.selectbox("Readiness Level:", readiness_options, index=readiness_options.index(assessment.get("readiness")) if assessment.get("readiness") in readiness_options else 0)
    
    # 3. Future Readiness Timing (optional) - Dynamic based on readiness
    future_readiness_timing = None
    if readiness == "Ready Future":
        timing_options = FORM_OPTIONS.get('future_readiness_timing', ["-- Select an Option --", "+1 to < 2 years", "+2 to < 3 years", "+3 to < 5 years"])
        # Only preserve previous timing if readiness was already "Ready Future"
        previous_timing = assessment.get("future_readiness_timing") if assessment.get("readiness") == "Ready Future" else "-- Select an Option --"
        timing_index = timing_options.index(previous_timing) if previous_timing in timing_options else 0
        future_readiness_timing = st.selectbox("Future Readiness Timing (optional):", timing_options, index=timing_index)
    
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
    
    top_skills = st.multiselect("Top Leadership Skills (select three):", SKILLS_LIST, default=valid_default_skills, max_selections=3)
    
    # 7. Development Focus & Opportunities
    development_focus = st.text_area("Development Focus & Opportunities:", value=assessment.get("development_focus", ""))
    
    # 8. Talent Development Actions
    talent_actions = st.text_area("Talent Development Actions:", value=assessment.get("talent_actions", ""))

    # Custom Submit/Cancel buttons
    col1, col2 = st.columns(2)
    with col1:
        button_label = "Update Successor" if is_editing else "Add Successor"
        if st.button(button_label, type="primary", use_container_width=True, key=f"submit_{person['EMPLOYEE_ID']}_{is_editing}"):
            errors = []
            if readiness == "-- Select an Option --": errors.append("Please select a Readiness Level.")
            if not strengths: errors.append("Please enter Successor Strengths.")
            if not top_skills: errors.append("Please select exactly 3 Top Leadership Skills for the Successor.")
            elif len(top_skills) != 3: errors.append("Please select exactly 3 Top Leadership Skills for the Successor.")
            if top_ple == "-- Select an Option --": errors.append("Please select a Top Demonstrated People Leader Expectation for the Successor.")
            if not development_focus: errors.append("Please enter Development Focus & Opportunities.")
            if not talent_actions: errors.append("Please enter Talent Development Actions.")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                successor_data = {
                    "readiness": readiness,
                    "future_readiness_timing": future_readiness_timing if readiness == "Ready Future" and future_readiness_timing != "-- Select an Option --" else None,
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
                
                # Clean up session state
                if contract_date_key in st.session_state:
                    del st.session_state[contract_date_key]
                
                st.session_state.selected_person = None
                st.session_state.editing_successor_index = None
                st.rerun()
    
    with col2:
        if st.button("Cancel", use_container_width=True, key=f"cancel_{person['EMPLOYEE_ID']}_{is_editing}"):
            # Clean up session state
            if contract_date_key in st.session_state:
                del st.session_state[contract_date_key]
            
            st.session_state.selected_person = None
            st.session_state.editing_successor_index = None
            st.rerun()
