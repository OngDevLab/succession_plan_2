"""
Snowflake database operations for succession planning tool
"""

import streamlit as st
import pandas as pd
import json
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
        
        # Format query with table name and employee_id (like your example)
        query = CONFIG['queries']['snowflake']['get_latest_incumbent_values'].format(
            succession_plans_table=CONFIG['database']['snowflake']['tables']['succession_plans'],
            employee_id=employee_id
        )
        
        # Execute query using st.connection (no params needed with string formatting)
        df = conn.query(query)
        
        if not df.empty:
            result = df.iloc[0].to_list()
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
        
        # Format query with table name and employee_id (like your example)
        query = CONFIG['queries']['snowflake']['get_latest_successor_values'].format(
            succession_plans_table=CONFIG['database']['snowflake']['tables']['succession_plans'],
            employee_id=employee_id
        )
        
        # Execute query using st.connection (no params needed with string formatting)
        df = conn.query(query)
        
        if not df.empty:
            result = df.iloc[0].to_list()
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
        
        # Format query with table name and both employee IDs (like your example)
        query = CONFIG['queries']['snowflake']['get_latest_successor_values_for_incumbent'].format(
            succession_plans_table=CONFIG['database']['snowflake']['tables']['succession_plans'],
            successor_employee_id=successor_employee_id,
            incumbent_employee_id=incumbent_employee_id
        )
        
        # Execute query using st.connection (no params needed with string formatting)
        df = conn.query(query)
        
        if not df.empty:
            result = df.iloc[0].to_list()
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
    """Save a succession plan record to Snowflake"""
    try:
        # Connect to Snowflake
        conn = st.connection("snowflake", type="snowflake")
        cursor = conn.cursor()
        
        # Get user access for ROW_CREATED_BY and ROW_CREATED_TIER
        user_access = st.session_state.get('current_user_access', {})
        created_by = user_access.get('user_id', 'unknown')
        created_tier = str(user_access.get('tier', 0))
        
        # Prepare data
        incumbent_id = incumbent_data['metadata']['EMPLOYEE_ID']
        incumbent_position_id = incumbent_data['metadata'].get('POSITION_ID', '')
        successor_id = successor_data['metadata']['EMPLOYEE_ID']
        successor_position_id = successor_data['metadata'].get('POSITION_ID', '')
        
        # Convert lists to JSON strings
        incumbent_top_skills = json.dumps(plan_details.get('top_skills', []))
        incumbent_sourcing_strategy = json.dumps(plan_details.get('sourcing_strategy', []))
        successor_top_skills = json.dumps(assessment_details.get('top_skills', []))
        
        # Insert query
        insert_sql = f"""
            INSERT INTO "HR_STREAMLIT"."SUCCESSION_PLAN"."TBL_SL_SUCCESSION_PLAN_DETAIL" (
                "SUCCESSION_PLAN_STATUS", "INCUMBENT_EMPLOYEE_ID", "INCUMBENT_POSITION_ID",
                "CRITICAL_ROLE_IND", "INCUMBENT_ROLE_RESPONSIBILITIES", "INCUMBENT_TOP_SKILLS",
                "INCUMBENT_TOP_PLE", "INCUMBENT_CONTRACT_END_DATE", "INCUMBENT_SOURCING_STRATEGY",
                "INCUMBENT_ROLE_TYPE", "INCUMBENT_ROLE_SCENARIO_PLAN", "INCUMBENT_ADDITIONAL_POSITION_TITLE",
                "SUCCESSOR_EMPLOYEE_ID", "SUCCESSOR_POSITION_ID", "SUCCESSOR_READINESS",
                "SUCCESSOR_FUTURE_READINESS_TIMING", "SUCCESSOR_CONTRACT_END_DATE", "SUCCESSOR_STRENGTHS",
                "SUCCESSOR_TOP_SKILLS", "SUCCESSOR_TOP_PLE", "SUCCESSOR_DEVELOPMENT_FOCUS",
                "SUCCESSOR_TALENT_ACTIONS", "ROW_CREATED_BY", "ROW_CREATED_ON", "ROW_CREATED_TIER"
            ) VALUES (
                'saved', '{incumbent_id}', '{incumbent_position_id}',
                {str(plan_details.get('critical_role', False)).upper()}, '{plan_details.get('responsibilities', '')}', '{incumbent_top_skills}',
                '{plan_details.get('top_ple', '')}', '{plan_details.get('contract_end_date', '')}', '{incumbent_sourcing_strategy}',
                '{plan_details.get('role_type', '')}', '{plan_details.get('scenario_plan', '')}', '{plan_details.get('new_position_title', '')}',
                '{successor_id}', '{successor_position_id}', '{assessment_details.get('readiness', '')}',
                '{assessment_details.get('future_readiness_timing', '')}', '{assessment_details.get('contract_end_date', '')}', '{assessment_details.get('strengths', '')}',
                '{successor_top_skills}', '{assessment_details.get('top_ple', '')}', '{assessment_details.get('development_focus', '')}',
                '{assessment_details.get('talent_actions', '')}', '{created_by}', CURRENT_TIMESTAMP(), '{created_tier}'
            )
        """
        
        cursor.execute(insert_sql)
        st.success("Succession plan saved to Snowflake!")
        return True
        
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
