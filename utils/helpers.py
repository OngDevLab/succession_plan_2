"""
Helper functions from app_final.py
"""

import streamlit as st
from streamlit.components.v1 import html

def force_page_reload():
    """Forces a full browser reload of the page using an HTML trick."""
    html_code = '<img src="non-existent-image.png" onerror="window.parent.location.reload()">'
    html(html_code, height=0, width=0)

def initialize_state():
    """Initializes session state variables if they don't exist."""
    defaults = {
        "app_data": {"incumbent": None, "successors": []},
        "selected_person": None,
        "search_term": "",
        "editing_incumbent": False,
        "editing_successor_index": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
