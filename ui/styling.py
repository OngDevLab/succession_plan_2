"""
CSS styling and visual components
"""

import streamlit as st

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
