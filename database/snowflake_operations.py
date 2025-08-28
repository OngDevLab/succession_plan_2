"""
Snowflake database operations for succession planning with collaborative workflow support
Uses st.connection() and f-string formatting for Snowflake compatibility
"""

import json
import datetime
import pandas as pd
import streamlit as st
from config.loader import CONFIG

def search_incumbents_snowflake(search_term, search_type="last_name"):
    """Search incumbents in Snowflake"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        
        # Use the configured Snowflake table for incumbents
        table_name = CONFIG['database']['snowflake']['tables']['incumbents']
        
        if search_type == "last_name":
            query = f"""
            SELECT EMPLOYEE_ID, PREFERRED_FIRST_NAME, PREFERRED_LAST_NAME, POSITION_TITLE,
                   MANAGEMENT_LEVEL, JOB_LEVEL, SEGMENT_HIER_LEVEL_2_NAME, LEADER_NAME, HR_SEGMENT
            FROM {table_name}
            WHERE UPPER(PREFERRED_LAST_NAME) LIKE UPPER('%{search_term}%')
            ORDER BY PREFERRED_LAST_NAME, PREFERRED_FIRST_NAME
            LIMIT 50
            """
        else:  # full_name
            query = f"""
            SELECT EMPLOYEE_ID, PREFERRED_FIRST_NAME, PREFERRED_LAST_NAME, POSITION_TITLE,
                   MANAGEMENT_LEVEL, JOB_LEVEL, SEGMENT_HIER_LEVEL_2_NAME, LEADER_NAME, HR_SEGMENT
            FROM {table_name}
            WHERE UPPER(PREFERRED_FIRST_NAME || ' ' || PREFERRED_LAST_NAME) LIKE UPPER('%{search_term}%')
            ORDER BY PREFERRED_LAST_NAME, PREFERRED_FIRST_NAME
            LIMIT 50
            """
        
        df = conn.query(query)
        return df.to_dict('records') if not df.empty else []
        
    except Exception as e:
        st.error(f"Error searching incumbents in Snowflake: {e}")
        return []

def search_successors_snowflake(search_term, search_type="last_name"):
    """Search successors in Snowflake"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        
        # Use the configured Snowflake table for successors
        table_name = CONFIG['database']['snowflake']['tables']['successors']
        
        if search_type == "last_name":
            query = f"""
            SELECT EMPLOYEE_ID, PREFERRED_FIRST_NAME, PREFERRED_LAST_NAME, POSITION_TITLE,
                   MANAGEMENT_LEVEL, JOB_LEVEL, SEGMENT_HIER_LEVEL_2_NAME, LEADER_NAME, HR_SEGMENT
            FROM {table_name}
            WHERE UPPER(PREFERRED_LAST_NAME) LIKE UPPER('%{search_term}%')
            ORDER BY PREFERRED_LAST_NAME, PREFERRED_FIRST_NAME
            LIMIT 50
            """
        else:  # full_name
            query = f"""
            SELECT EMPLOYEE_ID, PREFERRED_FIRST_NAME, PREFERRED_LAST_NAME, POSITION_TITLE,
                   MANAGEMENT_LEVEL, JOB_LEVEL, SEGMENT_HIER_LEVEL_2_NAME, LEADER_NAME, HR_SEGMENT
            FROM {table_name}
            WHERE UPPER(PREFERRED_FIRST_NAME || ' ' || PREFERRED_LAST_NAME) LIKE UPPER('%{search_term}%')
            ORDER BY PREFERRED_LAST_NAME, PREFERRED_FIRST_NAME
            LIMIT 50
            """
        
        df = conn.query(query)
        return df.to_dict('records') if not df.empty else []
        
    except Exception as e:
        st.error(f"Error searching successors in Snowflake: {e}")
        return []

def get_latest_successor_values_snowflake(employee_id):
    """Get latest successor values from Snowflake for prepopulation"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        
        query = f"""
        SELECT "SUCCESSOR_READINESS", "SUCCESSOR_FUTURE_READINESS_TIMING", "SUCCESSOR_CONTRACT_END_DATE",
               "SUCCESSOR_STRENGTHS", "SUCCESSOR_TOP_SKILLS", "SUCCESSOR_TOP_PLE", 
               "SUCCESSOR_DEVELOPMENT_FOCUS", "SUCCESSOR_TALENT_ACTIONS"
        FROM "HR_STREAMLIT"."SUCCESSION_PLAN"."TBL_SL_SUCCESSION_PLAN_DETAIL"
        WHERE "SUCCESSOR_EMPLOYEE_ID" = '{employee_id}'
        AND "REMOVED" = FALSE
        ORDER BY "ROW_CREATED_ON" DESC
        LIMIT 1
        """
        
        df = conn.query(query)
        
        if not df.empty:
            result = df.iloc[0]
            
            # Helper function to safely parse JSON
            def safe_json_parse(value, default=None):
                if not value or pd.isna(value):
                    return default or []
                try:
                    return json.loads(value) if isinstance(value, str) else value
                except:
                    return default or []
            
            return {
                "readiness": result['SUCCESSOR_READINESS'],
                "future_readiness_timing": result['SUCCESSOR_FUTURE_READINESS_TIMING'],
                "contract_end_date": result['SUCCESSOR_CONTRACT_END_DATE'],
                "strengths": result['SUCCESSOR_STRENGTHS'],
                "top_skills": safe_json_parse(result['SUCCESSOR_TOP_SKILLS'], []),
                "top_ple": result['SUCCESSOR_TOP_PLE'],
                "development_focus": result['SUCCESSOR_DEVELOPMENT_FOCUS'],
                "talent_actions": result['SUCCESSOR_TALENT_ACTIONS']
            }
        return None
        
    except Exception as e:
        st.error(f"Error getting latest successor values from Snowflake: {e}")
        return None

def get_latest_successor_values_for_incumbent_snowflake(successor_employee_id, incumbent_employee_id):
    """Get latest successor values for specific incumbent from Snowflake"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        
        query = f"""
        SELECT "SUCCESSOR_READINESS", "SUCCESSOR_FUTURE_READINESS_TIMING", "SUCCESSOR_CONTRACT_END_DATE",
               "SUCCESSOR_STRENGTHS", "SUCCESSOR_TOP_SKILLS", "SUCCESSOR_TOP_PLE", 
               "SUCCESSOR_DEVELOPMENT_FOCUS", "SUCCESSOR_TALENT_ACTIONS"
        FROM "HR_STREAMLIT"."SUCCESSION_PLAN"."TBL_SL_SUCCESSION_PLAN_DETAIL"
        WHERE "SUCCESSOR_EMPLOYEE_ID" = '{successor_employee_id}'
        AND "INCUMBENT_EMPLOYEE_ID" = '{incumbent_employee_id}'
        AND "REMOVED" = FALSE
        ORDER BY "ROW_CREATED_ON" DESC
        LIMIT 1
        """
        
        df = conn.query(query)
        
        if not df.empty:
            result = df.iloc[0]
            
            # Helper function to safely parse JSON
            def safe_json_parse(value, default=None):
                if not value or pd.isna(value):
                    return default or []
                try:
                    return json.loads(value) if isinstance(value, str) else value
                except:
                    return default or []
            
            return {
                "readiness": result['SUCCESSOR_READINESS'],
                "future_readiness_timing": result['SUCCESSOR_FUTURE_READINESS_TIMING'],
                "contract_end_date": result['SUCCESSOR_CONTRACT_END_DATE'],
                "strengths": result['SUCCESSOR_STRENGTHS'],
                "top_skills": safe_json_parse(result['SUCCESSOR_TOP_SKILLS'], []),
                "top_ple": result['SUCCESSOR_TOP_PLE'],
                "development_focus": result['SUCCESSOR_DEVELOPMENT_FOCUS'],
                "talent_actions": result['SUCCESSOR_TALENT_ACTIONS']
            }
        return None
        
    except Exception as e:
        st.error(f"Error getting successor values for incumbent from Snowflake: {e}")
        return None

def save_succession_plan_snowflake(incumbent_data, successor_data, plan_details, assessment_details, user_access=None, status='saved'):
    """Save succession plan to Snowflake with collaborative workflow support"""
    try:
        # Connect to Snowflake using Streamlit's connection
        conn = st.connection("snowflake", type="snowflake")
        cursor = conn.cursor()
        
        # Prepare user tracking data (OIDC compliant)
        user_email = user_access['user_id'] if user_access else 'SYSTEM'
        user_tier = str(user_access['tier']) if user_access else '0'
        user_segments = json.dumps(user_access['segments']) if user_access else '[]'
        
        # Escape single quotes in string values
        def escape_sql_string(value):
            if value is None:
                return 'NULL'
            # Escape single quotes by doubling them
            escaped_value = str(value).replace("'", "''")
            return f"'{escaped_value}'"
        
        def escape_sql_boolean(value):
            return 'TRUE' if value else 'FALSE'
        
        def escape_sql_date(value):
            if value is None:
                return 'NULL'
            return f"'{value}'"
        
        def escape_sql_timestamp(value):
            if value is None:
                return 'NULL'
            return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
        
        # Prepare escaped values
        incumbent_employee_id = escape_sql_string(incumbent_data['EMPLOYEE_ID'])
        incumbent_first_name = escape_sql_string(incumbent_data['PREFERRED_FIRST_NAME'])
        incumbent_last_name = escape_sql_string(incumbent_data['PREFERRED_LAST_NAME'])
        incumbent_email = escape_sql_string(incumbent_data.get('EMAIL_PRIMARY_WORK', ''))
        incumbent_position_title = escape_sql_string(incumbent_data.get('POSITION_TITLE', ''))
        incumbent_management_level = escape_sql_string(incumbent_data['MANAGEMENT_LEVEL'])
        incumbent_job_level = escape_sql_string(incumbent_data['JOB_LEVEL'])
        incumbent_segment = escape_sql_string(incumbent_data['SEGMENT_HIER_LEVEL_2_NAME'])
        
        critical_role_ind = escape_sql_boolean(plan_details['critical_role'])
        incumbent_responsibilities = escape_sql_string(plan_details['responsibilities'])
        incumbent_top_skills = escape_sql_string(json.dumps(plan_details['top_skills']))
        incumbent_top_ple = escape_sql_string(plan_details['top_ple'])
        incumbent_contract_end_date = escape_sql_date(plan_details.get('contract_end_date'))
        incumbent_sourcing_strategy = escape_sql_string(json.dumps(plan_details['sourcing_strategy']))
        incumbent_role_type = escape_sql_string(plan_details.get('role_type'))
        incumbent_scenario_plan = escape_sql_string(plan_details['scenario_plan'])
        incumbent_additional_position_title = escape_sql_string(plan_details.get('new_position_title'))
        
        successor_employee_id = escape_sql_string(successor_data['EMPLOYEE_ID'])
        successor_first_name = escape_sql_string(successor_data['PREFERRED_FIRST_NAME'])
        successor_last_name = escape_sql_string(successor_data['PREFERRED_LAST_NAME'])
        successor_email = escape_sql_string(successor_data.get('EMAIL_PRIMARY_WORK', ''))
        successor_position_title = escape_sql_string(successor_data.get('POSITION_TITLE', ''))
        successor_management_level = escape_sql_string(successor_data['MANAGEMENT_LEVEL'])
        successor_job_level = escape_sql_string(successor_data['JOB_LEVEL'])
        successor_segment = escape_sql_string(successor_data['SEGMENT_HIER_LEVEL_2_NAME'])
        
        successor_readiness = escape_sql_string(assessment_details['readiness'])
        successor_future_readiness_timing = escape_sql_string(assessment_details.get('future_readiness_timing'))
        successor_contract_end_date = escape_sql_date(assessment_details.get('contract_end_date'))
        successor_strengths = escape_sql_string(assessment_details['strengths'])
        successor_top_skills = escape_sql_string(json.dumps(assessment_details['top_skills']))
        successor_top_ple = escape_sql_string(assessment_details['top_ple'])
        successor_development_focus = escape_sql_string(assessment_details['development_focus'])
        successor_talent_actions = escape_sql_string(assessment_details['talent_actions'])
        
        removed = escape_sql_boolean(False)
        succession_plan_status = escape_sql_string(status)
        submitted_by = escape_sql_string(user_email) if status == 'submitted' else 'NULL'
        submitted_on = escape_sql_timestamp(datetime.datetime.now()) if status == 'submitted' else 'NULL'
        
        row_created_by = escape_sql_string(user_email)
        row_created_tier = escape_sql_string(user_tier)
        row_created_user_segments = escape_sql_string(user_segments)
        
        # Insert query using f-string formatting
        insert_sql = f"""
        INSERT INTO "HR_STREAMLIT"."SUCCESSION_PLAN"."TBL_SL_SUCCESSION_PLAN_DETAIL" (
            "INCUMBENT_EMPLOYEE_ID", "INCUMBENT_FIRST_NAME", "INCUMBENT_LAST_NAME", "INCUMBENT_EMAIL",
            "INCUMBENT_POSITION_TITLE", "INCUMBENT_MANAGEMENT_LEVEL", "INCUMBENT_JOB_LEVEL", "INCUMBENT_SEGMENT",
            "CRITICAL_ROLE_IND", "INCUMBENT_ROLE_RESPONSIBILITIES", "INCUMBENT_TOP_SKILLS", "INCUMBENT_TOP_PLE",
            "INCUMBENT_CONTRACT_END_DATE", "INCUMBENT_SOURCING_STRATEGY", "INCUMBENT_ROLE_TYPE", 
            "INCUMBENT_ROLE_SCENARIO_PLAN", "INCUMBENT_ADDITIONAL_POSITION_TITLE",
            "SUCCESSOR_EMPLOYEE_ID", "SUCCESSOR_FIRST_NAME", "SUCCESSOR_LAST_NAME", "SUCCESSOR_EMAIL",
            "SUCCESSOR_POSITION_TITLE", "SUCCESSOR_MANAGEMENT_LEVEL", "SUCCESSOR_JOB_LEVEL", "SUCCESSOR_SEGMENT",
            "SUCCESSOR_READINESS", "SUCCESSOR_FUTURE_READINESS_TIMING", "SUCCESSOR_CONTRACT_END_DATE",
            "SUCCESSOR_STRENGTHS", "SUCCESSOR_TOP_SKILLS", "SUCCESSOR_TOP_PLE", 
            "SUCCESSOR_DEVELOPMENT_FOCUS", "SUCCESSOR_TALENT_ACTIONS",
            "REMOVED", "SUCCESSION_PLAN_STATUS", "SUBMITTED_BY", "SUBMITTED_ON",
            "ROW_CREATED_BY", "ROW_CREATED_TIER", "ROW_CREATED_USER_SEGMENTS"
        ) VALUES (
            {incumbent_employee_id}, {incumbent_first_name}, {incumbent_last_name}, {incumbent_email},
            {incumbent_position_title}, {incumbent_management_level}, {incumbent_job_level}, {incumbent_segment},
            {critical_role_ind}, {incumbent_responsibilities}, {incumbent_top_skills}, {incumbent_top_ple},
            {incumbent_contract_end_date}, {incumbent_sourcing_strategy}, {incumbent_role_type},
            {incumbent_scenario_plan}, {incumbent_additional_position_title},
            {successor_employee_id}, {successor_first_name}, {successor_last_name}, {successor_email},
            {successor_position_title}, {successor_management_level}, {successor_job_level}, {successor_segment},
            {successor_readiness}, {successor_future_readiness_timing}, {successor_contract_end_date},
            {successor_strengths}, {successor_top_skills}, {successor_top_ple},
            {successor_development_focus}, {successor_talent_actions},
            {removed}, {succession_plan_status}, {submitted_by}, {submitted_on},
            {row_created_by}, {row_created_tier}, {row_created_user_segments}
        )
        """
        
        cursor.execute(insert_sql)
        st.success("Succession plan saved to Snowflake!")
        
        # Note: Snowflake auto-increment ID retrieval may vary
        # You might need to adjust this based on your Snowflake setup
        return "snowflake_record_saved"
        
    except Exception as e:
        st.error(f"Snowflake save error: {e}")
        return None

def get_latest_incumbent_values_snowflake(employee_id):
    """Get latest incumbent values from Snowflake for prepopulation"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        
        query = f"""
        SELECT "CRITICAL_ROLE_IND", "INCUMBENT_ROLE_RESPONSIBILITIES", "INCUMBENT_TOP_SKILLS", 
               "INCUMBENT_TOP_PLE", "INCUMBENT_CONTRACT_END_DATE", "INCUMBENT_SOURCING_STRATEGY",
               "INCUMBENT_ROLE_TYPE", "INCUMBENT_ROLE_SCENARIO_PLAN", "INCUMBENT_ADDITIONAL_POSITION_TITLE"
        FROM "HR_STREAMLIT"."SUCCESSION_PLAN"."TBL_SL_SUCCESSION_PLAN_DETAIL"
        WHERE "INCUMBENT_EMPLOYEE_ID" = '{employee_id}'
        AND "REMOVED" = FALSE
        ORDER BY "ROW_CREATED_ON" DESC
        LIMIT 1
        """
        
        df = conn.query(query)
        
        if not df.empty:
            result = df.iloc[0]
            
            # Helper function to safely parse JSON
            def safe_json_parse(value, default=None):
                if not value or pd.isna(value):
                    return default or []
                try:
                    return json.loads(value) if isinstance(value, str) else value
                except:
                    return default or []
            
            return {
                "critical_role": result['CRITICAL_ROLE_IND'],
                "responsibilities": result['INCUMBENT_ROLE_RESPONSIBILITIES'],
                "top_skills": safe_json_parse(result['INCUMBENT_TOP_SKILLS'], []),
                "top_ple": result['INCUMBENT_TOP_PLE'],
                "contract_end_date": result['INCUMBENT_CONTRACT_END_DATE'],
                "sourcing_strategy": safe_json_parse(result['INCUMBENT_SOURCING_STRATEGY'], []),
                "role_type": result['INCUMBENT_ROLE_TYPE'],
                "scenario_plan": result['INCUMBENT_ROLE_SCENARIO_PLAN'],
                "new_position_title": result['INCUMBENT_ADDITIONAL_POSITION_TITLE']
            }
        return None
        
    except Exception as e:
        st.error(f"Error getting latest incumbent values from Snowflake: {e}")
        return None

def get_collaborative_incumbent_values_snowflake(employee_id, user_access):
    """Get incumbent values for collaborative editing from Snowflake"""
    if not user_access:
        return None
    
    try:
        conn = st.connection("snowflake", type="snowflake")
        
        user_tier = user_access['tier']
        user_email = user_access['user_id']
        
        if user_tier == 1:
            # Tier 1: Can see any submission (for review)
            query = f"""
            SELECT "CRITICAL_ROLE_IND", "INCUMBENT_ROLE_RESPONSIBILITIES", "INCUMBENT_TOP_SKILLS", 
                   "INCUMBENT_TOP_PLE", "INCUMBENT_CONTRACT_END_DATE", "INCUMBENT_SOURCING_STRATEGY",
                   "INCUMBENT_ROLE_TYPE", "INCUMBENT_ROLE_SCENARIO_PLAN", "INCUMBENT_ADDITIONAL_POSITION_TITLE",
                   "SUCCESSION_PLAN_STATUS", "SUBMITTED_BY", "ROW_CREATED_TIER"
            FROM "HR_STREAMLIT"."SUCCESSION_PLAN"."TBL_SL_SUCCESSION_PLAN_DETAIL"
            WHERE "INCUMBENT_EMPLOYEE_ID" = '{employee_id}'
            AND "REMOVED" = FALSE
            ORDER BY "ROW_CREATED_ON" DESC
            LIMIT 1
            """
            
        elif user_tier in [2, 3]:
            # Tier 2/3: Complex visibility rules
            query = f"""
            WITH latest_submission AS (
                SELECT * FROM "HR_STREAMLIT"."SUCCESSION_PLAN"."TBL_SL_SUCCESSION_PLAN_DETAIL"
                WHERE "INCUMBENT_EMPLOYEE_ID" = '{employee_id}'
                AND "REMOVED" = FALSE
                AND "SUCCESSION_PLAN_STATUS" IN ('submitted', 'approved')
                ORDER BY "ROW_CREATED_ON" DESC
                LIMIT 1
            ),
            user_draft AS (
                SELECT * FROM "HR_STREAMLIT"."SUCCESSION_PLAN"."TBL_SL_SUCCESSION_PLAN_DETAIL"
                WHERE "INCUMBENT_EMPLOYEE_ID" = '{employee_id}'
                AND "SUBMITTED_BY" = '{user_email}'
                AND "REMOVED" = FALSE
                AND "SUCCESSION_PLAN_STATUS" IN ('saved', 'needs_edit')
                ORDER BY "ROW_CREATED_ON" DESC
                LIMIT 1
            )
            SELECT "CRITICAL_ROLE_IND", "INCUMBENT_ROLE_RESPONSIBILITIES", "INCUMBENT_TOP_SKILLS", 
                   "INCUMBENT_TOP_PLE", "INCUMBENT_CONTRACT_END_DATE", "INCUMBENT_SOURCING_STRATEGY",
                   "INCUMBENT_ROLE_TYPE", "INCUMBENT_ROLE_SCENARIO_PLAN", "INCUMBENT_ADDITIONAL_POSITION_TITLE",
                   "SUCCESSION_PLAN_STATUS", "SUBMITTED_BY", "ROW_CREATED_TIER", 'submitted' as source_type
            FROM latest_submission
            WHERE EXISTS (SELECT 1 FROM latest_submission)
            
            UNION ALL
            
            SELECT "CRITICAL_ROLE_IND", "INCUMBENT_ROLE_RESPONSIBILITIES", "INCUMBENT_TOP_SKILLS", 
                   "INCUMBENT_TOP_PLE", "INCUMBENT_CONTRACT_END_DATE", "INCUMBENT_SOURCING_STRATEGY",
                   "INCUMBENT_ROLE_TYPE", "INCUMBENT_ROLE_SCENARIO_PLAN", "INCUMBENT_ADDITIONAL_POSITION_TITLE",
                   "SUCCESSION_PLAN_STATUS", "SUBMITTED_BY", "ROW_CREATED_TIER", 'draft' as source_type
            FROM user_draft
            WHERE NOT EXISTS (SELECT 1 FROM latest_submission)
            
            ORDER BY source_type DESC
            LIMIT 1
            """
        
        df = conn.query(query)
        
        if not df.empty:
            result = df.iloc[0]
            
            # Helper function to safely parse JSON
            def safe_json_parse(value, default=None):
                if not value or pd.isna(value):
                    return default or []
                try:
                    return json.loads(value) if isinstance(value, str) else value
                except:
                    return default or []
            
            plan_data = {
                "critical_role": result['CRITICAL_ROLE_IND'],
                "responsibilities": result['INCUMBENT_ROLE_RESPONSIBILITIES'],
                "top_skills": safe_json_parse(result['INCUMBENT_TOP_SKILLS'], []),
                "top_ple": result['INCUMBENT_TOP_PLE'],
                "contract_end_date": result['INCUMBENT_CONTRACT_END_DATE'],
                "sourcing_strategy": safe_json_parse(result['INCUMBENT_SOURCING_STRATEGY'], []),
                "role_type": result['INCUMBENT_ROLE_TYPE'],
                "scenario_plan": result['INCUMBENT_ROLE_SCENARIO_PLAN'],
                "new_position_title": result['INCUMBENT_ADDITIONAL_POSITION_TITLE']
            }
            
            # Add metadata about the source
            metadata = {
                "submission_status": result['SUCCESSION_PLAN_STATUS'],
                "submitted_by": result['SUBMITTED_BY'],
                "submitter_tier": result['ROW_CREATED_TIER'],
                "source_type": result.get('SOURCE_TYPE', "unknown")
            }
            
            return {
                "plan_details": plan_data,
                "metadata": metadata
            }
        
        return None
        
    except Exception as e:
        st.error(f"Error getting collaborative incumbent values from Snowflake: {e}")
        return None

def approve_submission_snowflake(incumbent_employee_id, approver_user_access):
    """Approve a Tier 2/3 submission in Snowflake"""
    if not approver_user_access or approver_user_access['tier'] != 1:
        return False
    
    try:
        conn = st.connection("snowflake", type="snowflake")
        cursor = conn.cursor()
        
        approver_email = approver_user_access['user_id'].replace("'", "''")
        current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update submission status to approved
        update_sql = f"""
            UPDATE "HR_STREAMLIT"."SUCCESSION_PLAN"."TBL_SL_SUCCESSION_PLAN_DETAIL"
            SET "SUCCESSION_PLAN_STATUS" = 'approved',
                "APPROVED_BY" = '{approver_email}',
                "APPROVED_ON" = '{current_timestamp}'
            WHERE "INCUMBENT_EMPLOYEE_ID" = '{incumbent_employee_id}' 
            AND "SUCCESSION_PLAN_STATUS" = 'submitted'
            AND "ROW_CREATED_TIER" IN ('2', '3')
            AND "REMOVED" = FALSE
        """
        
        cursor.execute(update_sql)
        st.success("Submission approved in Snowflake!")
        return True
        
    except Exception as e:
        st.error(f"Error approving submission in Snowflake: {e}")
        return False

def request_edits_snowflake(incumbent_employee_id, requester_user_access):
    """Request edits on a Tier 2/3 submission in Snowflake"""
    if not requester_user_access or requester_user_access['tier'] != 1:
        return False
    
    try:
        conn = st.connection("snowflake", type="snowflake")
        cursor = conn.cursor()
        
        requester_email = requester_user_access['user_id'].replace("'", "''")
        current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update submission status to needs_edit
        update_sql = f"""
            UPDATE "HR_STREAMLIT"."SUCCESSION_PLAN"."TBL_SL_SUCCESSION_PLAN_DETAIL"
            SET "SUCCESSION_PLAN_STATUS" = 'needs_edit',
                "EDIT_REQUESTED_BY" = '{requester_email}',
                "EDIT_REQUESTED_ON" = '{current_timestamp}'
            WHERE "INCUMBENT_EMPLOYEE_ID" = '{incumbent_employee_id}' 
            AND "SUCCESSION_PLAN_STATUS" IN ('submitted', 'approved')
            AND ("ROW_CREATED_TIER" IN ('2', '3') OR ("ROW_CREATED_TIER" = '1' AND "SUCCESSION_PLAN_STATUS" = 'approved'))
            AND "REMOVED" = FALSE
        """
        
        cursor.execute(update_sql)
        st.success("Edit request sent in Snowflake!")
        return True
        
    except Exception as e:
        st.error(f"Error requesting edits in Snowflake: {e}")
        return False

def reopen_approved_plan_snowflake(incumbent_employee_id, requester_user_access):
    """Reopen an approved plan for editing in Snowflake"""
    if not requester_user_access or requester_user_access['tier'] != 1:
        return False
    
    try:
        conn = st.connection("snowflake", type="snowflake")
        cursor = conn.cursor()
        
        requester_email = requester_user_access['user_id'].replace("'", "''")
        current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Change status from 'approved' back to 'needs_edit'
        update_sql = f"""
            UPDATE "HR_STREAMLIT"."SUCCESSION_PLAN"."TBL_SL_SUCCESSION_PLAN_DETAIL"
            SET "SUCCESSION_PLAN_STATUS" = 'needs_edit',
                "EDIT_REQUESTED_BY" = '{requester_email}',
                "EDIT_REQUESTED_ON" = '{current_timestamp}'
            WHERE "INCUMBENT_EMPLOYEE_ID" = '{incumbent_employee_id}' 
            AND "SUCCESSION_PLAN_STATUS" = 'approved'
            AND "REMOVED" = FALSE
        """
        
        cursor.execute(update_sql)
        st.success("Approved plan reopened for editing in Snowflake!")
        return True
        
    except Exception as e:
        st.error(f"Error reopening approved plan in Snowflake: {e}")
        return False

def test_snowflake_connection():
    """Test Snowflake connection and return status"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        # Simple test query
        df = conn.query("SELECT 1 as test_connection")
        if not df.empty:
            return True, "Connected"
        else:
            return False, "Connection failed"
    except Exception as e:
        return False, f"Error: {str(e)}"

# Set availability flag
SNOWFLAKE_AVAILABLE = True  # Assume available since we're using st.connection
