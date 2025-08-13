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
from database.operations import search_employees, save_succession_plan
from ui.components import (
    load_css, display_sidebar_summary, display_search_box, display_search_results,
    display_selected_incumbent_card, display_incumbent_form, display_successor_form
)
from utils.helpers import force_page_reload, initialize_state
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

st.title("🏛️ Succession Planning Tool v4 - Functions")
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
    st.info("Search for the employee you want to create a succession plan for.")
    display_search_box("incumbent")
    if st.session_state.search_term:
        results = search_employees(st.session_state.search_term)
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
                    name = f"{succ['metadata']['PREFERRED_NAME_FIRST_NAME']} {succ['metadata']['PREFERRED_NAME_LAST_NAME']}"
                    readiness = succ['assessment']['readiness']
                    assessment = succ['assessment']
                    
                    with col:
                        with st.container(border=True):
                            st.image(f"https://rostr.disney.com/api/v2/people/{succ['metadata']['EMPLOYEE_ID']}/avatars/thumbnail_large?locale=en&token=abc4fc58f30914f6d99faa8a31f4d44c", width=80)
                            st.markdown(f"**{name}**")
                            st.caption(f"Readiness: {readiness}")
                            
                            with st.expander("View Assessment Details"):
                                st.markdown(f"**Readiness Level:** {assessment.get('readiness', 'Not specified')}")
                                if assessment.get('future_readiness_timing'):
                                    st.markdown(f"**Future Timing:** {assessment.get('future_readiness_timing')}")
                                st.markdown(f"**Top Demonstrated PLE:**")
                                st.info(assessment.get('top_ple', 'Not specified.'))
                                st.markdown(f"**Top Skills:**")
                                st.info(", ".join(assessment.get('top_skills', ['Not specified.'])))
                                st.markdown(f"**Strengths:**")
                                st.info(assessment.get('strengths', 'Not specified.'))
                                st.markdown(f"**Development Focus:**")
                                st.info(assessment.get('development_focus', 'Not specified.'))
                                st.markdown(f"**Talent Actions:**")
                                st.info(assessment.get('talent_actions', 'Not specified.'))
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("Edit", key=f"edit_succ_{actual_index}", use_container_width=True):
                                    st.session_state.editing_successor_index = actual_index
                                    st.rerun()
                            with c2:
                                if st.button("Change Successor", key=f"remove_succ_{actual_index}", help="Select a different successor", use_container_width=True):
                                    st.session_state.app_data['successors'].pop(actual_index)
                                    st.rerun()
        
        # Search for new successors - only show if incumbent exists and not editing incumbent
        if st.session_state.app_data['incumbent'] and not st.session_state.get("editing_incumbent"):
            st.info("Search for potential successors to add to the plan.")
            display_search_box("successor")
            if st.session_state.search_term:
                results = search_employees(st.session_state.search_term)
                if results:
                    display_search_results(results, "successor")
                else:
                    st.warning("No employees found.")

# --- SUBMIT SECTION - EXACT COPY FROM app_final.py ---
if st.session_state.app_data['incumbent'] and st.session_state.app_data['successors']:
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
                st.success(f"✅ Successfully saved {success_count} succession plan record(s) to the database!")
                st.info(f"🆔 Record IDs: {', '.join([rid[:8] + '...' for rid in saved_record_ids[:3]])}{'...' if len(saved_record_ids) > 3 else ''}")
                st.balloons()
            else:
                st.error(f"❌ Only {success_count} out of {len(successors)} records were saved successfully.")
    
    with col2:
        # PowerPoint download with session state approach
        if 'pptx_data' not in st.session_state:
            st.session_state.pptx_data = None
        
        # Generate button
        if st.button("📊 Generate PowerPoint", use_container_width=True, key="generate_pptx"):
            try:
                with st.spinner("Generating PowerPoint..."):
                    pptx_buffer = create_succession_plan_from_template(
                        st.session_state.app_data['incumbent'],
                        st.session_state.app_data['successors']
                    )
                    st.session_state.pptx_data = pptx_buffer.getvalue()
                    st.success("✅ PowerPoint generated! Download button below.")
            except Exception as e:
                st.error(f"Error creating PowerPoint: {e}")
        
        # Download button (only shows if data exists)
        if st.session_state.pptx_data:
            incumbent_name = st.session_state.app_data['incumbent']['metadata']['PREFERRED_NAME_LAST_NAME']
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
