"""
Snowflake database operations for succession planning tool
"""

import streamlit as st
import pandas as pd
import json
from config.loader import CONFIG

# Snowflake is available through st.connection
SNOWFLAKE_AVAILABLE = True

def safe_json_parse(json_str, default=None):
    """Safely parse JSON string, return default if parsing fails"""
    if not json_str:
        return default
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def get_snowflake_connection():
    """Create and return a Snowflake connection using st.connection"""
    try:
        # Use Streamlit's built-in connection method (like your working code)
        conn = st.connection("snowflake", type="snowflake")
        return conn
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {e}")
        raise

@st.cache_data(show_spinner="Searching Snowflake database...")
def search_incumbents_snowflake(search_term, search_type="last_name"):
    """Queries Snowflake for incumbents by last name or full name."""
    if not SNOWFLAKE_AVAILABLE:
        st.error("Snowflake connector not available")
        return []
    
    try:
        conn = get_snowflake_connection()
        
        # Choose the appropriate query based on search type
        if search_type == "full_name":
            query_key = 'search_incumbents_full_name'
        else:
            query_key = 'search_incumbents'
        
        # Format query with table name and search limit
        query = CONFIG['queries']['snowflake'][query_key].format(
            incumbents_table=CONFIG['database']['snowflake']['tables']['incumbents'],
            search_limit=CONFIG['database']['limits']['incumbent_search']
        )
        
        # Execute query with parameterized search term
        df = pd.read_sql_query(query, conn, params=[f"%{search_term}%"])
        conn.close()
        return df.to_dict('records')
        
    except Exception as e:
        st.error(f"Snowflake database error: {e}")
        return []

@st.cache_data(show_spinner="Searching Snowflake database...")
def search_successors_snowflake(search_term, search_type="last_name"):
    """Queries Snowflake for successors by last name or full name."""
    if not SNOWFLAKE_AVAILABLE:
        st.error("Snowflake connector not available")
        return []
    
    try:
        conn = get_snowflake_connection()
        
        # Choose the appropriate query based on search type
        if search_type == "full_name":
            query_key = 'search_successors_full_name'
        else:
            query_key = 'search_successors'
        
        # Format query with table name and search limit
        query = CONFIG['queries']['snowflake'][query_key].format(
            successors_table=CONFIG['database']['snowflake']['tables']['successors'],
            search_limit=CONFIG['database']['limits']['successor_search']
        )
        
        # Execute query with parameterized search term
        df = pd.read_sql_query(query, conn, params=[f"%{search_term}%"])
        conn.close()
        return df.to_dict('records')
        
    except Exception as e:
        st.error(f"Snowflake database error: {e}")
        return []

def get_latest_incumbent_values_snowflake(employee_id):
    """Get the latest incumbent plan values for prepopulation from Snowflake"""
    try:
        conn = get_snowflake_connection()
        
        # Format query with table name
        query = CONFIG['queries']['snowflake']['get_latest_incumbent_values'].format(
            succession_plans_table=CONFIG['database']['snowflake']['tables']['succession_plans']
        )
        
        # Execute query using st.connection
        df = conn.query(query, params=(employee_id,))
        
        if not df.empty:
            result = df.iloc[0].to_list()
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
                # "contract_end_date": result["contract_end_date": result[2],],  # Excluded to keep clear (x) button
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

def get_latest_successor_values_for_incumbent_snowflake(successor_employee_id, incumbent_employee_id):
    """Get the latest successor assessment values for prepopulation from Snowflake, filtered by incumbent"""
    if not SNOWFLAKE_AVAILABLE:
        return None
    
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        # Format query with table name
        query = CONFIG['queries']['snowflake']['get_latest_successor_values_for_incumbent'].format(
            succession_plans_table=CONFIG['database']['snowflake']['tables']['succession_plans']
        )
        
        cursor.execute(query, [successor_employee_id, incumbent_employee_id])
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "readiness": result[0],
                "future_readiness_timing": result[1],
                # "contract_end_date": result["contract_end_date": result[2],],  # Excluded to keep clear (x) button
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
    try:
        conn = get_snowflake_connection()
        # Test with a simple query
        df = conn.query("SELECT 1 as test")
        if not df.empty and df.iloc[0]['test'] == 1:
            return True, "Connection successful"
        else:
            return False, "Query returned unexpected result"
    except Exception as e:
        return False, f"Connection failed: {e}"
