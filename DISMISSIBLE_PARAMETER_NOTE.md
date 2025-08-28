# Dismissible Parameter Note

## Issue
The `dismissible=False` parameter in `@st.dialog()` decorators was causing compatibility issues with Streamlit version 1.47.1.

## Current Status
The parameter has been temporarily removed for compatibility:

```python
# Current (compatible)
@st.dialog("Incumbent Plan Details", width="large")
def display_incumbent_form():

@st.dialog("Successor Plan", width="large") 
def display_successor_form():
```

## To Add Back Dismissible
If your Streamlit version supports the `dismissible` parameter, you can manually add it back:

```python
# With dismissible parameter
@st.dialog("Incumbent Plan Details", width="large", dismissible=False)
def display_incumbent_form():

@st.dialog("Successor Plan", width="large", dismissible=False)
def display_successor_form():
```

## What Dismissible Does
- `dismissible=False`: Prevents users from closing the dialog by clicking outside of it
- Users must use the Cancel/Close buttons to exit the form
- Helps prevent accidental data loss during form entry

## Version Compatibility
The `dismissible` parameter may be available in newer versions of Streamlit. Check your version with:
```bash
python -c "import streamlit as st; print(st.__version__)"
```

You can safely add `dismissible=False` back to both dialog decorators if your version supports it.
