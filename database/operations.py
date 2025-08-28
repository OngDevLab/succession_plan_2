"""
Database functions - Using fully configurable queries from config
"""

import streamlit as st
import pandas as pd
import sqlite3
import json
import datetime
from config.loader import CONFIG

@st.cache_data(show_spinner="Searching database...")
def search_incumbents(search_term, search_type="last_name"):
    """Queries the SQLite database for incumbents by last name or full name."""
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['employee_db'])
        
        # Choose the appropriate query based on search type
        if search_type == "full_name":
            query_key = 'search_incumbents_full_name'
        else:
            query_key = 'search_incumbents'
        
        # Format query with table name and search limit
        query = CONFIG['queries']['sqlite'][query_key].format(
            incumbents_table=CONFIG['database']['sqlite']['tables']['incumbents'],
            search_limit=CONFIG['database']['limits']['incumbent_search']
        )
        
        df = pd.read_sql_query(query, conn, params=(f"%{search_term}%",))
        conn.close()
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Database error: {e}")
        return []

@st.cache_data(show_spinner="Searching database...")
def search_successors(search_term, search_type="last_name"):
    """Queries the SQLite database for successors by last name or full name."""
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['employee_db'])
        
        # Choose the appropriate query based on search type
        if search_type == "full_name":
            query_key = 'search_successors_full_name'
        else:
            query_key = 'search_successors'
        
        # Format query with table name and search limit
        query = CONFIG['queries']['sqlite'][query_key].format(
            successors_table=CONFIG['database']['sqlite']['tables']['successors'],
            search_limit=CONFIG['database']['limits']['successor_search']
        )
        
        df = pd.read_sql_query(query, conn, params=(f"%{search_term}%",))
        conn.close()
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Database error: {e}")
        return []

# Keep the old function for backward compatibility, but make it search successors
@st.cache_data(show_spinner="Searching database...")
def search_employees(search_term, search_type="last_name"):
    """Queries the SQLite database for employees by last name or full name. (Legacy function - now searches successors)"""
    return search_successors(search_term, search_type)

def get_latest_incumbent_values(employee_id):
    """Get the latest incumbent plan values for prepopulation"""
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        cursor = conn.cursor()
        
        # Format query with table name
        query = CONFIG['queries']['sqlite']['get_latest_incumbent_values'].format(
            succession_plans_table=CONFIG['database']['sqlite']['tables']['succession_plans']
        )
        
        cursor.execute(query, (employee_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Helper function to safely parse JSON or return as list
            def safe_json_parse(value, default=None):
                if not value:
                    return default or []
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # If it's not valid JSON, treat as single item or return as-is
                    if isinstance(value, str):
                        return [value] if default == [] else value
                    return value
            
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
        return None

def get_latest_successor_values(employee_id):
    """Get the latest successor assessment values for prepopulation"""
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        cursor = conn.cursor()
        
        # Format query with table name
        query = CONFIG['queries']['sqlite']['get_latest_successor_values'].format(
            succession_plans_table=CONFIG['database']['sqlite']['tables']['succession_plans']
        )
        
        cursor.execute(query, (employee_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Helper function to safely parse JSON or return as list
            def safe_json_parse(value, default=None):
                if not value:
                    return default or []
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # If it's not valid JSON, treat as single item or return as-is
                    if isinstance(value, str):
                        return [value] if default == [] else value
                    return value
            
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
        return None

def get_latest_successor_values_for_incumbent(successor_employee_id, incumbent_employee_id):
    """Get the latest successor assessment values for prepopulation, filtered by incumbent"""
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        cursor = conn.cursor()
        
        # Format query with table name
        query = CONFIG['queries']['sqlite']['get_latest_successor_values_for_incumbent'].format(
            succession_plans_table=CONFIG['database']['sqlite']['tables']['succession_plans']
        )
        
        cursor.execute(query, (successor_employee_id, incumbent_employee_id))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Helper function to safely parse JSON or return as list
            def safe_json_parse(value, default=None):
                if not value:
                    return default or []
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # If it's not valid JSON, treat as single item or return as-is
                    if isinstance(value, str):
                        return [value] if default == [] else value
                    return value
            
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
        return None

def get_existing_successors_for_incumbent(incumbent_employee_id):
    """Get existing successors for an incumbent (latest non-removed entries only)"""
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        
        # Format query with table name
        query = CONFIG['queries']['sqlite']['get_existing_successors_for_incumbent'].format(
            succession_plans_table=CONFIG['database']['sqlite']['tables']['succession_plans']
        )
        
        df = pd.read_sql_query(query, conn, params=(incumbent_employee_id, incumbent_employee_id))
        conn.close()
        
        successors = []
        for _, row in df.iterrows():
            # Helper function to safely parse JSON or return as list
            def safe_json_parse(value, default=None):
                if not value:
                    return default or []
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # If it's not valid JSON, treat as single item or return as-is
                    if isinstance(value, str):
                        return [value] if default == [] else value
                    return value
            
            # Create metadata structure matching the employee search results
            metadata = {
                'EMPLOYEE_ID': row['SUCCESSOR_EMPLOYEE_ID'],
                'PREFERRED_FIRST_NAME': row['SUCCESSOR_FIRST_NAME'],
                'PREFERRED_LAST_NAME': row['SUCCESSOR_LAST_NAME'],
                'POSITION_TITLE': row['SUCCESSOR_POSITION'],
                'MANAGEMENT_LEVEL': row['SUCCESSOR_MANAGEMENT_LEVEL'],
                'JOB_LEVEL': row['SUCCESSOR_JOB_LEVEL'],
                'SEGMENT_HIER_LEVEL_2_NAME': row['SUCCESSOR_SEGMENT'],
                'LEADER_NAME': None,  # Not stored in succession plans
                'HR_SEGMENT': None    # Not stored in succession plans
            }
            
            # Create assessment structure
            assessment = {
                'readiness': row['SUCCESSOR_READINESS'],
                'future_readiness_timing': row['SUCCESSOR_FUTURE_READINESS_TIMING'],
                'contract_end_date': row['SUCCESSOR_CONTRACT_END_DATE'],
                'strengths': row['SUCCESSOR_STRENGTHS'],
                'top_skills': safe_json_parse(row['SUCCESSOR_TOP_SKILLS'], []),
                'top_ple': row['SUCCESSOR_TOP_PLE'],
                'development_focus': row['SUCCESSOR_DEVELOPMENT_FOCUS'],
                'talent_actions': row['SUCCESSOR_TALENT_ACTIONS']
            }
            
            successors.append({
                'metadata': metadata,
                'assessment': assessment
            })
        
        return successors
        
    except Exception as e:
        return []

def mark_successor_as_removed(incumbent_data, successor_data, plan_details, assessment_details):
    """Mark a successor as removed by creating a new record with REMOVED=TRUE"""
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        cursor = conn.cursor()
        
        # Format query with table name
        query = CONFIG['queries']['sqlite']['mark_successor_as_removed'].format(
            succession_plans_table=CONFIG['database']['sqlite']['tables']['succession_plans']
        )
        
        cursor.execute(query, (
            incumbent_data['EMPLOYEE_ID'],
            incumbent_data['PREFERRED_FIRST_NAME'],
            incumbent_data['PREFERRED_LAST_NAME'],
            incumbent_data.get('EMAIL_PRIMARY_WORK', ''),
            incumbent_data.get('POSITION_TITLE', ''),
            incumbent_data['MANAGEMENT_LEVEL'],
            incumbent_data['JOB_LEVEL'],
            incumbent_data['SEGMENT_HIER_LEVEL_2_NAME'],
            plan_details['critical_role'],
            plan_details['responsibilities'],
            json.dumps(plan_details['top_skills']),
            plan_details['top_ple'],
            plan_details.get('contract_end_date'),
            json.dumps(plan_details['sourcing_strategy']),
            plan_details.get('role_type'),
            plan_details['scenario_plan'],
            plan_details.get('new_position_title'),
            successor_data['EMPLOYEE_ID'],
            successor_data['PREFERRED_FIRST_NAME'],
            successor_data['PREFERRED_LAST_NAME'],
            successor_data.get('EMAIL_PRIMARY_WORK', ''),
            successor_data.get('POSITION_TITLE', ''),
            successor_data['MANAGEMENT_LEVEL'],
            successor_data['JOB_LEVEL'],
            successor_data['SEGMENT_HIER_LEVEL_2_NAME'],
            assessment_details['readiness'],
            assessment_details.get('future_readiness_timing'),
            assessment_details.get('contract_end_date'),
            assessment_details['strengths'],
            json.dumps(assessment_details['top_skills']),
            assessment_details['top_ple'],
            assessment_details['development_focus'],
            assessment_details['talent_actions']
        ))
        
        # Get the generated RECORD_ID
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return str(record_id)
        
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

def save_succession_plan(incumbent_data, successor_data, plan_details, assessment_details, user_access=None, status='saved'):
    """Save a succession plan record to the database with user tracking"""
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        cursor = conn.cursor()
        
        # Format query with table name
        query = CONFIG['queries']['sqlite']['save_succession_plan'].format(
            succession_plans_table=CONFIG['database']['sqlite']['tables']['succession_plans']
        )
        
        # Prepare user tracking data
        user_email = user_access['user_id'] if user_access else 'SYSTEM'
        user_tier = user_access['tier'] if user_access else 0
        user_segments = json.dumps(user_access['segments']) if user_access else '[]'
        
        cursor.execute(query, (
            incumbent_data['EMPLOYEE_ID'],
            incumbent_data['PREFERRED_FIRST_NAME'],
            incumbent_data['PREFERRED_LAST_NAME'],
            incumbent_data.get('EMAIL_PRIMARY_WORK', ''),  # Default to empty string if not available
            incumbent_data.get('POSITION_TITLE', ''),  # Use POSITION_TITLE instead of POSITION_NBR_DESCRIPTION
            incumbent_data['MANAGEMENT_LEVEL'],
            incumbent_data['JOB_LEVEL'],
            incumbent_data['SEGMENT_HIER_LEVEL_2_NAME'],
            plan_details['critical_role'],
            plan_details['responsibilities'],
            json.dumps(plan_details['top_skills']),
            plan_details['top_ple'],
            plan_details.get('contract_end_date'),
            json.dumps(plan_details['sourcing_strategy']),
            plan_details.get('role_type'),
            plan_details['scenario_plan'],
            plan_details.get('new_position_title'),
            successor_data['EMPLOYEE_ID'],
            successor_data['PREFERRED_FIRST_NAME'],
            successor_data['PREFERRED_LAST_NAME'],
            successor_data.get('EMAIL_PRIMARY_WORK', ''),  # Default to empty string if not available
            successor_data.get('POSITION_TITLE', ''),  # Use POSITION_TITLE instead of POSITION_NBR_DESCRIPTION
            successor_data['MANAGEMENT_LEVEL'],
            successor_data['JOB_LEVEL'],
            successor_data['SEGMENT_HIER_LEVEL_2_NAME'],
            assessment_details['readiness'],
            assessment_details.get('future_readiness_timing'),
            assessment_details.get('contract_end_date'),
            assessment_details['strengths'],
            json.dumps(assessment_details['top_skills']),
            assessment_details['top_ple'],
            assessment_details['development_focus'],
            assessment_details['talent_actions'],
            False,  # REMOVED = FALSE for new records
            status,  # SUBMISSION_STATUS
            user_email,  # SUBMITTED_BY
            datetime.datetime.now() if status == 'submitted' else None,  # SUBMITTED_ON
            user_tier,  # USER_TIER (new field)
            user_segments  # USER_SEGMENTS (new field)
        ))
        
        # Get the generated RECORD_ID
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return str(record_id)  # Return as string for consistency
        
    except Exception as e:
        st.error(f"Database error: {e}")
        return None
