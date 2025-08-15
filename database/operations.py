"""
Database functions - Using fully configurable queries from config
"""

import streamlit as st
import pandas as pd
import sqlite3
import json
from config.loader import CONFIG

@st.cache_data(show_spinner="Searching database...")
def search_employees(last_name):
    """Queries the SQLite database for employees by last name."""
    try:
        conn = sqlite3.connect(CONFIG['database']['employee_db'])
        
        # Format query with table name and search limit
        query = CONFIG['queries']['search_employees'].format(
            employee_table=CONFIG['database']['tables']['employee'],
            search_limit=CONFIG['database']['limits']['employee_search']
        )
        
        df = pd.read_sql_query(query, conn, params=(f"%{last_name}%",))
        conn.close()
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Database error: {e}")
        return []

def get_latest_incumbent_values(employee_id):
    """Get the latest incumbent plan values for prepopulation"""
    try:
        conn = sqlite3.connect(CONFIG['database']['succession_plans_db'])
        cursor = conn.cursor()
        
        # Format query with table name
        query = CONFIG['queries']['get_latest_incumbent_values'].format(
            succession_plans_table=CONFIG['database']['tables']['succession_plans']
        )
        
        cursor.execute(query, (employee_id,))
        
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
        return None

def get_latest_successor_values(employee_id):
    """Get the latest successor assessment values for prepopulation"""
    try:
        conn = sqlite3.connect(CONFIG['database']['succession_plans_db'])
        cursor = conn.cursor()
        
        # Format query with table name
        query = CONFIG['queries']['get_latest_successor_values'].format(
            succession_plans_table=CONFIG['database']['tables']['succession_plans']
        )
        
        cursor.execute(query, (employee_id,))
        
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
        return None

def save_succession_plan(incumbent_data, successor_data, plan_details, assessment_details):
    """Save a succession plan record to the database with database-side UUID generation"""
    try:
        conn = sqlite3.connect(CONFIG['database']['succession_plans_db'])
        cursor = conn.cursor()
        
        # Format query with table name
        query = CONFIG['queries']['save_succession_plan'].format(
            succession_plans_table=CONFIG['database']['tables']['succession_plans']
        )
        
        cursor.execute(query, (
            incumbent_data['EMPLOYEE_ID'],
            incumbent_data['PREFERRED_NAME_FIRST_NAME'],
            incumbent_data['PREFERRED_NAME_LAST_NAME'],
            incumbent_data['EMAIL_PRIMARY_WORK'],
            incumbent_data['POSITION_NBR_DESCRIPTION'],
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
            successor_data['PREFERRED_NAME_FIRST_NAME'],
            successor_data['PREFERRED_NAME_LAST_NAME'],
            successor_data['EMAIL_PRIMARY_WORK'],
            successor_data['POSITION_NBR_DESCRIPTION'],
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
        
        return str(record_id)  # Return as string for consistency
        
    except Exception as e:
        st.error(f"Database error: {e}")
        return None
