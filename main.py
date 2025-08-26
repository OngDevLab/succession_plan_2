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
from database.backend_manager import search_incumbents, search_successors, save_succession_plan
from database.operations import search_employees  # Keep this for backward compatibility
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
display_sidebar_summary()

# Display backend selector in sidebar
current_backend = display_backend_selector()

st.title("🏛️ Succession Planning Tool v4 - Functions")

# Display current backend status
display_backend_status()

# Show configuration help if Snowflake is not properly configured
if current_backend == 'snowflake':
    from database.backend_manager import backend_manager
    backends = backend_manager.get_available_backends()
    snowflake_info = next((b for b in backends if b['name'] == 'snowflake'), None)
    if snowflake_info and not snowflake_info['available']:
        show_backend_configuration_help()
st.caption("🆔 Database-side UUIDv4 | 📝 ALL CAPS columns | ✨ Clean UI | 💡 Smart Prepopulation | 🔧 Function-based Modules")

# --- DIALOG MANAGEMENT ---
# Determine which dialog should be open (only one at a time)
show_incumbent_dialog = st.session_state.get("editing_incumbent") or (st.session_state.selected_person and not st.session_state.app_data['incumbent'])
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
    
    st.info("Search for the employee you want to create a succession plan for.")
    display_search_box("incumbent")
    if st.session_state.search_term:
        search_type = st.session_state.get('current_search_type', 'last_name')
        results = search_incumbents(st.session_state.search_term, search_type)
        if results:
            display_search_results(results, "incumbent")
        else:
            st.warning("No employees found.")

# --- SUCCESSORS SECTION ---
if st.session_state.app_data['successors'] or st.session_state.app_data['incumbent']:
    st.divider()
    
    if show_successor_dialog:
        display_successor_form()
    else:
        # Show added successors in columns
        if st.session_state.app_data['successors']:
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
        
        # Search for new successors - only show if incumbent exists and not editing incumbent
        if st.session_state.app_data['incumbent'] and not st.session_state.get("editing_incumbent"):
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save to Database", type="primary", use_container_width=True):
            incumbent = st.session_state.app_data['incumbent']
            successors = st.session_state.app_data['successors']
            success_count = 0
            saved_record_ids = []
            
            for successor in successors:
                record_id = save_succession_plan(
                    incumbent['metadata'], 
                    successor['metadata'], 
                    incumbent['plan_details'], 
                    successor['assessment']
                )
                if record_id:
                    success_count += 1
                    saved_record_ids.append(record_id)
            
            if success_count == len(successors):
                st.success(f"Successfully saved {success_count} succession plan record(s) to the database!")
                st.info(f"Record IDs: {', '.join([rid[:8] + '...' for rid in saved_record_ids[:3]])}{'...' if len(saved_record_ids) > 3 else ''}")
            else:
                st.error(f"Only {success_count} out of {len(successors)} records were saved successfully.")
    
    with col2:
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
        # Keep JSON option as backup
        final_json_string = json.dumps(st.session_state.app_data, indent=4, default=str)
        st.download_button(
            label="📄 Download as JSON", 
            data=final_json_string, 
            file_name="succession_plan.json", 
            mime="application/json",
            use_container_width=True
        )
