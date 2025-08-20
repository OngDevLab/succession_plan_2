"""
Snowflake database operations for succession planning tool
"""

import streamlit as st
import pandas as pd
import json
from config.loader import CONFIG

# Try to import snowflake connector
try:
    import snowflake.connector
    from snowflake.connector.pandas_tools import write_pandas
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    st.error("Snowflake connector not installed. Please install: pip install snowflake-connector-python")

def get_snowflake_connection():
    """Create and return a Snowflake connection using configuration or secrets"""
    if not SNOWFLAKE_AVAILABLE:
        raise Exception("Snowflake connector not available")
    
    try:
        # Try to get connection parameters from Streamlit secrets first
        if hasattr(st, 'secrets') and 'snowflake' in st.secrets:
            conn_params = {
                'account': st.secrets.snowflake.account,
                'user': st.secrets.snowflake.user,
                'password': st.secrets.snowflake.password,
                'warehouse': st.secrets.snowflake.warehouse,
                'database': st.secrets.snowflake.database,
                'schema': st.secrets.snowflake.schema,
            }
        else:
            # Fallback to environment variables or config
            import os
            conn_params = {
                'account': os.getenv('SNOWFLAKE_ACCOUNT', CONFIG['database']['snowflake']['account']),
                'user': os.getenv('SNOWFLAKE_USER', CONFIG['database']['snowflake']['user']),
                'password': os.getenv('SNOWFLAKE_PASSWORD', CONFIG['database']['snowflake']['password']),
                'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', CONFIG['database']['snowflake']['warehouse']),
                'database': os.getenv('SNOWFLAKE_DATABASE', CONFIG['database']['snowflake']['database']),
                'schema': os.getenv('SNOWFLAKE_SCHEMA', CONFIG['database']['snowflake']['schema']),
            }
        
        # Validate that we have all required parameters
        required_params = ['account', 'user', 'password', 'warehouse', 'database', 'schema']
        missing_params = [param for param in required_params if not conn_params.get(param)]
        
        if missing_params:
            raise Exception(f"Missing Snowflake connection parameters: {', '.join(missing_params)}")
        
        return snowflake.connector.connect(**conn_params)
        
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {e}")
        raise

@st.cache_data(show_spinner="Searching Snowflake database...")
def search_incumbents_snowflake(last_name):
    """Queries Snowflake for incumbents by last name."""
    if not SNOWFLAKE_AVAILABLE:
        st.error("Snowflake connector not available")
        return []
    
    try:
        conn = get_snowflake_connection()
        
        # Format query with table name and search limit
        query = CONFIG['queries']['snowflake']['search_incumbents'].format(
            incumbents_table=CONFIG['database']['snowflake']['tables']['incumbents'],
            search_limit=CONFIG['database']['limits']['incumbent_search']
        )
        
        # Execute query with parameterized search term
        df = pd.read_sql_query(query, conn, params=[f"%{last_name}%"])
        conn.close()
        return df.to_dict('records')
        
    except Exception as e:
        st.error(f"Snowflake database error: {e}")
        return []

@st.cache_data(show_spinner="Searching Snowflake database...")
def search_successors_snowflake(last_name):
    """Queries Snowflake for successors by last name."""
    if not SNOWFLAKE_AVAILABLE:
        st.error("Snowflake connector not available")
        return []
    
    try:
        conn = get_snowflake_connection()
        
        # Format query with table name and search limit
        query = CONFIG['queries']['snowflake']['search_successors'].format(
            successors_table=CONFIG['database']['snowflake']['tables']['successors'],
            search_limit=CONFIG['database']['limits']['successor_search']
        )
        
        # Execute query with parameterized search term
        df = pd.read_sql_query(query, conn, params=[f"%{last_name}%"])
        conn.close()
        return df.to_dict('records')
        
    except Exception as e:
        st.error(f"Snowflake database error: {e}")
        return []

def get_latest_incumbent_values_snowflake(employee_id):
    """Get the latest incumbent plan values for prepopulation from Snowflake"""
    if not SNOWFLAKE_AVAILABLE:
        return None
    
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        # Format query with table name
        query = CONFIG['queries']['snowflake']['get_latest_incumbent_values'].format(
            succession_plans_table=CONFIG['database']['snowflake']['tables']['succession_plans']
        )
        
        cursor.execute(query, [employee_id])
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "critical_role": result[0],
                "responsibilities": result[1],
                "top_skills": json.loads(result[2]) if result[2] else [],
                "top_ple": result[3],
                "contract_end_date": result[4],
                "sourcing_strategy": json.loads(result[5]) if result[5] else [],
                "role_type": result[6],
                "scenario_plan": result[7],
                "new_position_title": result[8]
            }
        return None
        
    except Exception as e:
        st.warning(f"Could not retrieve previous values from Snowflake: {e}")
        return None

def get_latest_successor_values_snowflake(employee_id):
    """Get the latest successor assessment values for prepopulation from Snowflake"""
    if not SNOWFLAKE_AVAILABLE:
        return None
    
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        # Format query with table name
        query = CONFIG['queries']['snowflake']['get_latest_successor_values'].format(
            succession_plans_table=CONFIG['database']['snowflake']['tables']['succession_plans']
        )
        
        cursor.execute(query, [employee_id])
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "readiness": result[0],
                "future_readiness_timing": result[1],
                "contract_end_date": result[2],
                "strengths": result[3],
                "top_skills": json.loads(result[4]) if result[4] else [],
                "top_ple": result[5],
                "development_focus": result[6],
                "talent_actions": result[7]
            }
        return None
        
    except Exception as e:
        st.warning(f"Could not retrieve previous values from Snowflake: {e}")
        return None

def save_succession_plan_snowflake(incumbent_data, successor_data, plan_details, assessment_details):
    """Save a succession plan record to Snowflake (placeholder for future implementation)"""
    st.warning("Saving to Snowflake is not yet implemented. Data will be saved to SQLite instead.")
    # For now, fall back to SQLite saving
    from .operations import save_succession_plan
    return save_succession_plan(incumbent_data, successor_data, plan_details, assessment_details)

def test_snowflake_connection():
    """Test the Snowflake connection and return status"""
    if not SNOWFLAKE_AVAILABLE:
        return False, "Snowflake connector not installed"
    
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        return True, "Connection successful"
    except Exception as e:
        return False, f"Connection failed: {e}"
