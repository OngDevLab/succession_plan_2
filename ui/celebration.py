"""
Celebration and feedback components
"""

import streamlit as st

def show_mickey_celebration():
    """Display celebration using reliable Streamlit balloons"""
    # Show balloons - this always works!
    st.balloons()
    
    # Add a success message
    st.success("🎉 **SUCCESS!** Your succession plan has been saved to the database! 🎉")

@st.dialog("🎉 Mickey Celebration! 🎉", width="large")
def show_celebration_dialog():
    """This function is no longer used but kept for compatibility"""
    pass
