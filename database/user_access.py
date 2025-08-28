"""
User access and permission management functions
"""

import sqlite3
import json
import pandas as pd
import datetime
import streamlit as st
from config.loader import CONFIG
from utils.formatters import format_management_level, format_employee_name

def get_user_access(user_email):
    """Get user access information by email"""
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['employee_db'])
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT USER_ID, EMPLOYEE_ID, HR_ACCESS,
                   TIER_1_ACCESS_IND, TIER_2_ACCESS_IND, TIER_3_ACCESS_IND,
                   SUCCESSION_PLAN_SEGMENT, LEADER_EMPLOYEE_ID
            FROM user_access 
            WHERE WORK_PRIMARY_EMAIL = ?
        """, (user_email,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, employee_id, hr_access, tier1, tier2, tier3, segments_json, leaders_json = result
            
            # Parse JSON arrays
            segments = json.loads(segments_json) if segments_json else []
            leader_ids = json.loads(leaders_json) if leaders_json else []
            
            return {
                'user_id': user_email,  # Use email as primary identifier (OIDC PK)
                'internal_user_id': user_id,  # Keep internal ID for reference
                'employee_id': employee_id,
                'hr_access': hr_access,
                'tier_1': tier1,
                'tier_2': tier2,
                'tier_3': tier3,
                'segments': segments,
                'leader_employee_ids': leader_ids,
                'tier': 1 if tier1 else (2 if tier2 else (3 if tier3 else 0))
            }
        
        return None
        
    except Exception as e:
        return None

def get_all_test_users():
    """Get all test users for dropdown selection"""
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['employee_db'])
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT WORK_PRIMARY_EMAIL, USER_ID,
                   TIER_1_ACCESS_IND, TIER_2_ACCESS_IND, TIER_3_ACCESS_IND,
                   SUCCESSION_PLAN_SEGMENT, LEADER_EMPLOYEE_ID
            FROM user_access 
            ORDER BY TIER_1_ACCESS_IND DESC, TIER_2_ACCESS_IND DESC, TIER_3_ACCESS_IND DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            email, user_id, tier1, tier2, tier3, segments_json, leaders_json = row
            
            segments = json.loads(segments_json) if segments_json else []
            leader_ids = json.loads(leaders_json) if leaders_json else []
            
            tier = 1 if tier1 else (2 if tier2 else (3 if tier3 else 0))
            
            # Create display name
            display_name = f"Tier {tier} - {email} ({len(segments)} segments, {len(leader_ids)} employees)"
            
            users.append({
                'email': email,
                'display_name': display_name,
                'tier': tier,
                'segments': segments,
                'leader_ids': leader_ids
            })
        
        conn.close()
        return users
        
    except Exception as e:
        return []

def filter_incumbents_by_access(search_results, user_access):
    """Filter incumbent search results based on user access level"""
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

def get_all_incumbents_in_segments(user_access):
    """Get all employees in user's segments (for Tier 1 users)"""
    if not user_access or user_access['tier'] != 1:
        return []
    
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['employee_db'])
        
        user_segments = user_access['segments']
        if not user_segments:
            return []
        
        placeholders = ','.join(['?' for _ in user_segments])
        query = f"""
            SELECT SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_FIRST_NAME,
                   PREFERRED_LAST_NAME, EMPLOYEE_ID, POSITION_ID,
                   POSITION_TITLE, MANAGEMENT_LEVEL, JOB_LEVEL,
                   DAYS_IN_MANAGEMENT_LEVEL, LEADER_NAME, HR_SEGMENT
            FROM incumbents
            WHERE SEGMENT_HIER_LEVEL_2_NAME IN ({placeholders})
            ORDER BY PREFERRED_LAST_NAME, PREFERRED_FIRST_NAME
        """
        
        df = pd.read_sql_query(query, conn, params=user_segments)
        conn.close()
        
        return df.to_dict('records')
        
    except Exception as e:
        return []

def get_collaborative_incumbent_values(employee_id, user_access):
    """Get incumbent values for collaborative editing with proper visibility rules"""
    if not user_access:
        return None
    
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        cursor = conn.cursor()
        
        user_tier = user_access['tier']
        user_email = user_access['user_id']
        
        # Different visibility rules based on user tier and submission status
        if user_tier == 1:
            # Tier 1: Can see any submission in their segments (for review)
            query = """
                SELECT CRITICAL_ROLE, RESPONSIBILITIES, INCUMBENT_TOP_SKILLS, INCUMBENT_TOP_PLE,
                       INCUMBENT_CONTRACT_END_DATE, SOURCING_STRATEGY, ROLE_TYPE, SCENARIO_PLAN,
                       NEW_POSITION_TITLE, SUBMISSION_STATUS, SUBMITTED_BY, USER_TIER
                FROM succession_plans 
                WHERE INCUMBENT_EMPLOYEE_ID = ?
                AND REMOVED = FALSE
                ORDER BY CREATED_AT DESC
                LIMIT 1
            """
            cursor.execute(query, (employee_id,))
            
        elif user_tier in [2, 3]:
            # Tier 2/3: Complex visibility rules
            query = """
                WITH latest_submission AS (
                    SELECT * FROM succession_plans
                    WHERE INCUMBENT_EMPLOYEE_ID = ?
                    AND REMOVED = FALSE
                    AND SUBMISSION_STATUS IN ('submitted', 'approved')
                    ORDER BY CREATED_AT DESC
                    LIMIT 1
                ),
                user_draft AS (
                    SELECT * FROM succession_plans
                    WHERE INCUMBENT_EMPLOYEE_ID = ?
                    AND SUBMITTED_BY = ?
                    AND REMOVED = FALSE
                    AND SUBMISSION_STATUS IN ('saved', 'needs_edit')
                    ORDER BY CREATED_AT DESC
                    LIMIT 1
                )
                SELECT CRITICAL_ROLE, RESPONSIBILITIES, INCUMBENT_TOP_SKILLS, INCUMBENT_TOP_PLE,
                       INCUMBENT_CONTRACT_END_DATE, SOURCING_STRATEGY, ROLE_TYPE, SCENARIO_PLAN,
                       NEW_POSITION_TITLE, SUBMISSION_STATUS, SUBMITTED_BY, USER_TIER,
                       'submitted' as source_type
                FROM latest_submission
                WHERE EXISTS (SELECT 1 FROM latest_submission)
                
                UNION ALL
                
                SELECT CRITICAL_ROLE, RESPONSIBILITIES, INCUMBENT_TOP_SKILLS, INCUMBENT_TOP_PLE,
                       INCUMBENT_CONTRACT_END_DATE, SOURCING_STRATEGY, ROLE_TYPE, SCENARIO_PLAN,
                       NEW_POSITION_TITLE, SUBMISSION_STATUS, SUBMITTED_BY, USER_TIER,
                       'draft' as source_type
                FROM user_draft
                WHERE NOT EXISTS (SELECT 1 FROM latest_submission)
                
                ORDER BY source_type DESC
                LIMIT 1
            """
            cursor.execute(query, (employee_id, employee_id, user_email))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Helper function to safely parse JSON
            def safe_json_parse(value, default=None):
                if not value:
                    return default or []
                try:
                    return json.loads(value) if isinstance(value, str) else value
                except:
                    return default or []
            
            plan_data = {
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
            
            # Add metadata about the source
            metadata = {
                "submission_status": result[9],
                "submitted_by": result[10],
                "submitter_tier": result[11],
                "source_type": result[12] if len(result) > 12 else "unknown"
            }
            
            return {
                "plan_details": plan_data,
                "metadata": metadata
            }
        
        return None
        
    except Exception as e:

        return None

def get_collaborative_planning_data(incumbent_employee_id, user_access):
    """Get the latest collaborative planning data for an incumbent that the user can access"""
    if not user_access:
        return None
    
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        
        # Get the latest succession plan data for this incumbent
        # Include all records from users who have access to this incumbent
        query = """
            WITH latest_incumbent_plan AS (
                SELECT * FROM succession_plans
                WHERE INCUMBENT_EMPLOYEE_ID = ?
                AND REMOVED = FALSE
                ORDER BY CREATED_AT DESC
                LIMIT 1
            ),
            latest_successors AS (
                SELECT DISTINCT 
                    SUCCESSOR_EMPLOYEE_ID,
                    MAX(CREATED_AT) as latest_created_at
                FROM succession_plans
                WHERE INCUMBENT_EMPLOYEE_ID = ?
                AND REMOVED = FALSE
                GROUP BY SUCCESSOR_EMPLOYEE_ID
            ),
            current_successors AS (
                SELECT sp.*
                FROM succession_plans sp
                INNER JOIN latest_successors ls ON 
                    sp.SUCCESSOR_EMPLOYEE_ID = ls.SUCCESSOR_EMPLOYEE_ID 
                    AND sp.CREATED_AT = ls.latest_created_at
                WHERE sp.INCUMBENT_EMPLOYEE_ID = ?
                AND sp.REMOVED = FALSE
            )
            SELECT 
                'incumbent' as record_type,
                INCUMBENT_EMPLOYEE_ID, INCUMBENT_FIRST_NAME, INCUMBENT_LAST_NAME,
                INCUMBENT_POSITION, INCUMBENT_MANAGEMENT_LEVEL, INCUMBENT_JOB_LEVEL,
                INCUMBENT_SEGMENT, CRITICAL_ROLE, RESPONSIBILITIES, INCUMBENT_TOP_SKILLS,
                INCUMBENT_TOP_PLE, INCUMBENT_CONTRACT_END_DATE, SOURCING_STRATEGY,
                ROLE_TYPE, SCENARIO_PLAN, NEW_POSITION_TITLE,
                NULL as SUCCESSOR_EMPLOYEE_ID, NULL as SUCCESSOR_FIRST_NAME, NULL as SUCCESSOR_LAST_NAME,
                NULL as SUCCESSOR_POSITION, NULL as SUCCESSOR_MANAGEMENT_LEVEL, NULL as SUCCESSOR_JOB_LEVEL,
                NULL as SUCCESSOR_SEGMENT, NULL as SUCCESSOR_READINESS, NULL as SUCCESSOR_FUTURE_READINESS_TIMING,
                NULL as SUCCESSOR_CONTRACT_END_DATE, NULL as SUCCESSOR_STRENGTHS, NULL as SUCCESSOR_TOP_SKILLS,
                NULL as SUCCESSOR_TOP_PLE, NULL as SUCCESSOR_DEVELOPMENT_FOCUS, NULL as SUCCESSOR_TALENT_ACTIONS,
                SUBMITTED_BY, USER_TIER, CREATED_AT, SUBMISSION_STATUS
            FROM latest_incumbent_plan
            
            UNION ALL
            
            SELECT 
                'successor' as record_type,
                INCUMBENT_EMPLOYEE_ID, INCUMBENT_FIRST_NAME, INCUMBENT_LAST_NAME,
                INCUMBENT_POSITION, INCUMBENT_MANAGEMENT_LEVEL, INCUMBENT_JOB_LEVEL,
                INCUMBENT_SEGMENT, CRITICAL_ROLE, RESPONSIBILITIES, INCUMBENT_TOP_SKILLS,
                INCUMBENT_TOP_PLE, INCUMBENT_CONTRACT_END_DATE, SOURCING_STRATEGY,
                ROLE_TYPE, SCENARIO_PLAN, NEW_POSITION_TITLE,
                SUCCESSOR_EMPLOYEE_ID, SUCCESSOR_FIRST_NAME, SUCCESSOR_LAST_NAME,
                SUCCESSOR_POSITION, SUCCESSOR_MANAGEMENT_LEVEL, SUCCESSOR_JOB_LEVEL,
                SUCCESSOR_SEGMENT, SUCCESSOR_READINESS, SUCCESSOR_FUTURE_READINESS_TIMING,
                SUCCESSOR_CONTRACT_END_DATE, SUCCESSOR_STRENGTHS, SUCCESSOR_TOP_SKILLS,
                SUCCESSOR_TOP_PLE, SUCCESSOR_DEVELOPMENT_FOCUS, SUCCESSOR_TALENT_ACTIONS,
                SUBMITTED_BY, USER_TIER, CREATED_AT, SUBMISSION_STATUS
            FROM current_successors
            ORDER BY record_type, CREATED_AT DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(incumbent_employee_id, incumbent_employee_id, incumbent_employee_id))
        conn.close()
        
        if df.empty:
            return None
        
        # Separate incumbent and successor records
        incumbent_records = df[df['record_type'] == 'incumbent']
        successor_records = df[df['record_type'] == 'successor']
        
        result = {
            'incumbent': None,
            'successors': [],
            'collaboration_info': {
                'contributors': [],
                'last_updated': None,
                'total_successors': len(successor_records)
            }
        }
        
        # Build incumbent data from latest record
        if not incumbent_records.empty:
            inc_row = incumbent_records.iloc[0]
            result['incumbent'] = {
                'metadata': {
                    'EMPLOYEE_ID': inc_row['INCUMBENT_EMPLOYEE_ID'],
                    'PREFERRED_FIRST_NAME': inc_row['INCUMBENT_FIRST_NAME'],
                    'PREFERRED_LAST_NAME': inc_row['INCUMBENT_LAST_NAME'],
                    'POSITION_TITLE': inc_row['INCUMBENT_POSITION'],
                    'MANAGEMENT_LEVEL': inc_row['INCUMBENT_MANAGEMENT_LEVEL'],
                    'JOB_LEVEL': inc_row['INCUMBENT_JOB_LEVEL'],
                    'SEGMENT_HIER_LEVEL_2_NAME': inc_row['INCUMBENT_SEGMENT']
                },
                'plan_details': {
                    'critical_role': inc_row['CRITICAL_ROLE'],
                    'responsibilities': inc_row['RESPONSIBILITIES'],
                    'top_skills': json.loads(inc_row['INCUMBENT_TOP_SKILLS']) if inc_row['INCUMBENT_TOP_SKILLS'] else [],
                    'top_ple': inc_row['INCUMBENT_TOP_PLE'],
                    'contract_end_date': inc_row['INCUMBENT_CONTRACT_END_DATE'],
                    'sourcing_strategy': json.loads(inc_row['SOURCING_STRATEGY']) if inc_row['SOURCING_STRATEGY'] else [],
                    'role_type': inc_row['ROLE_TYPE'],
                    'scenario_plan': inc_row['SCENARIO_PLAN'],
                    'new_position_title': inc_row['NEW_POSITION_TITLE']
                }
            }
            
            result['collaboration_info']['last_updated'] = inc_row['CREATED_AT']
        
        # Build successor data from latest records for each successor
        contributors = set()
        for _, succ_row in successor_records.iterrows():
            successor = {
                'metadata': {
                    'EMPLOYEE_ID': succ_row['SUCCESSOR_EMPLOYEE_ID'],
                    'PREFERRED_FIRST_NAME': succ_row['SUCCESSOR_FIRST_NAME'],
                    'PREFERRED_LAST_NAME': succ_row['SUCCESSOR_LAST_NAME'],
                    'POSITION_TITLE': succ_row['SUCCESSOR_POSITION'],
                    'MANAGEMENT_LEVEL': succ_row['SUCCESSOR_MANAGEMENT_LEVEL'],
                    'JOB_LEVEL': succ_row['SUCCESSOR_JOB_LEVEL'],
                    'SEGMENT_HIER_LEVEL_2_NAME': succ_row['SUCCESSOR_SEGMENT']
                },
                'assessment': {
                    'readiness': succ_row['SUCCESSOR_READINESS'],
                    'future_readiness_timing': succ_row['SUCCESSOR_FUTURE_READINESS_TIMING'],
                    'contract_end_date': succ_row['SUCCESSOR_CONTRACT_END_DATE'],
                    'strengths': succ_row['SUCCESSOR_STRENGTHS'],
                    'top_skills': json.loads(succ_row['SUCCESSOR_TOP_SKILLS']) if succ_row['SUCCESSOR_TOP_SKILLS'] else [],
                    'top_ple': succ_row['SUCCESSOR_TOP_PLE'],
                    'development_focus': succ_row['SUCCESSOR_DEVELOPMENT_FOCUS'],
                    'talent_actions': succ_row['SUCCESSOR_TALENT_ACTIONS']
                },
                'contributor_info': {
                    'added_by': succ_row['SUBMITTED_BY'],
                    'user_tier': succ_row['USER_TIER'],
                    'added_on': succ_row['CREATED_AT'],
                    'status': succ_row['SUBMISSION_STATUS']
                }
            }
            
            result['successors'].append(successor)
            contributors.add(f"{succ_row['SUBMITTED_BY']} (Tier {succ_row['USER_TIER']})")
        
        result['collaboration_info']['contributors'] = list(contributors)
        
        return result
        
    except Exception as e:

        return None

def get_employee_planning_dashboard(user_access):
    """Get comprehensive dashboard of all employees user can plan for with their planning status"""
    if not user_access:
        return pd.DataFrame()
    
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['employee_db'])
        
        tier = user_access['tier']
        
        # Get accessible employees based on tier
        if tier == 1:
            # Tier 1: All employees in their segments
            user_segments = user_access['segments']
            if not user_segments:
                return pd.DataFrame()
            
            placeholders = ','.join(['?' for _ in user_segments])
            employee_query = f"""
                SELECT SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_FIRST_NAME,
                       PREFERRED_LAST_NAME, EMPLOYEE_ID, POSITION_TITLE, 
                       MANAGEMENT_LEVEL, JOB_LEVEL, LEADER_NAME
                FROM incumbents
                WHERE SEGMENT_HIER_LEVEL_2_NAME IN ({placeholders})
                ORDER BY SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_LAST_NAME, PREFERRED_FIRST_NAME
            """
            params = user_segments
            
        elif tier == 2:
            # Tier 2: Only assigned employees in their segments
            user_segments = user_access['segments']
            leader_ids = user_access['leader_employee_ids']
            
            if not user_segments or not leader_ids:
                return pd.DataFrame()
            
            segment_placeholders = ','.join(['?' for _ in user_segments])
            leader_placeholders = ','.join(['?' for _ in leader_ids])
            
            employee_query = f"""
                SELECT SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_FIRST_NAME,
                       PREFERRED_LAST_NAME, EMPLOYEE_ID, POSITION_TITLE, 
                       MANAGEMENT_LEVEL, JOB_LEVEL, LEADER_NAME
                FROM incumbents
                WHERE SEGMENT_HIER_LEVEL_2_NAME IN ({segment_placeholders})
                AND EMPLOYEE_ID IN ({leader_placeholders})
                ORDER BY PREFERRED_LAST_NAME, PREFERRED_FIRST_NAME
            """
            params = user_segments + leader_ids
            
        elif tier == 3:
            # Tier 3: Only assigned incumbents
            leader_ids = user_access['leader_employee_ids']
            
            if not leader_ids:
                return pd.DataFrame()
            
            placeholders = ','.join(['?' for _ in leader_ids])
            employee_query = f"""
                SELECT SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_FIRST_NAME,
                       PREFERRED_LAST_NAME, EMPLOYEE_ID, POSITION_TITLE, 
                       MANAGEMENT_LEVEL, JOB_LEVEL, LEADER_NAME
                FROM incumbents
                WHERE EMPLOYEE_ID IN ({placeholders})
                ORDER BY PREFERRED_LAST_NAME, PREFERRED_FIRST_NAME
            """
            params = leader_ids
        
        else:
            return pd.DataFrame()
        
        # Get employee data
        employees_df = pd.read_sql_query(employee_query, conn, params=params)
        
        if employees_df.empty:
            conn.close()
            return pd.DataFrame()
        
        # Get succession plan status for these employees (enhanced for collaboration)
        conn_plans = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        
        employee_ids = employees_df['EMPLOYEE_ID'].tolist()
        plan_placeholders = ','.join(['?' for _ in employee_ids])
        
        # Get query from config and format it
        query_template = CONFIG['queries']['sqlite']['get_employee_planning_dashboard']
        plans_query = query_template.format(
            succession_plans_table=CONFIG['database']['sqlite']['tables']['succession_plans'],
            employee_placeholders=plan_placeholders
        )
        
        plans_df = pd.read_sql_query(plans_query, conn_plans, params=employee_ids + employee_ids + employee_ids)
        
        conn.close()
        conn_plans.close()
        
        # Merge employee data with planning status
        dashboard_df = employees_df.merge(
            plans_df, 
            left_on='EMPLOYEE_ID', 
            right_on='INCUMBENT_EMPLOYEE_ID', 
            how='left'
        )
        
        # Clean up and format the data
        dashboard_df['PLANNING_STATUS'] = dashboard_df['SUBMISSION_STATUS'].fillna('not_planned')
        dashboard_df['SUCCESSOR_COUNT'] = dashboard_df['successor_count'].fillna(0).astype(int)
        dashboard_df['CONTRIBUTOR_COUNT'] = dashboard_df['contributor_count'].fillna(0).astype(int)
        dashboard_df['ALL_CONTRIBUTORS'] = dashboard_df['all_contributors'].fillna('')
        dashboard_df['LAST_UPDATED'] = dashboard_df['SUBMITTED_ON']
        dashboard_df['UPDATED_BY'] = dashboard_df['SUBMITTED_BY']
        dashboard_df['SUBMITTER_TIER'] = dashboard_df['USER_TIER'].fillna(0).infer_objects(copy=False).astype(int)
        
        # Create enhanced status display with collaboration info
        def create_status_display(row):
            status_map = {
                'not_planned': '⚪ Not Planned',
                'not_complete': '🟡 In Progress', 
                'saved': '🟠 Draft',
                'submitted': '🔵 Submitted',
                'approved': '🟢 Approved',
                'needs_edit': '🔴 Needs Edit'
            }
            
            # Use the latest overall status (no mixed states)
            base_status = status_map.get(row['PLANNING_STATUS'], '⚪ Not Planned')
            
            # Add collaboration indicator
            if row['CONTRIBUTOR_COUNT'] > 1:
                base_status += f" 👥{row['CONTRIBUTOR_COUNT']}"
            
            # Add reopen option for approved plans (Tier 1 only)
            if row['PLANNING_STATUS'] == 'approved':
                base_status += " 🔄"  # Indicator that it can be reopened
            
            return base_status
        
        dashboard_df['STATUS_DISPLAY'] = dashboard_df.apply(create_status_display, axis=1)
        
        # Select and rename columns for display
        display_columns = [
            'EMPLOYEE_ID', 'PREFERRED_FIRST_NAME', 'PREFERRED_LAST_NAME',
            'POSITION_TITLE', 'MANAGEMENT_LEVEL', 'JOB_LEVEL', 
            'SEGMENT_HIER_LEVEL_2_NAME', 'LEADER_NAME',
            'STATUS_DISPLAY', 'SUCCESSOR_COUNT', 'CONTRIBUTOR_COUNT', 'ALL_CONTRIBUTORS', 'UPDATED_BY', 'SUBMITTER_TIER'
        ]
        
        result_df = dashboard_df[display_columns].copy()
        result_df.columns = [
            'Employee ID', 'First Name', 'Last Name', 'Position', 
            'Mgmt Level', 'Job Level', 'Segment', 'Leader',
            'Planning Status', 'Successors', 'Contributors', 'All Contributors', 'Last Updated By', 'Tier'
        ]
        
        return result_df
        
    except Exception as e:

        return pd.DataFrame()

def can_user_search(user_access):
    """Check if user can perform searches"""
    if not user_access:
        return False
    
    # Tier 3 users cannot search
    return user_access['tier'] != 3

def can_user_submit(user_access):
    """Check if user can submit succession plans"""
    if not user_access:
        return False
    
    # All tiers can submit
    return user_access['tier'] in [1, 2, 3]

def can_user_approve(user_access):
    """Check if user can approve succession plans"""
    if not user_access:
        return False
    
    # Only Tier 1 can approve
    return user_access['tier'] == 1

def get_accessible_incumbents_for_tier3(user_access):
    """Get the specific incumbents that Tier 3 users can access"""
    if not user_access or user_access['tier'] != 3:
        return []
    
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['employee_db'])
        
        # Get employee details for the assigned employee IDs
        leader_ids = user_access['leader_employee_ids']
        if not leader_ids:
            return []
        
        placeholders = ','.join(['?' for _ in leader_ids])
        query = f"""
            SELECT SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_FIRST_NAME,
                   PREFERRED_LAST_NAME, EMPLOYEE_ID, POSITION_ID,
                   POSITION_TITLE, MANAGEMENT_LEVEL, JOB_LEVEL,
                   DAYS_IN_MANAGEMENT_LEVEL, LEADER_NAME, HR_SEGMENT
            FROM incumbents
            WHERE EMPLOYEE_ID IN ({placeholders})
        """
        
        df = pd.read_sql_query(query, conn, params=leader_ids)
        conn.close()
        
        return df.to_dict('records')
        
    except Exception as e:

        return []

def get_submitted_plans_for_tier1(user_access):
    """Get submitted succession plans that Tier 1 can see (within their segments) - only from Tier 2 and Tier 3"""
    if not user_access or user_access['tier'] != 1:
        return []
    
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        
        # Get submitted plans in user's segments from Tier 2 and Tier 3 only
        user_segments = user_access['segments']
        if not user_segments:
            return []
        
        placeholders = ','.join(['?' for _ in user_segments])
        
        # Get query from config and format it
        query_template = CONFIG['queries']['sqlite']['get_submitted_plans_for_tier1']
        query = query_template.format(
            succession_plans_table=CONFIG['database']['sqlite']['tables']['succession_plans'],
            segment_placeholders=placeholders
        )
        
        df = pd.read_sql_query(query, conn, params=user_segments + user_segments)
        conn.close()
        
        return df.to_dict('records')
        
    except Exception as e:

        return []

def get_tier2_submission_for_incumbent(incumbent_employee_id, user_access):
    """Get Tier 2/3 submission for a specific incumbent that Tier 1 can review"""
    if not user_access or user_access['tier'] != 1:
        return None
    
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        
        # Get query from config and format it
        query_template = CONFIG['queries']['sqlite']['get_tier2_submission_for_incumbent']
        query = query_template.format(
            succession_plans_table=CONFIG['database']['sqlite']['tables']['succession_plans']
        )
        
        df = pd.read_sql_query(query, conn, params=(incumbent_employee_id, incumbent_employee_id))
        conn.close()
        
        if df.empty:
            return None
        
        # Convert to the format expected by the app
        submission_data = {
            'incumbent': {
                'metadata': {},
                'plan_details': {}
            },
            'successors': []
        }
        
        # Group by successor to handle multiple successors
        for _, row in df.iterrows():
            # Build incumbent data (same for all rows)
            if not submission_data['incumbent']['metadata']:
                submission_data['incumbent']['metadata'] = {
                    'EMPLOYEE_ID': row['INCUMBENT_EMPLOYEE_ID'],
                    'PREFERRED_FIRST_NAME': row['INCUMBENT_FIRST_NAME'],
                    'PREFERRED_LAST_NAME': row['INCUMBENT_LAST_NAME'],
                    'POSITION_TITLE': row['INCUMBENT_POSITION'],
                    'MANAGEMENT_LEVEL': row['INCUMBENT_MANAGEMENT_LEVEL'],
                    'JOB_LEVEL': row['INCUMBENT_JOB_LEVEL'],
                    'SEGMENT_HIER_LEVEL_2_NAME': row['INCUMBENT_SEGMENT']
                }
                
                submission_data['incumbent']['plan_details'] = {
                    'critical_role': row['CRITICAL_ROLE'],
                    'responsibilities': row['RESPONSIBILITIES'],
                    'top_skills': json.loads(row['INCUMBENT_TOP_SKILLS']) if row['INCUMBENT_TOP_SKILLS'] else [],
                    'top_ple': row['INCUMBENT_TOP_PLE'],
                    'contract_end_date': row['INCUMBENT_CONTRACT_END_DATE'],
                    'sourcing_strategy': json.loads(row['SOURCING_STRATEGY']) if row['SOURCING_STRATEGY'] else [],
                    'role_type': row['ROLE_TYPE'],
                    'scenario_plan': row['SCENARIO_PLAN'],
                    'new_position_title': row['NEW_POSITION_TITLE']
                }
            
            # Add successor data
            successor = {
                'metadata': {
                    'EMPLOYEE_ID': row['SUCCESSOR_EMPLOYEE_ID'],
                    'PREFERRED_FIRST_NAME': row['SUCCESSOR_FIRST_NAME'],
                    'PREFERRED_LAST_NAME': row['SUCCESSOR_LAST_NAME'],
                    'POSITION_TITLE': row['SUCCESSOR_POSITION'],
                    'MANAGEMENT_LEVEL': row['SUCCESSOR_MANAGEMENT_LEVEL'],
                    'JOB_LEVEL': row['SUCCESSOR_JOB_LEVEL'],
                    'SEGMENT_HIER_LEVEL_2_NAME': row['SUCCESSOR_SEGMENT']
                },
                'assessment': {
                    'readiness': row['SUCCESSOR_READINESS'],
                    'future_readiness_timing': row['SUCCESSOR_FUTURE_READINESS_TIMING'],
                    'contract_end_date': row['SUCCESSOR_CONTRACT_END_DATE'],
                    'strengths': row['SUCCESSOR_STRENGTHS'],
                    'top_skills': json.loads(row['SUCCESSOR_TOP_SKILLS']) if row['SUCCESSOR_TOP_SKILLS'] else [],
                    'top_ple': row['SUCCESSOR_TOP_PLE'],
                    'development_focus': row['SUCCESSOR_DEVELOPMENT_FOCUS'],
                    'talent_actions': row['SUCCESSOR_TALENT_ACTIONS']
                }
            }
            
            submission_data['successors'].append(successor)
        
        # Add submission metadata
        submission_data['submission_info'] = {
            'submitted_by': df.iloc[0]['SUBMITTED_BY'],
            'submitted_on': df.iloc[0]['SUBMITTED_ON'],
            'user_tier': df.iloc[0]['USER_TIER']
        }
        
        return submission_data
        
    except Exception as e:

        return None

def approve_submission(incumbent_employee_id, approver_user_access):
    """Approve a Tier 2/3 submission (changes status to approved)"""
    if not approver_user_access or approver_user_access['tier'] != 1:
        return False
    
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        cursor = conn.cursor()
        
        # Update submission status to approved for Tier 2/3 submissions only
        cursor.execute("""
            UPDATE succession_plans 
            SET SUBMISSION_STATUS = 'approved',
                APPROVED_BY = ?,
                APPROVED_ON = ?
            WHERE INCUMBENT_EMPLOYEE_ID = ? 
            AND SUBMISSION_STATUS = 'submitted'
            AND USER_TIER IN (2, 3)
            AND REMOVED = FALSE
        """, (approver_user_access['user_id'], datetime.datetime.now(), incumbent_employee_id))
        
        updated_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return updated_rows > 0
        
    except Exception as e:

        return False

def request_edits(incumbent_employee_id, requester_user_access):
    """Request edits on a Tier 2/3 submission (changes status back to needs_edit)"""
    if not requester_user_access or requester_user_access['tier'] != 1:
        return False
    
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        cursor = conn.cursor()
        
        # First, let's see what records exist for this incumbent
        cursor.execute("""
            SELECT INCUMBENT_EMPLOYEE_ID, SUBMISSION_STATUS, USER_TIER, REMOVED, SUBMITTED_BY
            FROM succession_plans 
            WHERE INCUMBENT_EMPLOYEE_ID = ?
            ORDER BY CREATED_AT DESC
            LIMIT 5
        """, (incumbent_employee_id,))
        
        records = cursor.fetchall()
        print(f"DEBUG: Found {len(records)} records for incumbent {incumbent_employee_id}")
        for record in records:
            print(f"DEBUG: ID={record[0]}, Status={record[1]}, Tier={record[2]}, Removed={record[3]}, SubmittedBy={record[4]}")
        
        # Update submission status to needs_edit for Tier 2/3 submissions only
        cursor.execute("""
            UPDATE succession_plans 
            SET SUBMISSION_STATUS = 'needs_edit',
                EDIT_REQUESTED_BY = ?,
                EDIT_REQUESTED_ON = ?
            WHERE INCUMBENT_EMPLOYEE_ID = ? 
            AND SUBMISSION_STATUS IN ('submitted', 'approved')
            AND (USER_TIER IN (2, 3) OR (USER_TIER = 1 AND SUBMISSION_STATUS = 'approved'))
            AND REMOVED = FALSE
        """, (requester_user_access['user_id'], datetime.datetime.now(), incumbent_employee_id))
        
        updated_rows = cursor.rowcount
        print(f"DEBUG: Updated {updated_rows} rows for incumbent {incumbent_employee_id}")
        conn.commit()
        conn.close()
        
        return updated_rows > 0
        
    except Exception as e:
        print(f"DEBUG: Exception in request_edits: {e}")
        return False

def reopen_approved_plan(incumbent_employee_id, requester_user_access):
    """Reopen an approved plan for editing (Tier 1 only)"""
    if not requester_user_access or requester_user_access['tier'] != 1:
        return False
    
    try:
        conn = sqlite3.connect(CONFIG['database']['sqlite']['succession_plans_db'])
        cursor = conn.cursor()
        
        # Change status from 'approved' back to 'needs_edit'
        cursor.execute("""
            UPDATE succession_plans 
            SET SUBMISSION_STATUS = 'needs_edit',
                EDIT_REQUESTED_BY = ?,
                EDIT_REQUESTED_ON = ?
            WHERE INCUMBENT_EMPLOYEE_ID = ? 
            AND SUBMISSION_STATUS = 'approved'
            AND REMOVED = FALSE
        """, (requester_user_access['user_id'], datetime.datetime.now(), incumbent_employee_id))
        
        updated_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return updated_rows > 0
        
    except Exception as e:

        return False
