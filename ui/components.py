"""
Main UI components module - imports from specialized component files
"""

# Import celebration components
from .celebration import show_mickey_celebration, show_celebration_dialog

# Import styling components
from .styling import load_css

# Import sidebar components
from .sidebar import display_sidebar_summary

# Import search components
from .search import display_search_box, display_search_results

# Import card components
from .cards import display_selected_incumbent_card

# Import form components
from .forms import display_incumbent_form, display_successor_form

# Re-export all functions for backward compatibility
__all__ = [
    'show_mickey_celebration',
    'show_celebration_dialog',
    'load_css',
    'display_sidebar_summary',
    'display_search_box',
    'display_search_results',
    'display_selected_incumbent_card',
    'display_incumbent_form',
    'display_successor_form'
]
