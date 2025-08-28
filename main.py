"""
Main app - exact copy of app_final.py but with modular imports
"""

import streamlit as st
import pandas as pd
import sqlite3
import json
import random
from streamlit.components.v1 import html
import datetime
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import io

# Import from modules
from config.loader import SKILLS_LIST, PLE_LIST, CONFIG
from database.backend_manager import (
    search_incumbents, search_successors, save_succession_plan,
    get_user_access, filter_incumbents_by_access, 
    can_user_search, can_user_submit, can_user_approve,
    get_all_incumbents_in_segments, get_employee_planning_dashboard,
    get_latest_incumbent_values
)
from database.operations import search_employees  # Keep this for backward compatibility
from database.backend_manager import (
    search_incumbents, search_successors, save_succession_plan,
    get_user_access, filter_incumbents_by_access, 
    get_all_incumbents_in_segments, get_employee_planning_dashboard,
    approve_submission, request_edits, reopen_approved_plan,
    get_all_test_users, get_accessible_incumbents_for_tier3,
    get_submitted_plans_for_tier1, get_tier2_submission_for_incumbent
)
from ui.components import (
    load_css, display_sidebar_summary, display_search_box, display_search_results,
    display_selected_incumbent_card, display_incumbent_form, display_successor_form
)
from ui.backend_selector import display_backend_selector, display_backend_status, show_backend_configuration_help
from utils.helpers import force_page_reload, initialize_state
from utils.pptx_repair import auto_repair_pptx
from pptx_gen.simple_text_generator import create_succession_plan_from_template

# --- Page and State Configuration ---
st.set_page_config(
    layout=CONFIG['ui']['layout'], 
    page_title=CONFIG['ui']['page_title']
)

# Initialize state and load CSS
initialize_state()
load_css()

# --- Main Application ---
st.sidebar.image(CONFIG['ui']['logo_path'], width=CONFIG['ui']['logo_width'])

# --- USER ACCESS CONTROL (Testing) ---
st.sidebar.divider()
st.sidebar.subheader("🔐 User Access (Testing)")

# Get all test users for dropdown
test_users = get_all_test_users()
if test_users:
    user_options = ["Select a test user..."] + [user['display_name'] for user in test_users]
    
    selected_user_display = st.sidebar.selectbox(
        "Select Test User:",
        options=user_options,
        key="selected_test_user"
    )
    
    # Get user access info
    current_user_access = None
    if selected_user_display != "Select a test user...":
        # Find the selected user
        selected_user = next((u for u in test_users if u['display_name'] == selected_user_display), None)
        if selected_user:
            current_user_access = get_user_access(selected_user['email'])
            
            # Display user info
            if current_user_access:
                tier = current_user_access['tier']
                st.sidebar.success(f"**Tier {tier} User**")
                
                # Compact summary
                segments = current_user_access['segments']
                employees = current_user_access['leader_employee_ids']
                
                if tier == 1:
                    st.sidebar.info(f"📍 **Segments ({len(segments)})**: {', '.join(segments[:2])}{'...' if len(segments) > 2 else ''}")
                    st.sidebar.caption("Access: All employees in segments")
                elif tier == 2:
                    st.sidebar.info(f"📍 **Segment**: {segments[0] if segments else 'None'}")
                    st.sidebar.info(f"👥 **Employees ({len(employees)})**: {len(employees)} assigned")
                else:  # tier == 3
                    st.sidebar.info(f"📍 **Segment**: {segments[0] if segments else 'None'}")
                    st.sidebar.info(f"👤 **Assigned**: {len(employees)} incumbent(s)")
                
                # Store in session state
                st.session_state.current_user_access = current_user_access
            else:
                st.sidebar.error("User access not found")
                st.session_state.current_user_access = None
    else:
        st.session_state.current_user_access = None
        st.sidebar.info("Please select a user to test access levels")
else:
    st.sidebar.error("No test users found. Run setup_user_access.py first.")
    st.session_state.current_user_access = None

display_sidebar_summary()

# Display backend selector and status in sidebar
current_backend = display_backend_selector()

# Display current backend status in sidebar
st.sidebar.divider()
with st.sidebar:
    display_backend_status()
    
    # Show configuration help if Snowflake is not properly configured
    if current_backend == 'snowflake':
        from database.backend_manager import backend_manager
        backends = backend_manager.get_available_backends()
        snowflake_info = next((b for b in backends if b['name'] == 'snowflake'), None)
        if snowflake_info and not snowflake_info['available']:
            show_backend_configuration_help()

st.title("Succession Planning Tool")

# --- EMPLOYEE PLANNING DASHBOARD ---
user_access = st.session_state.get('current_user_access')
if user_access:
    st.subheader("📊 Your Employee Planning Dashboard")
    
    # Get dashboard data
    dashboard_df = get_employee_planning_dashboard(user_access)
    
    if not dashboard_df.empty:
        # Summary metrics
        total_employees = len(dashboard_df)
        planned_employees = len(dashboard_df[dashboard_df['Planning Status'] != '⚪ Not Planned'])
        planning_percentage = (planned_employees / total_employees * 100) if total_employees > 0 else 0
        
        # Display metrics
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.metric("Total Employees", total_employees)
        with metric_col2:
            st.metric("Planned", planned_employees)
        with metric_col3:
            st.metric("Planning %", f"{planning_percentage:.1f}%")
        with metric_col4:
            avg_successors = dashboard_df[dashboard_df['Successors'] > 0]['Successors'].mean()
            st.metric("Avg Successors", f"{avg_successors:.1f}" if not pd.isna(avg_successors) else "0")
        
        # Filter options
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            # Status filter
            status_options = ['All'] + sorted(dashboard_df['Planning Status'].unique().tolist())
            selected_status = st.selectbox("Filter by Status:", status_options)
        
        with filter_col2:
            # Segment filter (for Tier 1 users)
            if user_access['tier'] == 1:
                segment_options = ['All'] + sorted(dashboard_df['Segment'].unique().tolist())
                selected_segment = st.selectbox("Filter by Segment:", segment_options)
            else:
                selected_segment = 'All'
        
        with filter_col3:
            # Search by name
            name_search = st.text_input("Search by Name:", placeholder="Enter first or last name...")
        
        # Apply filters
        filtered_df = dashboard_df.copy()
        
        if selected_status != 'All':
            filtered_df = filtered_df[filtered_df['Planning Status'] == selected_status]
        
        if selected_segment != 'All':
            filtered_df = filtered_df[filtered_df['Segment'] == selected_segment]
        
        if name_search:
            name_mask = (
                filtered_df['First Name'].str.contains(name_search, case=False, na=False) |
                filtered_df['Last Name'].str.contains(name_search, case=False, na=False)
            )
            filtered_df = filtered_df[name_mask]
        
        # Display filtered results count
        if len(filtered_df) != len(dashboard_df):
            st.info(f"Showing {len(filtered_df)} of {len(dashboard_df)} employees")
        
        # Display the dataframe
        if not filtered_df.empty:
            # Configure column display
            column_config = {
                "Employee ID": st.column_config.TextColumn("Employee ID", width="small"),
                "First Name": st.column_config.TextColumn("First Name", width="medium"),
                "Last Name": st.column_config.TextColumn("Last Name", width="medium"),
                "Position": st.column_config.TextColumn("Position", width="large"),
                "Planning Status": st.column_config.TextColumn("Status", width="medium"),
                "Successors": st.column_config.NumberColumn("Successors", width="small"),
                "Segment": st.column_config.TextColumn("Segment", width="large"),
                "Leader": st.column_config.TextColumn("Leader", width="medium"),
                "Last Updated By": st.column_config.TextColumn("Updated By", width="small"),
                "Tier": st.column_config.NumberColumn("Tier", width="small")
            }
            
            # Show dataframe with click selection
            selected_rows = st.dataframe(
                filtered_df,
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Handle row selection
            if selected_rows and len(selected_rows.selection.rows) > 0:
                selected_idx = selected_rows.selection.rows[0]
                selected_employee = filtered_df.iloc[selected_idx]
                
                st.info(f"Selected: {selected_employee['First Name']} {selected_employee['Last Name']} - {selected_employee['Position']}")
                
                # Quick action buttons
                action_col1, action_col2, action_col3 = st.columns(3)
                
                with action_col1:
                    # Change button text based on user tier
                    button_text = "👁️ View Plan" if user_access['tier'] == 1 else "📝 Create/Edit Plan"
                    if st.button(button_text, use_container_width=True):
                        # Clear any existing plan data when selecting new person
                        st.session_state.app_data['incumbent'] = None
                        st.session_state.app_data['successors'] = []
                        
                        # Create a person object for the selected employee
                        selected_person = {
                            'EMPLOYEE_ID': selected_employee['Employee ID'],
                            'PREFERRED_FIRST_NAME': selected_employee['First Name'],
                            'PREFERRED_LAST_NAME': selected_employee['Last Name'],
                            'POSITION_TITLE': selected_employee['Position'],
                            'MANAGEMENT_LEVEL': selected_employee['Mgmt Level'],
                            'JOB_LEVEL': selected_employee['Job Level'],
                            'SEGMENT_HIER_LEVEL_2_NAME': selected_employee['Segment'],
                            'LEADER_NAME': selected_employee['Leader'],
                            'HR_SEGMENT': selected_employee['Segment']
                        }
                        
                        st.session_state.selected_person = selected_person
                        st.session_state.current_search_context = 'incumbent'  # Dataframe selection is incumbent context
                        st.success(f"Selected {selected_employee['First Name']} {selected_employee['Last Name']} for planning!")
                        st.rerun()
                
                with action_col2:
                    if selected_employee['Planning Status'] != '⚪ Not Planned':
                        if st.button("👁️ View Existing Plan", use_container_width=True):
                            # Load existing plan data
                            employee_id = selected_employee['Employee ID']
                            
                            # Get incumbent data
                            incumbent_values = get_latest_incumbent_values(employee_id)
                            if incumbent_values:
                                # Create incumbent metadata
                                incumbent_metadata = {
                                    'EMPLOYEE_ID': employee_id,
                                    'PREFERRED_FIRST_NAME': selected_employee['First Name'],
                                    'PREFERRED_LAST_NAME': selected_employee['Last Name'],
                                    'POSITION_TITLE': selected_employee['Position'],
                                    'MANAGEMENT_LEVEL': selected_employee['Mgmt Level'],
                                    'JOB_LEVEL': selected_employee['Job Level'],
                                    'SEGMENT_HIER_LEVEL_2_NAME': selected_employee['Segment'],
                                    'HR_SEGMENT': selected_employee['Segment']
                                }
                                
                                # Load into session state
                                st.session_state.app_data['incumbent'] = {
                                    "metadata": incumbent_metadata,
                                    "plan_details": incumbent_values
                                }
                                
                                # Get existing successors
                                from database.operations import get_existing_successors_for_incumbent
                                existing_successors = get_existing_successors_for_incumbent(employee_id)
                                if existing_successors:
                                    st.session_state.app_data['successors'] = existing_successors
                                else:
                                    st.session_state.app_data['successors'] = []
                                
                                # For Tier 1 users, set review mode when viewing existing plans
                                if user_access and user_access['tier'] == 1:
                                    # Get the submission data for review mode
                                    tier2_submission = get_tier2_submission_for_incumbent(employee_id, user_access)
                                    if tier2_submission:
                                        st.session_state.reviewing_submission = tier2_submission
                                
                                st.success(f"✅ Loaded existing plan for {selected_employee['First Name']} {selected_employee['Last Name']}")
                                st.rerun()
                            else:
                                st.error("No existing plan data found for this employee.")
                
                with action_col3:
                    if selected_employee['Planning Status'] in ['🔵 Submitted', '🔴 Needs Edit'] and user_access['tier'] == 1:
                        if st.button("📋 Review Submission", use_container_width=True):
                            # Load the submission for review
                            tier2_submission = get_tier2_submission_for_incumbent(selected_employee['Employee ID'], user_access)
                            if tier2_submission:
                                st.session_state.app_data['incumbent'] = tier2_submission['incumbent']
                                st.session_state.app_data['successors'] = tier2_submission['successors']
                                st.session_state.reviewing_submission = tier2_submission['submission_info']
                                st.success("Submission loaded for review!")
                                st.rerun()
                    elif selected_employee['Planning Status'] == '🟢 Approved 🔄' and user_access['tier'] == 1:
                        if st.button("🔄 Reopen for Editing", use_container_width=True):
                            if reopen_approved_plan(selected_employee['Employee ID'], user_access):
                                st.success("✅ Plan reopened for editing!")
                                st.rerun()
                            else:
                                st.error("Failed to reopen plan")
        else:
            st.warning("No employees match your current filters.")
    else:
        st.warning("No employees found for your access level.")

# --- DIALOG MANAGEMENT ---
# Check if a new incumbent is being selected (different from current incumbent)
# Only clear when selecting from incumbent search, not successor search
if (st.session_state.selected_person and 
    st.session_state.app_data['incumbent'] and 
    st.session_state.selected_person['EMPLOYEE_ID'] != st.session_state.app_data['incumbent']['metadata']['EMPLOYEE_ID'] and
    st.session_state.get('current_search_context') == 'incumbent'):
    # Clear existing incumbent data when selecting a different person from incumbent search
    st.session_state.app_data['incumbent'] = None
    st.session_state.app_data['successors'] = []
    st.session_state.editing_incumbent = False
    st.session_state.editing_successor_index = None

# Determine which dialog should be open (only one at a time)
# Don't show edit dialog for Tier 1 users (they should only review)
is_tier1_review_mode = user_access and user_access['tier'] == 1
show_incumbent_dialog = (st.session_state.get("editing_incumbent") or (st.session_state.selected_person and not st.session_state.app_data['incumbent'])) and not is_tier1_review_mode
show_successor_dialog = (st.session_state.selected_person and st.session_state.app_data['incumbent']) or st.session_state.editing_successor_index is not None

# If both would be true, prioritize incumbent
if show_incumbent_dialog and show_successor_dialog:
    show_successor_dialog = False

# --- INCUMBENT SECTION ---
if show_incumbent_dialog:
    display_incumbent_form()
elif st.session_state.app_data['incumbent']:
    display_selected_incumbent_card(st.session_state.app_data['incumbent'])
else:
    # Always clear selected_person when we're in the search state to ensure search box shows
    if st.session_state.selected_person:
        st.session_state.selected_person = None
    
    # Check user access
    user_access = st.session_state.get('current_user_access')
    
    if not user_access:
        st.warning("⚠️ Please select a test user from the sidebar to continue.")
        st.stop()
    else:
        # Handle Tier 3 users (no search, only assigned incumbents)
        if user_access['tier'] == 3:
            st.info("As a Tier 3 user, you can only work with your assigned incumbents.")
            
            accessible_incumbents = get_accessible_incumbents_for_tier3(user_access)
            if accessible_incumbents:
                st.subheader("Your Assigned Incumbents")
                display_search_results(accessible_incumbents, "incumbent")
            else:
                st.warning("No incumbents have been assigned to you.")
        
        # Handle Tier 1 and 2 users (can search with filtering)
        elif can_user_search(user_access):
            # Show submitted plans for Tier 1 users (from Tier 2 and 3 only)
            if user_access['tier'] == 1:
                submitted_plans = get_submitted_plans_for_tier1(user_access)
                if submitted_plans:
                    st.info("📋 **Submissions Awaiting Your Review** (from Tier 2 and Tier 3 users)")
                    
                    for plan in submitted_plans[:3]:  # Show top 3
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            st.write(f"**{plan['INCUMBENT_FIRST_NAME']} {plan['INCUMBENT_LAST_NAME']}**")
                            st.caption(f"Segment: {plan['INCUMBENT_SEGMENT']}")
                        with col2:
                            st.caption(f"Submitted by: {plan['SUBMITTED_BY']} (Tier {plan['USER_TIER']})")
                            st.caption(f"Successors: {plan['successor_count']}")
                        with col3:
                            if st.button("Review", key=f"review_{plan['INCUMBENT_EMPLOYEE_ID']}_{plan['SUBMITTED_BY']}", use_container_width=True):
                                # Load the Tier 2/3 submission for review
                                tier23_submission = get_tier2_submission_for_incumbent(plan['INCUMBENT_EMPLOYEE_ID'], user_access)
                                if tier23_submission:
                                    # Populate session state with Tier 2/3 data
                                    st.session_state.app_data['incumbent'] = tier23_submission['incumbent']
                                    st.session_state.app_data['successors'] = tier23_submission['successors']
                                    st.session_state.reviewing_submission = tier23_submission['submission_info']
                                    st.success(f"Tier {tier23_submission['submission_info']['user_tier']} submission loaded for review!")
                                    st.rerun()
                    
                    if len(submitted_plans) > 3:
                        st.caption(f"... and {len(submitted_plans) - 3} more submitted plans")
                    
                    st.divider()
            
            # Browse all option for Tier 1
            if user_access['tier'] == 1:
                if st.button("📋 Browse All Employees in My Segments", use_container_width=True):
                    st.session_state.show_all_incumbents = True
                    st.rerun()
            
            # Show all incumbents table if requested
            if st.session_state.get('show_all_incumbents') and user_access['tier'] == 1:
                st.subheader("📋 All Employees in Your Segments")
                
                all_incumbents = get_all_incumbents_in_segments(user_access)
                if all_incumbents:
                    # Convert to DataFrame for better display
                    import pandas as pd
                    df = pd.DataFrame(all_incumbents)
                    
                    # Format the data for display
                    display_df = df[['PREFERRED_FIRST_NAME', 'PREFERRED_LAST_NAME', 'POSITION_TITLE', 
                                   'MANAGEMENT_LEVEL', 'SEGMENT_HIER_LEVEL_2_NAME', 'EMPLOYEE_ID']].copy()
                    display_df.columns = ['First Name', 'Last Name', 'Position', 'Mgmt Level', 'Segment', 'Employee ID']
                    
                    st.info(f"Showing {len(display_df)} employees in your segments")
                
                # Configure column display
                column_config = {
                    "First Name": st.column_config.TextColumn("First Name", width="medium"),
                    "Last Name": st.column_config.TextColumn("Last Name", width="medium"),
                    "Position": st.column_config.TextColumn("Position", width="large"),
                    "Mgmt Level": st.column_config.TextColumn("Level", width="medium"),
                    "Segment": st.column_config.TextColumn("Segment", width="large"),
                    "Employee ID": st.column_config.TextColumn("Employee ID", width="small")
                }
                
                # Show dataframe with click selection
                selected_rows = st.dataframe(
                    display_df,
                    column_config=column_config,
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row"
                )
                
                # Handle row selection
                if selected_rows and len(selected_rows.selection.rows) > 0:
                    selected_idx = selected_rows.selection.rows[0]
                    selected_employee = display_df.iloc[selected_idx]
                    
                    st.success(f"Selected: {selected_employee['First Name']} {selected_employee['Last Name']} - {selected_employee['Position']}")
                    
                    # Quick action buttons
                    action_col1, action_col2 = st.columns(2)
                    
                    with action_col1:
                        if st.button("📝 Create Plan for This Employee", use_container_width=True):
                            # Find the full employee data
                            selected_employee_data = next(
                                (emp for emp in all_incumbents if emp['EMPLOYEE_ID'] == selected_employee['Employee ID']), 
                                None
                            )
                            
                            if selected_employee_data:
                                st.session_state.selected_person = selected_employee_data
                                st.session_state.current_search_context = 'incumbent'  # Dataframe selection is incumbent context
                                st.session_state.show_all_incumbents = False  # Hide the table
                                st.success(f"Selected {selected_employee['First Name']} {selected_employee['Last Name']} for planning!")
                                st.rerun()
                    
                    with action_col2:
                        if st.button("🔍 Search Instead", use_container_width=True):
                            st.session_state.show_all_incumbents = False
                            st.rerun()
                else:
                    st.warning("No employees found in your segments.")
            
            # Clear browse mode for non-Tier 1 users
            elif st.session_state.get('show_all_incumbents'):
                st.session_state.show_all_incumbents = False
                st.rerun()
        
        # Only show search if not browsing all
        elif not st.session_state.get('show_all_incumbents'):
            st.info("Search for the employee you want to create a succession plan for.")
            display_search_box("incumbent")
            if st.session_state.search_term:
                search_type = st.session_state.get('current_search_type', 'last_name')
                results = search_incumbents(st.session_state.search_term, search_type)
                
                # Filter results based on user access
                filtered_results = filter_incumbents_by_access(results, user_access)
                
                if filtered_results:
                    st.caption(f"Showing {len(filtered_results)} of {len(results)} results (filtered by your access level)")
                    display_search_results(filtered_results, "incumbent")
                elif results:
                    st.warning(f"Found {len(results)} employees, but none are in your accessible segments/employees.")
                else:
                    st.warning("No employees found.")
        else:
            st.error("You do not have search permissions.")

# --- SUCCESSORS SECTION ---
if st.session_state.app_data['successors'] or st.session_state.app_data['incumbent']:
    st.divider()
    
    if show_successor_dialog:
        display_successor_form()
    else:
        # Show added successors in columns
        if st.session_state.app_data['successors']:
            st.subheader("👥 Successors")
            successors = st.session_state.app_data['successors']
            
            # Create rows of up to 3 columns each with consistent thirds width
            for row_start in range(0, len(successors), 3):
                row_successors = successors[row_start:row_start + 3]
                cols = st.columns(3)  # Always use 3 equal columns
                
                for i, succ in enumerate(row_successors):
                    col = cols[i]  # Use the appropriate column
                    actual_index = row_start + i
                    name = f"{succ['metadata']['PREFERRED_FIRST_NAME']} {succ['metadata']['PREFERRED_LAST_NAME']}"
                    readiness = succ['assessment']['readiness']
                    assessment = succ['assessment']
                    
                    with col:
                        with st.container(border=True):
                            st.image(f"https://rostr.disney.com/api/v2/people/{succ['metadata']['EMPLOYEE_ID']}/avatars/thumbnail_large?locale=en&token=abc4fc58f30914f6d99faa8a31f4d44c", width=80)
                            st.markdown(f"**{name}**")
                            st.caption(f"Readiness: {readiness}")
                            
                            with st.expander("View Plan Details"):
                                # 1. Contract End Date (optional)
                                if assessment.get('contract_end_date'):
                                    st.markdown(f"**Contract End Date:** {assessment.get('contract_end_date')}")
                                
                                # 2. Readiness Level
                                st.markdown(f"**Readiness Level:** {assessment.get('readiness', 'Not specified')}")
                                
                                # 3. Future Readiness Timing (optional)
                                if assessment.get('future_readiness_timing'):
                                    st.markdown(f"**Future Readiness Timing:** {assessment.get('future_readiness_timing')}")
                                
                                # 4. Strengths
                                st.markdown(f"**Strengths:**")
                                st.info(assessment.get('strengths', 'Not specified.'))
                                
                                # 5. Top Demonstrated People Leader Expectations
                                st.markdown(f"**Top Demonstrated People Leader Expectations:**")
                                st.info(assessment.get('top_ple', 'Not specified.'))
                                
                                # 6. Top Leadership Skills
                                st.markdown(f"**Top Leadership Skills:**")
                                st.info(", ".join(assessment.get('top_skills', ['Not specified.'])))
                                
                                # 7. Development Focus & Opportunities
                                st.markdown(f"**Development Focus & Opportunities:**")
                                st.info(assessment.get('development_focus', 'Not specified.'))
                                
                                # 8. Talent Development Actions
                                st.markdown(f"**Talent Development Actions:**")
                                st.info(assessment.get('talent_actions', 'Not specified.'))
                            
                            c1, c2 = st.columns(2)
                            # Only show edit/remove buttons if NOT in review mode
                            if not (st.session_state.get('reviewing_submission') and user_access and user_access['tier'] == 1):
                                with c1:
                                    if st.button("Edit", key=f"edit_succ_{actual_index}", use_container_width=True):
                                        st.session_state.editing_successor_index = actual_index
                                        st.rerun()
                                with c2:
                                    if st.button("Remove", key=f"remove_succ_{actual_index}", help="Remove this successor from the plan", use_container_width=True):
                                        # Mark successor as removed in database if incumbent and plan details exist
                                        if st.session_state.app_data['incumbent'] and st.session_state.app_data['incumbent'].get('plan_details'):
                                            from database.operations import mark_successor_as_removed
                                            mark_successor_as_removed(
                                                st.session_state.app_data['incumbent']['metadata'],
                                                succ['metadata'],
                                                st.session_state.app_data['incumbent']['plan_details'],
                                                succ['assessment']
                                            )
                                        
                                        # Remove from session state
                                        st.session_state.app_data['successors'].pop(actual_index)
                                        st.success(f"{name} has been removed from the succession plan.")
                                        st.rerun()
        
        # Search for new successors - only show if incumbent exists, not editing incumbent, and not in review mode
        if (st.session_state.app_data['incumbent'] and 
            not st.session_state.get("editing_incumbent") and 
            not (st.session_state.get('reviewing_submission') and user_access and user_access['tier'] == 1)):
            st.info("Search for potential successors to add to the plan.")
            display_search_box("successor")
            if st.session_state.search_term:
                search_type = st.session_state.get('current_search_type', 'last_name')
                results = search_successors(st.session_state.search_term, search_type)
                if results:
                    display_search_results(results, "successor")
                else:
                    st.warning("No employees found.")

# --- SUBMIT SECTION - EXACT COPY FROM app_final.py ---
if st.session_state.app_data['incumbent'] and st.session_state.app_data['successors']:
    # Only clear selected_person if we're not actively showing a successor form
    if st.session_state.selected_person and not show_successor_dialog:
        st.session_state.selected_person = None
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    user_access = st.session_state.get('current_user_access')
    reviewing_submission = st.session_state.get('reviewing_submission')
    
    # Show approval controls if reviewing a Tier 2/3 submission
    if reviewing_submission and user_access and user_access['tier'] == 1:
        submitter_tier = reviewing_submission.get('submission_info', {}).get('user_tier', reviewing_submission.get('user_tier', 'Unknown'))
        submitted_by = reviewing_submission.get('submission_info', {}).get('submitted_by', reviewing_submission.get('submitted_by', 'Unknown'))
        st.info(f"📋 **Reviewing submission from {submitted_by} (Tier {submitter_tier})**")
        st.warning("🔒 **Review Mode**: This is read-only. You can approve or send back for editing.")
        
        approval_col1, approval_col2, approval_col3 = st.columns(3)
        
        with approval_col1:
            if st.button("✅ Approve Submission", type="primary", use_container_width=True):
                incumbent_id = st.session_state.app_data['incumbent']['metadata']['EMPLOYEE_ID']
                if approve_submission(incumbent_id, user_access):
                    st.success("✅ Submission approved!")
                    st.session_state.reviewing_submission = None
                    st.session_state.app_data['incumbent'] = None
                    st.session_state.app_data['successors'] = []
                    st.rerun()
                else:
                    st.error("Failed to approve submission")
        
        with approval_col2:
            if st.button("❌ Send Back for Editing", use_container_width=True):
                incumbent_id = st.session_state.app_data['incumbent']['metadata']['EMPLOYEE_ID']
                if request_edits(incumbent_id, user_access):
                    st.success("✅ Sent back for editing!")
                    st.session_state.reviewing_submission = None
                    st.session_state.app_data['incumbent'] = None
                    st.session_state.app_data['successors'] = []
                    st.rerun()
                else:
                    st.error("Failed to send back for editing")
        
        with approval_col3:
            if st.button("🚪 Exit Review", use_container_width=True):
                st.session_state.reviewing_submission = None
                st.session_state.app_data['incumbent'] = None
                st.session_state.app_data['successors'] = []
                st.rerun()
        
        st.divider()
        
        # Continue to show the normal plan interface below the approval buttons
        # The edit/remove buttons and successor search are already hidden by the conditions above
    
    # Regular save controls (only show if not in review mode)
    elif st.session_state.app_data['incumbent'] and st.session_state.app_data['successors']:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Draft", use_container_width=True):
                if not user_access:
                    st.error("Please select a user first")
                elif can_user_submit(user_access):
                    incumbent = st.session_state.app_data['incumbent']
                    successors = st.session_state.app_data['successors']
                    success_count = 0
                    saved_record_ids = []
                    
                    for successor in successors:
                        record_id = save_succession_plan(
                            incumbent['metadata'], 
                            successor['metadata'], 
                            incumbent['plan_details'], 
                            successor['assessment'],
                            user_access=user_access,
                            status='saved'
                        )
                        if record_id:
                            success_count += 1
                            saved_record_ids.append(record_id)
                    
                    if success_count == len(successors):
                        st.success(f"✅ Saved {success_count} succession plan record(s) as draft!")
                        st.info(f"Record IDs: {', '.join([rid[:8] + '...' for rid in saved_record_ids[:3]])}{'...' if len(saved_record_ids) > 3 else ''}")
                    else:
                        st.error(f"Only {success_count} out of {len(successors)} records were saved successfully.")
                else:
                    st.error("You do not have permission to save succession plans")
        
        with col2:
            # Different submit buttons based on tier
            if user_access['tier'] == 1:
                # Tier 1: Just "Submit" (they can approve their own)
                if st.button("📤 Submit", type="primary", use_container_width=True):
                    if not user_access:
                        st.error("Please select a user first")
                    elif can_user_submit(user_access):
                        incumbent = st.session_state.app_data['incumbent']
                        successors = st.session_state.app_data['successors']
                        success_count = 0
                        saved_record_ids = []
                        
                        for successor in successors:
                            record_id = save_succession_plan(
                                incumbent['metadata'], 
                                successor['metadata'], 
                                incumbent['plan_details'], 
                                successor['assessment'],
                                user_access=user_access,
                                status='approved'  # Tier 1 submissions are auto-approved
                            )
                            if record_id:
                                success_count += 1
                                saved_record_ids.append(record_id)
                        
                        if success_count == len(successors):
                            st.success(f"✅ Submitted {success_count} succession plan record(s)!")
                            st.info("As a Tier 1 user, your submission is automatically approved.")
                        else:
                            st.error(f"Only {success_count} out of {len(successors)} records were submitted successfully.")
                    else:
                        st.error("You do not have permission to submit succession plans")
            
            elif user_access['tier'] == 2:
                # Tier 2: "Submit for Review" (needs Tier 1 approval)
                if st.button("📤 Submit for Review", type="primary", use_container_width=True):
                    if not user_access:
                        st.error("Please select a user first")
                    elif can_user_submit(user_access):
                        incumbent = st.session_state.app_data['incumbent']
                        successors = st.session_state.app_data['successors']
                        success_count = 0
                        saved_record_ids = []
                        
                        for successor in successors:
                            record_id = save_succession_plan(
                            incumbent['metadata'], 
                            successor['metadata'], 
                            incumbent['plan_details'], 
                            successor['assessment'],
                            user_access=user_access,
                            status='submitted'  # Tier 2 needs approval
                        )
                            if record_id:
                                success_count += 1
                                saved_record_ids.append(record_id)
                    
                    if success_count == len(successors):
                        st.success(f"✅ Submitted {success_count} succession plan record(s) for Tier 1 review!")
                        st.info("Your submission will be reviewed by a Tier 1 user.")
                    else:
                        st.error(f"Only {success_count} out of {len(successors)} records were submitted successfully.")
                else:
                    st.error("You do not have permission to submit succession plans")
            
            elif user_access['tier'] == 3:
                # Tier 3: Just "Submit" (fire and forget to Tier 1)
                if st.button("📤 Submit", type="primary", use_container_width=True):
                    if not user_access:
                        st.error("Please select a user first")
                    elif can_user_submit(user_access):
                        incumbent = st.session_state.app_data['incumbent']
                        successors = st.session_state.app_data['successors']
                        success_count = 0
                        saved_record_ids = []
                        
                        for successor in successors:
                            record_id = save_succession_plan(
                            incumbent['metadata'], 
                            successor['metadata'], 
                            incumbent['plan_details'], 
                            successor['assessment'],
                            user_access=user_access,
                            status='submitted'  # Tier 3 goes to Tier 1 for review
                        )
                        if record_id:
                            success_count += 1
                            saved_record_ids.append(record_id)
                    
                    if success_count == len(successors):
                        st.success(f"✅ Submitted {success_count} succession plan record(s)!")
                        st.info("Your submission has been sent for review.")
                    else:
                        st.error(f"Only {success_count} out of {len(successors)} records were submitted successfully.")
                else:
                    st.error("You do not have permission to submit succession plans")
            
            else:
                st.error("Invalid user tier")
        
        with col3:
            # PowerPoint download with session state approach
            if 'pptx_data' not in st.session_state:
                st.session_state.pptx_data = None
            
            # Generate PowerPoint button (includes automatic repair)
            if st.button("📊 Generate PowerPoint", use_container_width=True, key="generate_pptx"):
                try:
                    with st.spinner("Generating PowerPoint..."):
                        # Generate the PowerPoint
                        pptx_buffer = create_succession_plan_from_template(
                            st.session_state.app_data['incumbent'],
                            st.session_state.app_data['successors']
                        )
                        
                        # Always run additional repair step for extra cleaning
                        with st.spinner("Applying final repairs and optimizations..."):
                            import io
                            # Apply temp_file repair method for extra thorough cleaning
                            final_buffer = auto_repair_pptx(pptx_buffer, method="temp_file")
                            st.session_state.pptx_data = final_buffer.getvalue()
                        
                        st.success("PowerPoint generated and optimized! Download button below.")
                        
                except Exception as e:
                    st.error(f"Error creating PowerPoint: {e}")
        
        # Download button (only shows if data exists)
        if st.session_state.pptx_data:
            incumbent_name = st.session_state.app_data['incumbent']['metadata']['PREFERRED_LAST_NAME']
            st.download_button(
                label="📥 Download PowerPoint",
                data=st.session_state.pptx_data,
                file_name=f"succession_plan_{incumbent_name}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
                key="download_pptx_file"
            )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start New Plan (Reload App)", use_container_width=True):
            force_page_reload()
    with col2:
        # For Tier 1 users, show PowerPoint download instead of JSON
        if user_access and user_access['tier'] == 1:
            # PowerPoint download for Tier 1
            if 'pptx_data' not in st.session_state:
                st.session_state.pptx_data = None
            
            # Generate PowerPoint button for Tier 1
            if st.button("📊 Generate PowerPoint", use_container_width=True, key="generate_pptx_tier1"):
                try:
                    with st.spinner("Generating PowerPoint..."):
                        # Generate the PowerPoint
                        pptx_buffer = create_succession_plan_from_template(
                            st.session_state.app_data['incumbent'],
                            st.session_state.app_data['successors']
                        )
                        
                        # Always run additional repair step for extra cleaning
                        with st.spinner("Applying final repairs and optimizations..."):
                            import io
                            # Apply temp_file repair method for extra thorough cleaning
                            final_buffer = auto_repair_pptx(pptx_buffer, method="temp_file")
                            st.session_state.pptx_data = final_buffer.getvalue()
                        
                        st.success("PowerPoint generated and optimized! Download button below.")
                        
                except Exception as e:
                    st.error(f"Error creating PowerPoint: {e}")
            
            # PowerPoint download button for Tier 1
            if st.session_state.pptx_data:
                st.download_button(
                    label="📊 Download PowerPoint",
                    data=st.session_state.pptx_data,
                    file_name=f"succession_plan_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True,
                    key="download_pptx_tier1"
                )
        else:
            # Keep JSON option for other tiers
            final_json_string = json.dumps(st.session_state.app_data, indent=4, default=str)
            st.download_button(
                label="📄 Download as JSON", 
                data=final_json_string, 
                file_name="succession_plan.json", 
                mime="application/json",
                use_container_width=True
            )
