"""
Snowflake user access and permission management functions
"""

import pandas as pd
import json
import streamlit as st
from config.loader import CONFIG

def get_user_access_snowflake(email):
    """Get user access information from Snowflake user access table"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        
        # Query user access table in Snowflake
        query = """
            SELECT WORK_PRIMARY_EMAIL, USER_ID, EMPLOYEE_ID, HR_ACCESS,
                   TIER_1_ACCESS_IND, TIER_2_ACCESS_IND, TIER_3_ACCESS_IND,
                   SUCCESSION_PLAN_SEGMENT, LEADER_EMPLOYEE_ID
            FROM HR_EXPLORATORY.HR_DE_SANDBOX.USER_ACCESS
            WHERE UPPER(WORK_PRIMARY_EMAIL) = UPPER(%s)
        """
        
        df = pd.read_sql_query(query, conn, params=(email,))
        conn.close()
        
        if df.empty:
            return None
        
        user_data = df.iloc[0]
        
        # Determine tier
        tier = 1 if user_data['TIER_1_ACCESS_IND'] else (2 if user_data['TIER_2_ACCESS_IND'] else 3)
        
        # Parse JSON fields
        segments = json.loads(user_data['SUCCESSION_PLAN_SEGMENT']) if user_data['SUCCESSION_PLAN_SEGMENT'] else []
        leader_ids = json.loads(user_data['LEADER_EMPLOYEE_ID']) if user_data['LEADER_EMPLOYEE_ID'] else []
        
        return {
            'user_id': email,  # Use email as primary identifier (OIDC PK)
            'internal_user_id': user_data['USER_ID'],  # Keep internal ID for reference
            'employee_id': user_data['EMPLOYEE_ID'],
            'tier': tier,
            'hr_access': user_data['HR_ACCESS'],
            'segments': segments,
            'leader_employee_ids': leader_ids
        }
        
    except Exception as e:

        return None

def filter_incumbents_by_access_snowflake(search_results, user_access):
    """Filter incumbent search results based on user access level (Snowflake version)"""
    if not user_access or not search_results:
        return []
    
    tier = user_access['tier']
    
    # Tier 1: Can see all employees in their segments (enhanced filtering)
    if tier == 1:
        user_segments = user_access['segments']
        if not user_segments:  # If no segments specified, can see all
            return search_results
        
        filtered = []
        for person in search_results:
            person_segment = person.get('SEGMENT_HIER_LEVEL_2_NAME', '')
            if person_segment in user_segments:
                filtered.append(person)
        return filtered
    
    # Tier 2: Can see employees assigned to them in their segments
    elif tier == 2:
        user_segments = user_access['segments']
        leader_ids = user_access['leader_employee_ids']
        
        filtered = []
        for person in search_results:
            person_segment = person.get('SEGMENT_HIER_LEVEL_2_NAME', '')
            person_id = person.get('EMPLOYEE_ID', '')
            
            # Must be in user's segment AND in their leader list
            if person_segment in user_segments and person_id in leader_ids:
                filtered.append(person)
        return filtered
    
    # Tier 3: Can only see specific assigned employees (no search)
    elif tier == 3:
        leader_ids = user_access['leader_employee_ids']
        
        filtered = []
        for person in search_results:
            person_id = person.get('EMPLOYEE_ID', '')
            if person_id in leader_ids:
                filtered.append(person)
        return filtered
    
    return []

def get_all_incumbents_in_segments_snowflake(user_access):
    """Get all employees in user's segments (for Tier 1 users) from Snowflake"""
    if not user_access or user_access['tier'] != 1:
        return []
    
    try:
        conn = st.connection("snowflake", type="snowflake")
        
        user_segments = user_access['segments']
        if not user_segments:
            return []
        
        # Create placeholders for segments
        placeholders = ','.join([f"'{segment}'" for segment in user_segments])
        
        incumbents_table = CONFIG['database']['snowflake']['tables']['incumbents']
        query = f"""
            SELECT SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_FIRST_NAME,
                   PREFERRED_LAST_NAME, EMPLOYEE_ID, POSITION_ID,
                   POSITION_TITLE, MANAGEMENT_LEVEL, JOB_LEVEL,
                   DAYS_IN_MANAGEMENT_LEVEL, LEADER_NAME, HR_SEGMENT
            FROM {incumbents_table}
            WHERE SEGMENT_HIER_LEVEL_2_NAME IN ({placeholders})
            ORDER BY PREFERRED_LAST_NAME, PREFERRED_FIRST_NAME
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df.to_dict('records')
        
    except Exception as e:

        return []

def get_employee_planning_dashboard_snowflake(user_access):
    """Get comprehensive dashboard of all employees user can plan for with their planning status (Snowflake version)"""
    if not user_access:
        return pd.DataFrame()
    
    try:
        conn = st.connection("snowflake", type="snowflake")
        
        tier = user_access['tier']
        incumbents_table = CONFIG['database']['snowflake']['tables']['incumbents']
        
        # Get accessible employees based on tier
        if tier == 1:
            # Tier 1: All employees in their segments
            user_segments = user_access['segments']
            if not user_segments:
                return pd.DataFrame()
            
            placeholders = ','.join([f"'{segment}'" for segment in user_segments])
            employee_query = f"""
                SELECT SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_FIRST_NAME,
                       PREFERRED_LAST_NAME, EMPLOYEE_ID, POSITION_TITLE, 
                       MANAGEMENT_LEVEL, JOB_LEVEL, LEADER_NAME
                FROM {incumbents_table}
                WHERE SEGMENT_HIER_LEVEL_2_NAME IN ({placeholders})
                ORDER BY SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_LAST_NAME, PREFERRED_FIRST_NAME
            """
            
        elif tier == 2:
            # Tier 2: Only assigned employees in their segments
            user_segments = user_access['segments']
            leader_ids = user_access['leader_employee_ids']
            
            if not user_segments or not leader_ids:
                return pd.DataFrame()
            
            segment_placeholders = ','.join([f"'{segment}'" for segment in user_segments])
            leader_placeholders = ','.join([f"'{emp_id}'" for emp_id in leader_ids])
            
            employee_query = f"""
                SELECT SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_FIRST_NAME,
                       PREFERRED_LAST_NAME, EMPLOYEE_ID, POSITION_TITLE, 
                       MANAGEMENT_LEVEL, JOB_LEVEL, LEADER_NAME
                FROM {incumbents_table}
                WHERE SEGMENT_HIER_LEVEL_2_NAME IN ({segment_placeholders})
                AND EMPLOYEE_ID IN ({leader_placeholders})
                ORDER BY PREFERRED_LAST_NAME, PREFERRED_FIRST_NAME
            """
            
        elif tier == 3:
            # Tier 3: Only assigned incumbents
            leader_ids = user_access['leader_employee_ids']
            
            if not leader_ids:
                return pd.DataFrame()
            
            placeholders = ','.join([f"'{emp_id}'" for emp_id in leader_ids])
            employee_query = f"""
                SELECT SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_FIRST_NAME,
                       PREFERRED_LAST_NAME, EMPLOYEE_ID, POSITION_TITLE, 
                       MANAGEMENT_LEVEL, JOB_LEVEL, LEADER_NAME
                FROM {incumbents_table}
                WHERE EMPLOYEE_ID IN ({placeholders})
                ORDER BY PREFERRED_LAST_NAME, PREFERRED_FIRST_NAME
            """
        
        else:
            return pd.DataFrame()
        
        # Get employee data
        employees_df = pd.read_sql_query(employee_query, conn)
        
        if employees_df.empty:
            conn.close()
            return pd.DataFrame()
        
        # For now, return basic employee data without succession plan status
        # (succession plan status would require the succession_plans table in Snowflake)
        
        # Format the data for display
        employees_df['PLANNING_STATUS'] = 'not_planned'  # Default status
        employees_df['SUCCESSOR_COUNT'] = 0
        employees_df['LAST_UPDATED'] = None
        employees_df['UPDATED_BY'] = None
        employees_df['SUBMITTER_TIER'] = 0
        
        # Create status display
        employees_df['STATUS_DISPLAY'] = '⚪ Not Planned'
        
        # Select and rename columns for display
        display_columns = [
            'EMPLOYEE_ID', 'PREFERRED_FIRST_NAME', 'PREFERRED_LAST_NAME',
            'POSITION_TITLE', 'MANAGEMENT_LEVEL', 'JOB_LEVEL', 
            'SEGMENT_HIER_LEVEL_2_NAME', 'LEADER_NAME',
            'STATUS_DISPLAY', 'SUCCESSOR_COUNT', 'UPDATED_BY', 'SUBMITTER_TIER'
        ]
        
        result_df = employees_df[display_columns].copy()
        result_df.columns = [
            'Employee ID', 'First Name', 'Last Name', 'Position', 
            'Mgmt Level', 'Job Level', 'Segment', 'Leader',
            'Planning Status', 'Successors', 'Last Updated By', 'Tier'
        ]
        
        conn.close()
        return result_df
        
    except Exception as e:

        return pd.DataFrame()

def can_user_search_snowflake(user_access):
    """Check if user can search for employees (Snowflake version)"""
    if not user_access:
        return False
    return user_access['tier'] in [1, 2]

def can_user_submit_snowflake(user_access):
    """Check if user can submit succession plans (Snowflake version)"""
    if not user_access:
        return False
    return user_access['tier'] in [1, 2, 3]

def can_user_approve_snowflake(user_access):
    """Check if user can approve succession plans (Snowflake version)"""
    if not user_access:
        return False
    return user_access['tier'] == 1
