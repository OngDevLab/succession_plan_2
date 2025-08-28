"""
Snowflake database operations for succession planning tool
"""

import streamlit as st
import pandas as pd
import json
import uuid
from datetime import datetime
from config.loader import CONFIG

# Try to import Snowpark session
try:
    from snowflake.snowpark.context import get_active_session
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False

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

def get_snowflake_session():
    """Get Snowflake session using Snowpark"""
    if not SNOWFLAKE_AVAILABLE:
        raise Exception("Snowflake Snowpark not available")
    try:
        session = get_active_session()
        return session
    except Exception as e:
        st.error(f"Failed to get Snowflake session: {e}")
        raise

@st.cache_data(show_spinner="Searching Snowflake database...")
def search_incumbents_snowflake(search_term, search_type="last_name"):
    """Queries Snowflake for incumbents by last name or full name."""
    try:
        conn = get_snowflake_connection()
        
        # Choose the appropriate query based on search type
        if search_type == "full_name":
            query_key = 'search_incumbents_full_name'
        else:
            query_key = 'search_incumbents'
        
        # Format query with table name, search term, and search limit (like your example)
        query = CONFIG['queries']['snowflake'][query_key].format(
            incumbents_table=CONFIG['database']['snowflake']['tables']['incumbents'],
            search_term=f"%{search_term}%",
            search_limit=CONFIG['database']['limits']['incumbent_search']
        )
        
        # Execute query using st.connection (no params needed with string formatting)
        df = conn.query(query)
        return df.to_dict('records')
        
    except Exception as e:
        st.error(f"Snowflake database error: {e}")
        return []

@st.cache_data(show_spinner="Searching Snowflake database...")
def search_successors_snowflake(search_term, search_type="last_name"):
    """Queries Snowflake for successors by last name or full name."""
    try:
        conn = get_snowflake_connection()
        
        # Choose the appropriate query based on search type
        if search_type == "full_name":
            query_key = 'search_successors_full_name'
        else:
            query_key = 'search_successors'
        
        # Format query with table name, search term, and search limit (like your example)
        query = CONFIG['queries']['snowflake'][query_key].format(
            successors_table=CONFIG['database']['snowflake']['tables']['successors'],
            search_term=f"%{search_term}%",
            search_limit=CONFIG['database']['limits']['successor_search']
        )
        
        # Execute query using st.connection (no params needed with string formatting)
        df = conn.query(query)
        return df.to_dict('records')
        
    except Exception as e:
        st.error(f"Snowflake database error: {e}")
        return []
    except Exception as e:
        st.error(f"Snowflake database error: {e}")
        return []

def get_latest_incumbent_values_snowflake(employee_id):
    """Get the latest incumbent plan values for prepopulation from Snowflake"""
    try:
        conn = get_snowflake_connection()
        
        query = CONFIG['queries']['snowflake']['get_latest_incumbent_values'].format(
            succession_plans_table=CONFIG['database']['snowflake']['tables']['succession_plans'],
            employee_id=employee_id
        )
        
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
        
        if result:
            return {
                "critical_role": result[0],
                "responsibilities": result[1],
                "top_skills": safe_json_parse(result[2], []),
                "top_ple": result[3],
                "contract_end_date": result[4],
                "sourcing_strategy": safe_json_parse(result[5], []),
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
    try:
        conn = get_snowflake_connection()
        
        query = CONFIG['queries']['snowflake']['get_latest_successor_values'].format(
            succession_plans_table=CONFIG['database']['snowflake']['tables']['succession_plans'],
            employee_id=employee_id
        )
        
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
        
        if result:
            return {
                "readiness": result[0],
                "future_readiness_timing": result[1],
                "contract_end_date": result[2],
                "strengths": result[3],
                "top_skills": safe_json_parse(result[4], []),
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
    try:
        conn = get_snowflake_connection()
        
        query = CONFIG['queries']['snowflake']['get_latest_successor_values_for_incumbent'].format(
            succession_plans_table=CONFIG['database']['snowflake']['tables']['succession_plans'],
            successor_employee_id=successor_employee_id,
            incumbent_employee_id=incumbent_employee_id
        )
        
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
        
        if result:
            return {
                "readiness": result[0],
                "future_readiness_timing": result[1],
                "contract_end_date": result[2],
                "strengths": result[3],
                "top_skills": safe_json_parse(result[4], []),
                "top_ple": result[5],
                "development_focus": result[6],
                "talent_actions": result[7]
            }
        return None
        
    except Exception as e:
        st.warning(f"Could not retrieve previous values from Snowflake: {e}")
        return None

def format_value(val):
    """Safely formats a Python value for direct insertion into an SQL query string."""
    if val is None:
        return "NULL"
    elif isinstance(val, bool):
        return str(val).upper()
    elif isinstance(val, (int, float)):
        return str(val)
    else:
        clean_val = str(val).replace("'", "''")
        return f"'{clean_val}'"

def save_succession_plan_snowflake(incumbent_data, successor_data, plan_details, assessment_details):
    """Save a succession plan record to Snowflake"""
    try:
        conn = st.connection("snowflake")
        table_name = CONFIG['database']['snowflake']['tables']['succession_plans']
        columns = CONFIG['queries']['snowflake']['save_succession_plan_columns']
        
        # Prepare record data
        record_data = {
            "RECORD_ID": str(uuid.uuid4()),
            "CREATED_AT": datetime.now(),
            "INCUMBENT_EMPLOYEE_ID": incumbent_data['EMPLOYEE_ID'],
            "INCUMBENT_FIRST_NAME": incumbent_data.get('PREFERRED_FIRST_NAME', ''),
            "INCUMBENT_LAST_NAME": incumbent_data.get('PREFERRED_LAST_NAME', ''),
            "INCUMBENT_EMAIL": incumbent_data.get('EMAIL_PRIMARY_WORK', ''),
            "INCUMBENT_POSITION": incumbent_data.get('POSITION_TITLE', ''),
            "INCUMBENT_MANAGEMENT_LEVEL": incumbent_data.get('MANAGEMENT_LEVEL', ''),
            "INCUMBENT_JOB_LEVEL": incumbent_data.get('JOB_LEVEL', ''),
            "INCUMBENT_SEGMENT": incumbent_data.get('SEGMENT_HIER_LEVEL_2_NAME', ''),
            "CRITICAL_ROLE": plan_details.get('critical_role', False),
            "RESPONSIBILITIES": plan_details.get('responsibilities', ''),
            "INCUMBENT_TOP_SKILLS": json.dumps(plan_details.get('top_skills', [])),
            "INCUMBENT_TOP_PLE": plan_details.get('top_ple', ''),
            "INCUMBENT_CONTRACT_END_DATE": plan_details.get('contract_end_date', ''),
            "SOURCING_STRATEGY": json.dumps(plan_details.get('sourcing_strategy', [])),
            "ROLE_TYPE": plan_details.get('role_type', ''),
            "SCENARIO_PLAN": plan_details.get('scenario_plan', ''),
            "NEW_POSITION_TITLE": plan_details.get('new_position_title', ''),
            "SUCCESSOR_EMPLOYEE_ID": successor_data['EMPLOYEE_ID'],
            "SUCCESSOR_FIRST_NAME": successor_data.get('PREFERRED_FIRST_NAME', ''),
            "SUCCESSOR_LAST_NAME": successor_data.get('PREFERRED_LAST_NAME', ''),
            "SUCCESSOR_EMAIL": successor_data.get('EMAIL_PRIMARY_WORK', ''),
            "SUCCESSOR_POSITION": successor_data.get('POSITION_TITLE', ''),
            "SUCCESSOR_MANAGEMENT_LEVEL": successor_data.get('MANAGEMENT_LEVEL', ''),
            "SUCCESSOR_JOB_LEVEL": successor_data.get('JOB_LEVEL', ''),
            "SUCCESSOR_SEGMENT": successor_data.get('SEGMENT_HIER_LEVEL_2_NAME', ''),
            "SUCCESSOR_READINESS": assessment_details.get('readiness', ''),
            "SUCCESSOR_FUTURE_READINESS_TIMING": assessment_details.get('future_readiness_timing', ''),
            "SUCCESSOR_CONTRACT_END_DATE": assessment_details.get('contract_end_date', ''),
            "SUCCESSOR_STRENGTHS": assessment_details.get('strengths', ''),
            "SUCCESSOR_TOP_SKILLS": json.dumps(assessment_details.get('top_skills', [])),
            "SUCCESSOR_TOP_PLE": assessment_details.get('top_ple', ''),
            "SUCCESSOR_DEVELOPMENT_FOCUS": assessment_details.get('development_focus', ''),
            "SUCCESSOR_TALENT_ACTIONS": assessment_details.get('talent_actions', ''),
            "REMOVED": False
        }
        
        columns = CONFIG['queries']['snowflake']['save_succession_plan_columns']
        formatted_values = ", ".join([format_value(v) for v in record_data.values()])
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({formatted_values})"
        
        with conn.cursor() as cursor:
            cursor.execute(insert_sql)
        
        st.success("Succession plan saved to Snowflake!")
        return record_data["RECORD_ID"]
        
    except Exception as e:
        st.error(f"Error saving to Snowflake: {e}")
        return False

def test_snowflake_connection():
    """Test the Snowflake connection and return status"""
    try:
        conn = get_snowflake_connection()
        # Test with a simple query (no params needed)
        df = conn.query("SELECT 1")
        if not df.empty:
            return True, "Connection successful"
        else:
            return False, "Query returned unexpected result"
    except Exception as e:
        return False, f"Connection failed: {e}"
