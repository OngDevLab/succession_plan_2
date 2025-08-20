"""
Backend manager for switching between SQLite and Snowflake databases
"""

import streamlit as st
from config.loader import CONFIG

# Import database operations
from .operations import (
    search_incumbents as search_incumbents_sqlite,
    search_successors as search_successors_sqlite,
    get_latest_incumbent_values as get_latest_incumbent_values_sqlite,
    get_latest_successor_values as get_latest_successor_values_sqlite,
    save_succession_plan as save_succession_plan_sqlite
)

from .snowflake_operations import (
    search_incumbents_snowflake,
    search_successors_snowflake,
    get_latest_incumbent_values_snowflake,
    get_latest_successor_values_snowflake,
    save_succession_plan_snowflake,
    test_snowflake_connection,
    SNOWFLAKE_AVAILABLE
)

class BackendManager:
    """Manages database backend selection and operations"""
    
    def __init__(self):
        self.initialize_backend_selection()
    
    def initialize_backend_selection(self):
        """Initialize backend selection in session state"""
        if 'selected_backend' not in st.session_state:
            st.session_state.selected_backend = CONFIG['backend']['default']
    
    def get_current_backend(self):
        """Get the currently selected backend"""
        return st.session_state.get('selected_backend', CONFIG['backend']['default'])
    
    def set_backend(self, backend_name):
        """Set the current backend"""
        if backend_name in CONFIG['backend']['available_backends']:
            st.session_state.selected_backend = backend_name
            # Clear any cached data when switching backends
            st.cache_data.clear()
        else:
            st.error(f"Invalid backend: {backend_name}")
    
    def get_available_backends(self):
        """Get list of available backends with their status"""
        backends = []
        for backend in CONFIG['backend']['available_backends']:
            if backend == 'sqlite':
                backends.append({
                    'name': 'sqlite',
                    'display_name': 'SQLite (Local)',
                    'available': True,
                    'status': 'Ready'
                })
            elif backend == 'snowflake':
                if SNOWFLAKE_AVAILABLE:
                    # Test connection
                    try:
                        is_connected, status = test_snowflake_connection()
                        backends.append({
                            'name': 'snowflake',
                            'display_name': 'Snowflake (Cloud)',
                            'available': is_connected,
                            'status': status
                        })
                    except:
                        backends.append({
                            'name': 'snowflake',
                            'display_name': 'Snowflake (Cloud)',
                            'available': False,
                            'status': 'Connection not configured'
                        })
                else:
                    backends.append({
                        'name': 'snowflake',
                        'display_name': 'Snowflake (Cloud)',
                        'available': False,
                        'status': 'Connector not installed'
                    })
        return backends
    
    def search_incumbents(self, last_name):
        """Search incumbents using the selected backend"""
        backend = self.get_current_backend()
        if backend == 'snowflake':
            return search_incumbents_snowflake(last_name)
        else:
            return search_incumbents_sqlite(last_name)
    
    def search_successors(self, last_name):
        """Search successors using the selected backend"""
        backend = self.get_current_backend()
        if backend == 'snowflake':
            return search_successors_snowflake(last_name)
        else:
            return search_successors_sqlite(last_name)
    
    def get_latest_incumbent_values(self, employee_id):
        """Get latest incumbent values using the selected backend"""
        backend = self.get_current_backend()
        if backend == 'snowflake':
            return get_latest_incumbent_values_snowflake(employee_id)
        else:
            # Always use SQLite for succession plans data for now
            return get_latest_incumbent_values_sqlite(employee_id)
    
    def get_latest_successor_values(self, employee_id):
        """Get latest successor values using the selected backend"""
        backend = self.get_current_backend()
        if backend == 'snowflake':
            return get_latest_successor_values_snowflake(employee_id)
        else:
            # Always use SQLite for succession plans data for now
            return get_latest_successor_values_sqlite(employee_id)
    
    def save_succession_plan(self, incumbent_data, successor_data, plan_details, assessment_details):
        """Save succession plan using the selected backend"""
        # For now, always save to SQLite regardless of selected backend
        # This preserves existing functionality
        return save_succession_plan_sqlite(incumbent_data, successor_data, plan_details, assessment_details)

# Create a global instance
backend_manager = BackendManager()

# Export convenience functions that use the backend manager
def search_incumbents(last_name):
    """Search incumbents using the selected backend"""
    return backend_manager.search_incumbents(last_name)

def search_successors(last_name):
    """Search successors using the selected backend"""
    return backend_manager.search_successors(last_name)

def get_latest_incumbent_values(employee_id):
    """Get latest incumbent values using the selected backend"""
    return backend_manager.get_latest_incumbent_values(employee_id)

def get_latest_successor_values(employee_id):
    """Get latest successor values using the selected backend"""
    return backend_manager.get_latest_successor_values(employee_id)

def save_succession_plan(incumbent_data, successor_data, plan_details, assessment_details):
    """Save succession plan using the selected backend"""
    return backend_manager.save_succession_plan(incumbent_data, successor_data, plan_details, assessment_details)
