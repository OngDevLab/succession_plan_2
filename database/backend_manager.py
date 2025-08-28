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
    get_latest_successor_values_for_incumbent as get_latest_successor_values_for_incumbent_sqlite,
    save_succession_plan as save_succession_plan_sqlite
)

from .snowflake_operations import (
    search_incumbents_snowflake,
    search_successors_snowflake,
    get_latest_incumbent_values_snowflake,
    get_latest_successor_values_snowflake,
    get_latest_successor_values_for_incumbent_snowflake,
    save_succession_plan_snowflake,
    test_snowflake_connection,
    SNOWFLAKE_AVAILABLE
)

from .snowflake_user_access import (
    get_user_access_snowflake,
    filter_incumbents_by_access_snowflake,
    get_all_incumbents_in_segments_snowflake,
    get_employee_planning_dashboard_snowflake,
    can_user_search_snowflake,
    can_user_submit_snowflake,
    can_user_approve_snowflake
)

class BackendManager:
    """Manages database backend selection and operations with separate read/write backends"""
    
    def __init__(self):
        # Don't initialize session state at import time
        pass
    
    def initialize_backend_selection(self):
        """Initialize backend selection in session state (only when session state is available)"""
        try:
            if 'selected_read_backend' not in st.session_state:
                st.session_state.selected_read_backend = CONFIG['backend']['default']
            if 'selected_write_backend' not in st.session_state:
                st.session_state.selected_write_backend = CONFIG['backend']['default']
            # Keep legacy backend for compatibility
            if 'selected_backend' not in st.session_state:
                st.session_state.selected_backend = CONFIG['backend']['default']
        except AttributeError:
            # Session state not available (running outside Streamlit)
            pass
    
    def get_read_backend(self):
        """Get the currently selected read backend"""
        try:
            self.initialize_backend_selection()  # Ensure initialization
            return st.session_state.get('selected_read_backend', CONFIG['backend']['default'])
        except AttributeError:
            # Session state not available, return default
            return CONFIG['backend']['default']
    
    def get_write_backend(self):
        """Get the currently selected write backend"""
        try:
            self.initialize_backend_selection()  # Ensure initialization
            return st.session_state.get('selected_write_backend', CONFIG['backend']['default'])
        except AttributeError:
            # Session state not available, return default
            return CONFIG['backend']['default']
    
    def get_current_backend(self):
        """Get the currently selected backend (legacy - returns read backend)"""
        return self.get_read_backend()
    
    def set_read_backend(self, backend_name):
        """Set the read backend"""
        if backend_name in CONFIG['backend']['available_backends']:
            try:
                self.initialize_backend_selection()  # Ensure initialization
                st.session_state.selected_read_backend = backend_name
                # Clear any cached data when switching backends
                st.cache_data.clear()
                st.success(f"✅ Read backend set to: {backend_name.upper()}")
            except AttributeError:
                # Session state not available, silently ignore
                pass
        else:
            try:
                st.error(f"Invalid backend: {backend_name}")
            except AttributeError:
                # Session state not available, silently ignore
                pass
    
    def set_write_backend(self, backend_name):
        """Set the write backend"""
        if backend_name in CONFIG['backend']['available_backends']:
            try:
                self.initialize_backend_selection()  # Ensure initialization
                st.session_state.selected_write_backend = backend_name
                st.success(f"✅ Write backend set to: {backend_name.upper()}")
            except AttributeError:
                # Session state not available, silently ignore
                pass
        else:
            try:
                st.error(f"Invalid backend: {backend_name}")
            except AttributeError:
                # Session state not available, silently ignore
                pass
    
    def set_backend(self, backend_name):
        """Set both read and write backends (legacy method)"""
        self.set_read_backend(backend_name)
        self.set_write_backend(backend_name)
        try:
            self.initialize_backend_selection()  # Ensure initialization
            st.session_state.selected_backend = backend_name
        except AttributeError:
            # Session state not available, silently ignore
            pass
    
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
    
    def search_incumbents(self, search_term, search_type="last_name"):
        """Search incumbents using the selected READ backend"""
        backend = self.get_read_backend()
        if backend == 'snowflake':
            return search_incumbents_snowflake(search_term, search_type)
        else:
            return search_incumbents_sqlite(search_term, search_type)
    
    def search_successors(self, search_term, search_type="last_name"):
        """Search successors using the selected READ backend"""
        backend = self.get_read_backend()
        if backend == 'snowflake':
            return search_successors_snowflake(search_term, search_type)
        else:
            return search_successors_sqlite(search_term, search_type)
    
    def get_latest_incumbent_values(self, employee_id):
        """Get latest incumbent values using the selected READ backend"""
        backend = self.get_read_backend()
        if backend == 'snowflake':
            return get_latest_incumbent_values_snowflake(employee_id)
        else:
            # Always use SQLite for succession plans data for now
            return get_latest_incumbent_values_sqlite(employee_id)
    
    def get_latest_successor_values(self, employee_id):
        """Get latest successor values using the selected READ backend"""
        backend = self.get_read_backend()
        if backend == 'snowflake':
            return get_latest_successor_values_snowflake(employee_id)
        else:
            # Always use SQLite for succession plans data for now
            return get_latest_successor_values_sqlite(employee_id)
    
    def get_latest_successor_values_for_incumbent(self, successor_employee_id, incumbent_employee_id):
        """Get latest successor values for specific incumbent using the selected READ backend"""
        backend = self.get_read_backend()
        if backend == 'snowflake':
            return get_latest_successor_values_for_incumbent_snowflake(successor_employee_id, incumbent_employee_id)
        else:
            # Always use SQLite for succession plans data for now
            return get_latest_successor_values_for_incumbent_sqlite(successor_employee_id, incumbent_employee_id)
    
    def save_succession_plan(self, incumbent_data, successor_data, plan_details, assessment_details, user_access=None, status='saved'):
        """Save succession plan using the selected WRITE backend"""
        backend = self.get_write_backend()
        if backend == 'snowflake':
            from .snowflake_operations import save_succession_plan_snowflake
            return save_succession_plan_snowflake(incumbent_data, successor_data, plan_details, assessment_details, user_access, status)
        else:
            # Use SQLite for local development and testing
            from .operations import save_succession_plan as save_succession_plan_sqlite
            return save_succession_plan_sqlite(incumbent_data, successor_data, plan_details, assessment_details, user_access, status)
    
    def approve_submission(self, incumbent_employee_id, approver_user_access):
        """Approve a submission using the selected WRITE backend"""
        backend = self.get_write_backend()
        if backend == 'snowflake':
            from .snowflake_operations import approve_submission_snowflake
            return approve_submission_snowflake(incumbent_employee_id, approver_user_access)
        else:
            from .user_access import approve_submission
            return approve_submission(incumbent_employee_id, approver_user_access)
    
    def request_edits(self, incumbent_employee_id, requester_user_access):
        """Request edits using the selected WRITE backend"""
        backend = self.get_write_backend()
        if backend == 'snowflake':
            from .snowflake_operations import request_edits_snowflake
            return request_edits_snowflake(incumbent_employee_id, requester_user_access)
        else:
            from .user_access import request_edits
            return request_edits(incumbent_employee_id, requester_user_access)
    
    def reopen_approved_plan(self, incumbent_employee_id, requester_user_access):
        """Reopen an approved plan using the selected WRITE backend"""
        backend = self.get_write_backend()
        if backend == 'snowflake':
            from .snowflake_operations import reopen_approved_plan_snowflake
            return reopen_approved_plan_snowflake(incumbent_employee_id, requester_user_access)
        else:
            from .user_access import reopen_approved_plan
            return reopen_approved_plan(incumbent_employee_id, requester_user_access)
    
    def get_collaborative_incumbent_values(self, employee_id, user_access):
        """Get collaborative incumbent values using the selected READ backend"""
        backend = self.get_read_backend()
        if backend == 'snowflake':
            from .snowflake_operations import get_collaborative_incumbent_values_snowflake
            return get_collaborative_incumbent_values_snowflake(employee_id, user_access)
        else:
            from .user_access import get_collaborative_incumbent_values
            return get_collaborative_incumbent_values(employee_id, user_access)
    
    def get_all_test_users(self):
        """Get all test users - SQLite only for now"""
        from .user_access import get_all_test_users
        return get_all_test_users()
    
    def get_accessible_incumbents_for_tier3(self, user_access):
        """Get accessible incumbents for tier 3 - SQLite only for now"""
        from .user_access import get_accessible_incumbents_for_tier3
        return get_accessible_incumbents_for_tier3(user_access)
    
    def get_submitted_plans_for_tier1(self, user_access):
        """Get submitted plans for tier 1 - SQLite only for now"""
        from .user_access import get_submitted_plans_for_tier1
        return get_submitted_plans_for_tier1(user_access)
    
    def get_tier2_submission_for_incumbent(self, incumbent_employee_id, user_access):
        """Get tier 2 submission for incumbent - SQLite only for now"""
        from .user_access import get_tier2_submission_for_incumbent
        return get_tier2_submission_for_incumbent(incumbent_employee_id, user_access)
    
    def get_employee_planning_dashboard(self, user_access):
        """Get employee planning dashboard - SQLite only for now"""
        from .user_access import get_employee_planning_dashboard
        return get_employee_planning_dashboard(user_access)
    
    def get_user_access(self, email):
        """Get user access using the selected READ backend"""
        backend = self.get_read_backend()
        if backend == 'snowflake':
            return get_user_access_snowflake(email)
        else:
            # Import here to avoid circular imports
            from .user_access import get_user_access as get_user_access_sqlite
            return get_user_access_sqlite(email)
    
    def filter_incumbents_by_access(self, search_results, user_access):
        """Filter incumbents by access using the selected READ backend"""
        backend = self.get_read_backend()
        if backend == 'snowflake':
            return filter_incumbents_by_access_snowflake(search_results, user_access)
        else:
            from .user_access import filter_incumbents_by_access as filter_incumbents_by_access_sqlite
            return filter_incumbents_by_access_sqlite(search_results, user_access)
    
    def get_all_incumbents_in_segments(self, user_access):
        """Get all incumbents in segments using the selected READ backend"""
        backend = self.get_read_backend()
        if backend == 'snowflake':
            return get_all_incumbents_in_segments_snowflake(user_access)
        else:
            from .user_access import get_all_incumbents_in_segments as get_all_incumbents_in_segments_sqlite
            return get_all_incumbents_in_segments_sqlite(user_access)
    
    def get_employee_planning_dashboard(self, user_access):
        """Get employee planning dashboard using the selected backend"""
        backend = self.get_current_backend()
        if backend == 'snowflake':
            return get_employee_planning_dashboard_snowflake(user_access)
        else:
            from .user_access import get_employee_planning_dashboard as get_employee_planning_dashboard_sqlite
            return get_employee_planning_dashboard_sqlite(user_access)
    
    def can_user_search(self, user_access):
        """Check if user can search using the selected backend"""
        backend = self.get_current_backend()
        if backend == 'snowflake':
            return can_user_search_snowflake(user_access)
        else:
            from .user_access import can_user_search as can_user_search_sqlite
            return can_user_search_sqlite(user_access)
    
    def can_user_submit(self, user_access):
        """Check if user can submit using the selected backend"""
        backend = self.get_current_backend()
        if backend == 'snowflake':
            return can_user_submit_snowflake(user_access)
        else:
            from .user_access import can_user_submit as can_user_submit_sqlite
            return can_user_submit_sqlite(user_access)
    
    def can_user_approve(self, user_access):
        """Check if user can approve using the selected backend"""
        backend = self.get_current_backend()
        if backend == 'snowflake':
            return can_user_approve_snowflake(user_access)
        else:
            from .user_access import can_user_approve as can_user_approve_sqlite
            return can_user_approve_sqlite(user_access)

# Create a global instance
backend_manager = BackendManager()

# Export convenience functions that use the backend manager
def search_incumbents(search_term, search_type="last_name"):
    """Search incumbents using the selected backend"""
    return backend_manager.search_incumbents(search_term, search_type)

# Export convenience functions that use the backend manager
def search_incumbents(search_term, search_type="last_name"):
    """Search incumbents using the selected backend"""
    return backend_manager.search_incumbents(search_term, search_type)

def search_successors(search_term, search_type="last_name"):
    """Search successors using the selected backend"""
    return backend_manager.search_successors(search_term, search_type)

def get_latest_incumbent_values(employee_id):
    """Get latest incumbent values using the selected backend"""
    return backend_manager.get_latest_incumbent_values(employee_id)

def get_latest_successor_values(employee_id):
    """Get latest successor values using the selected backend"""
    return backend_manager.get_latest_successor_values(employee_id)

def get_latest_successor_values_for_incumbent(successor_employee_id, incumbent_employee_id):
    """Get latest successor values for specific incumbent using the selected backend"""
    return backend_manager.get_latest_successor_values_for_incumbent(successor_employee_id, incumbent_employee_id)

def save_succession_plan(incumbent_data, successor_data, plan_details, assessment_details, user_access=None, status='saved'):
    """Save succession plan using the selected backend"""
    return backend_manager.save_succession_plan(incumbent_data, successor_data, plan_details, assessment_details, user_access, status)

def get_user_access(email):
    """Get user access using the selected backend"""
    return backend_manager.get_user_access(email)

def filter_incumbents_by_access(search_results, user_access):
    """Filter incumbents by access using the selected backend"""
    return backend_manager.filter_incumbents_by_access(search_results, user_access)

def get_all_incumbents_in_segments(user_access):
    """Get all incumbents in segments using the selected backend"""
    return backend_manager.get_all_incumbents_in_segments(user_access)

def approve_submission(incumbent_employee_id, approver_user_access):
    """Approve a submission using the selected backend"""
    return backend_manager.approve_submission(incumbent_employee_id, approver_user_access)

def request_edits(incumbent_employee_id, requester_user_access):
    """Request edits using the selected backend"""
    return backend_manager.request_edits(incumbent_employee_id, requester_user_access)

def reopen_approved_plan(incumbent_employee_id, requester_user_access):
    """Reopen an approved plan using the selected backend"""
    return backend_manager.reopen_approved_plan(incumbent_employee_id, requester_user_access)

def get_collaborative_incumbent_values(employee_id, user_access):
    """Get collaborative incumbent values using the selected backend"""
    return backend_manager.get_collaborative_incumbent_values(employee_id, user_access)

def get_all_test_users():
    """Get all test users"""
    return backend_manager.get_all_test_users()

def get_accessible_incumbents_for_tier3(user_access):
    """Get accessible incumbents for tier 3"""
    return backend_manager.get_accessible_incumbents_for_tier3(user_access)

def get_submitted_plans_for_tier1(user_access):
    """Get submitted plans for tier 1"""
    return backend_manager.get_submitted_plans_for_tier1(user_access)

def get_tier2_submission_for_incumbent(incumbent_employee_id, user_access):
    """Get tier 2 submission for incumbent"""
    return backend_manager.get_tier2_submission_for_incumbent(incumbent_employee_id, user_access)

def get_employee_planning_dashboard(user_access):
    """Get employee planning dashboard using the selected backend"""
    return backend_manager.get_employee_planning_dashboard(user_access)

def can_user_search(user_access):
    """Check if user can search using the selected backend"""
    return backend_manager.can_user_search(user_access)

def can_user_submit(user_access):
    """Check if user can submit using the selected backend"""
    return backend_manager.can_user_submit(user_access)

def can_user_approve(user_access):
    """Check if user can approve using the selected backend"""
    return backend_manager.can_user_approve(user_access)
