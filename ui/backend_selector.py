"""
Backend selector UI component
"""

import streamlit as st
from database.backend_manager import backend_manager

def display_backend_selector():
    """Display the backend selection interface"""
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗄️ Database Backend")
    
    # Get available backends
    backends = backend_manager.get_available_backends()
    current_backend = backend_manager.get_current_backend()
    
    # Create options for selectbox
    backend_options = []
    backend_mapping = {}
    
    for backend in backends:
        if backend['available']:
            display_text = f"{backend['display_name']} ✅"
            status_color = "🟢"
        else:
            display_text = f"{backend['display_name']} ❌"
            status_color = "🔴"
        
        backend_options.append(display_text)
        backend_mapping[display_text] = backend['name']
    
    # Find current selection
    current_display = None
    for option, name in backend_mapping.items():
        if name == current_backend:
            current_display = option
            break
    
    # Backend selector
    selected_display = st.sidebar.selectbox(
        "Choose Database:",
        options=backend_options,
        index=backend_options.index(current_display) if current_display else 0,
        help="Select which database to use for employee searches"
    )
    
    # Update backend if changed
    selected_backend = backend_mapping[selected_display]
    if selected_backend != current_backend:
        backend_manager.set_backend(selected_backend)
        st.sidebar.success(f"Switched to {selected_backend.title()}")
        st.rerun()
    
    # Display backend status
    current_backend_info = next((b for b in backends if b['name'] == current_backend), None)
    if current_backend_info:
        if current_backend_info['available']:
            st.sidebar.success(f"Status: {current_backend_info['status']}")
        else:
            st.sidebar.error(f"Status: {current_backend_info['status']}")
    
    # Display backend info
    with st.sidebar.expander("ℹ️ Backend Information"):
        st.write("**SQLite (Local):**")
        st.write("- Uses local database files")
        st.write("- Fast for development/testing")
        st.write("- Data stored locally")
        
        st.write("**Snowflake (Cloud):**")
        st.write("- Uses cloud data warehouse")
        st.write("- Production employee data")
        st.write("- Requires connection setup")
        
        if current_backend == 'snowflake':
            st.write("**Current Snowflake Tables:**")
            from config.loader import CONFIG
            tables = CONFIG['database']['snowflake']['tables']
            st.write(f"- Incumbents: `{tables['incumbents']}`")
            st.write(f"- Successors: `{tables['successors']}`")
    
    return current_backend

def display_backend_status():
    """Display current backend status in the main area"""
    current_backend = backend_manager.get_current_backend()
    backends = backend_manager.get_available_backends()
    current_info = next((b for b in backends if b['name'] == current_backend), None)
    
    if current_info:
        if current_backend == 'snowflake':
            if current_info['available']:
                st.info(f"🔗 Connected to **{current_info['display_name']}** - {current_info['status']}")
            else:
                st.warning(f"⚠️ **{current_info['display_name']}** - {current_info['status']}")
        else:
            st.info(f"💾 Using **{current_info['display_name']}** - {current_info['status']}")

def show_backend_configuration_help():
    """Show help for configuring Snowflake backend"""
    with st.expander("🔧 Snowflake Configuration Help"):
        st.markdown("""
        ### Setting up Snowflake Connection
        
        To use Snowflake as your backend, you need to configure connection parameters. 
        You can do this in several ways:
        
        #### Option 1: Streamlit Secrets (Recommended)
        Create a `.streamlit/secrets.toml` file with:
        ```toml
        [snowflake]
        account = "your-account"
        user = "your-username"
        password = "your-password"
        warehouse = "your-warehouse"
        database = "your-database"
        schema = "your-schema"
        ```
        
        #### Option 2: Environment Variables
        Set these environment variables:
        - `SNOWFLAKE_ACCOUNT`
        - `SNOWFLAKE_USER`
        - `SNOWFLAKE_PASSWORD`
        - `SNOWFLAKE_WAREHOUSE`
        - `SNOWFLAKE_DATABASE`
        - `SNOWFLAKE_SCHEMA`
        
        #### Option 3: Update Config File
        Edit `config/config.yaml` and update the snowflake section.
        
        ### Table Names
        Make sure your Snowflake tables match the names in the config:
        - Incumbents table: Update `database.snowflake.tables.incumbents`
        - Successors table: Update `database.snowflake.tables.successors`
        
        ### Required Columns
        Your Snowflake tables should have these columns:
        - `SEGMENT_HIER_LEVEL_2_NAME`
        - `PREFERRED_FIRST_NAME`
        - `PREFERRED_LAST_NAME`
        - `EMPLOYEE_ID`
        - `POSITION_REFERENCE_ID`
        - `POSITION_TITLE`
        - `MANAGEMENT_LEVEL`
        - `JOB_LEVEL`
        - `DAYS_IN_MANAGEMENT_LEVEL`
        - `LEADER_NAME`
        - `HR_SEGMENT`
        """)
