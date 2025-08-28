"""
Backend selector UI component with separate read/write backend selection
"""

import streamlit as st
from database.backend_manager import backend_manager

def display_backend_selector():
    """Display the dual backend selection interface"""
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗄️ Database Configuration")
    
    # Get available backends
    backends = backend_manager.get_available_backends()
    current_read_backend = backend_manager.get_read_backend()
    current_write_backend = backend_manager.get_write_backend()
    
    # Create options for selectbox
    backend_options = []
    backend_mapping = {}
    
    for backend in backends:
        if backend['available']:
            display_text = f"{backend['display_name']}"
            backend_options.append(display_text)
            backend_mapping[display_text] = backend['name']
    
    if not backend_options:
        st.sidebar.error("No backends available")
        return current_read_backend
    
    # Read Backend Selection
    st.sidebar.write("**📖 Read/Query Backend:**")
    current_read_display = None
    for option, name in backend_mapping.items():
        if name == current_read_backend:
            current_read_display = option
            break
    
    selected_read_display = st.sidebar.selectbox(
        "Data source for searches & queries:",
        options=backend_options,
        index=backend_options.index(current_read_display) if current_read_display else 0,
        key="read_backend_selector",
        help="Choose where to read employee data from"
    )
    
    # Write Backend Selection
    st.sidebar.write("**💾 Write/Save Backend:**")
    current_write_display = None
    for option, name in backend_mapping.items():
        if name == current_write_backend:
            current_write_display = option
            break
    
    selected_write_display = st.sidebar.selectbox(
        "Data destination for succession plans:",
        options=backend_options,
        index=backend_options.index(current_write_display) if current_write_display else 0,
        key="write_backend_selector",
        help="Choose where to save succession plan data"
    )
    
    # Update backends if changed
    selected_read_backend = backend_mapping[selected_read_display]
    selected_write_backend = backend_mapping[selected_write_display]
    
    if selected_read_backend != current_read_backend:
        backend_manager.set_read_backend(selected_read_backend)
        st.rerun()
    
    if selected_write_backend != current_write_backend:
        backend_manager.set_write_backend(selected_write_backend)
        st.rerun()
    
    # Show current configuration summary
    st.sidebar.info(f"""
    **Current Setup:**
    📖 **Queries**: {selected_read_backend.upper()}
    💾 **Saves**: {selected_write_backend.upper()}
    """)
    
    # Return read backend for compatibility
    return selected_read_backend

def display_backend_status():
    """Display detailed backend status information"""
    
    backends = backend_manager.get_available_backends()
    read_backend = backend_manager.get_read_backend()
    write_backend = backend_manager.get_write_backend()
    
    st.subheader("🔧 Backend Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📖 Read Backend Status:**")
        read_info = next((b for b in backends if b['name'] == read_backend), None)
        if read_info:
            status_icon = "🟢" if read_info['available'] else "🔴"
            st.write(f"{status_icon} **{read_info['display_name']}**")
            st.write(f"Status: {read_info['status']}")
        
    with col2:
        st.write("**💾 Write Backend Status:**")
        write_info = next((b for b in backends if b['name'] == write_backend), None)
        if write_info:
            status_icon = "🟢" if write_info['available'] else "🔴"
            st.write(f"{status_icon} **{write_info['display_name']}**")
            st.write(f"Status: {write_info['status']}")
    
    # Show all available backends
    with st.expander("All Backend Details"):
        for backend in backends:
            status_icon = "🟢" if backend['available'] else "🔴"
            st.write(f"{status_icon} **{backend['display_name']}**: {backend['status']}")

def show_backend_configuration_help():
    """Show help for configuring backends"""
    
    st.warning("⚠️ Backend Configuration Needed")
    
    with st.expander("Backend Configuration Help"):
        st.markdown("""
        ### Dual Backend System
        
        This application supports separate backends for different operations:
        
        **📖 Read Backend (Queries):**
        - Used for searching employees
        - Used for loading existing data
        - Used for dashboard displays
        
        **💾 Write Backend (Saves):**
        - Used for saving succession plans
        - Used for workflow operations (approve, reject)
        - Used for audit trail updates
        
        ### Configuration Options:
        
        **Option 1: Both SQLite (Development)**
        - Read: SQLite, Write: SQLite
        - All data stays local
        - Good for testing and development
        
        **Option 2: Snowflake Queries, SQLite Saves**
        - Read: Snowflake, Write: SQLite
        - Query live employee data
        - Save plans locally for testing
        
        **Option 3: Both Snowflake (Production)**
        - Read: Snowflake, Write: Snowflake
        - Full production setup
        - All data in Snowflake
        
        **Option 4: SQLite Queries, Snowflake Saves**
        - Read: SQLite, Write: Snowflake
        - Use local test data for queries
        - Save to production Snowflake table
        """)
