"""
Custom date input component with clear functionality
"""

import streamlit as st
import datetime

def date_input_with_clear(label, value=None, key=None, help_text=None):
    """
    Custom date input with a clear button
    
    Args:
        label: Label for the date input
        value: Initial date value (None for empty)
        key: Unique key for the component
        help_text: Optional help text
    
    Returns:
        Selected date or None if cleared
    """
    # Create unique keys for the components
    date_key = f"{key}_date" if key else "date_input"
    clear_key = f"{key}_clear" if key else "clear_button"
    state_key = f"{key}_state" if key else "date_state"
    
    # Initialize session state for this date input
    if state_key not in st.session_state:
        st.session_state[state_key] = value
    
    # Create columns for date input and clear button
    col_date, col_clear = st.columns([4, 1])
    
    with col_date:
        # Show date input with current value
        current_value = st.session_state[state_key]
        if current_value is not None:
            selected_date = st.date_input(
                label, 
                value=current_value, 
                key=date_key,
                help=help_text
            )
        else:
            selected_date = st.date_input(
                label, 
                key=date_key,
                help=help_text
            )
        
        # Update session state when date changes
        st.session_state[state_key] = selected_date
    
    with col_clear:
        st.write("")  # Add spacing to align with date input
        if st.button("✕", key=clear_key, help="Clear date", use_container_width=True):
            st.session_state[state_key] = None
            st.rerun()
    
    return st.session_state[state_key]
