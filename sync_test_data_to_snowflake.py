#!/usr/bin/env python3
"""
Sync test data to Snowflake with proper casting and collaborative scenarios
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime
import snowflake.connector
import os

def get_snowflake_connection():
    """Get Snowflake connection using environment variables or Streamlit secrets"""
    try:
        # Try to get from environment variables first
        conn_params = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'user': os.getenv('SNOWFLAKE_USER'),
            'password': os.getenv('SNOWFLAKE_PASSWORD'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': os.getenv('SNOWFLAKE_DATABASE', 'HR_EXPLORATORY'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA', 'HR_DE_SANDBOX')
        }
        
        # Check if all required params are available
        if not all([conn_params['account'], conn_params['user'], conn_params['password']]):
            print("❌ Missing Snowflake connection parameters in environment variables")
            print("Required: SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD")
            print("Optional: SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA")
            return None
        
        conn = snowflake.connector.connect(**conn_params)
        return conn
        
    except Exception as e:
        print(f"❌ Error connecting to Snowflake: {e}")
        return None

def sync_user_access_to_snowflake():
    """Sync user access test data to Snowflake with proper casting"""
    
    print("🔄 Syncing user access test data to Snowflake...")
    
    # Get data from SQLite
    try:
        sqlite_conn = sqlite3.connect("succession_db.sqlite")
        
        query = """
            SELECT WORK_PRIMARY_EMAIL, USER_ID, EMPLOYEE_ID, HR_ACCESS,
                   TIER_1_ACCESS_IND, TIER_2_ACCESS_IND, TIER_3_ACCESS_IND,
                   SUCCESSION_PLAN_SEGMENT, LEADER_EMPLOYEE_ID,
                   CREATED_BY, CREATED_ON, UPDATED_BY, UPDATED_ON
            FROM user_access
        """
        
        df = pd.read_sql_query(query, sqlite_conn)
        sqlite_conn.close()
        
        if df.empty:
            print("❌ No user access data found in SQLite")
            return False
        
        print(f"📊 Found {len(df)} user access records in SQLite")
        
    except Exception as e:
        print(f"❌ Error reading from SQLite: {e}")
        return False
    
    # Connect to Snowflake
    snowflake_conn = get_snowflake_connection()
    if not snowflake_conn:
        return False
    
    try:
        cursor = snowflake_conn.cursor()
        
        # Create table if it doesn't exist
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS HR_EXPLORATORY.HR_DE_SANDBOX.USER_ACCESS (
                WORK_PRIMARY_EMAIL VARCHAR(255),
                USER_ID VARCHAR(100),
                EMPLOYEE_ID VARCHAR(50),
                HR_ACCESS BOOLEAN,
                TIER_1_ACCESS_IND BOOLEAN,
                TIER_2_ACCESS_IND BOOLEAN,
                TIER_3_ACCESS_IND BOOLEAN,
                SUCCESSION_PLAN_SEGMENT VARCHAR(5000),
                LEADER_EMPLOYEE_ID VARCHAR(5000),
                CREATED_BY VARCHAR(100),
                CREATED_ON TIMESTAMP,
                UPDATED_BY VARCHAR(100),
                UPDATED_ON TIMESTAMP
            )
        """
        
        cursor.execute(create_table_sql)
        print("✅ User access table created/verified in Snowflake")
        
        # Clear existing test data
        cursor.execute("DELETE FROM HR_EXPLORATORY.HR_DE_SANDBOX.USER_ACCESS WHERE CREATED_BY = 'SYSTEM'")
        print("🗑️ Cleared existing test data from Snowflake")
        
        # Insert data row by row with explicit casting
        insert_sql = """
            INSERT INTO HR_EXPLORATORY.HR_DE_SANDBOX.USER_ACCESS (
                WORK_PRIMARY_EMAIL, USER_ID, EMPLOYEE_ID, HR_ACCESS,
                TIER_1_ACCESS_IND, TIER_2_ACCESS_IND, TIER_3_ACCESS_IND,
                SUCCESSION_PLAN_SEGMENT, LEADER_EMPLOYEE_ID,
                CREATED_BY, CREATED_ON, UPDATED_BY, UPDATED_ON
            ) VALUES (
                %s, %s, %s, %s::BOOLEAN,
                %s::BOOLEAN, %s::BOOLEAN, %s::BOOLEAN,
                %s, %s,
                %s, %s::TIMESTAMP, %s, %s::TIMESTAMP
            )
        """
        
        inserted_count = 0
        for _, row in df.iterrows():
            try:
                cursor.execute(insert_sql, (
                    row['WORK_PRIMARY_EMAIL'],
                    row['USER_ID'],
                    row['EMPLOYEE_ID'],
                    bool(row['HR_ACCESS']),
                    bool(row['TIER_1_ACCESS_IND']),
                    bool(row['TIER_2_ACCESS_IND']),
                    bool(row['TIER_3_ACCESS_IND']),
                    row['SUCCESSION_PLAN_SEGMENT'],
                    row['LEADER_EMPLOYEE_ID'],
                    row['CREATED_BY'],
                    row['CREATED_ON'],
                    row['UPDATED_BY'],
                    row['UPDATED_ON']
                ))
                inserted_count += 1
                
            except Exception as e:
                print(f"❌ Error inserting row for {row['WORK_PRIMARY_EMAIL']}: {e}")
        
        snowflake_conn.commit()
        print(f"✅ Inserted {inserted_count} user access records into Snowflake")
        
        # Verify the data
        cursor.execute("SELECT COUNT(*) FROM HR_EXPLORATORY.HR_DE_SANDBOX.USER_ACCESS WHERE CREATED_BY = 'SYSTEM'")
        count = cursor.fetchone()[0]
        print(f"🔍 Verification: {count} records in Snowflake USER_ACCESS table")
        
        # Show collaborative scenarios in Snowflake
        cursor.execute("""
            SELECT WORK_PRIMARY_EMAIL, 
                   TIER_1_ACCESS_IND, TIER_2_ACCESS_IND, TIER_3_ACCESS_IND,
                   SUCCESSION_PLAN_SEGMENT, LEADER_EMPLOYEE_ID
            FROM HR_EXPLORATORY.HR_DE_SANDBOX.USER_ACCESS 
            WHERE CREATED_BY = 'SYSTEM'
            ORDER BY TIER_1_ACCESS_IND DESC, TIER_2_ACCESS_IND DESC, TIER_3_ACCESS_IND DESC
        """)
        
        results = cursor.fetchall()
        print(f"\n📋 SNOWFLAKE USER ACCESS DATA:")
        print("Email | Tier | Segments | Leader IDs")
        print("-" * 80)
        
        for row in results:
            email, t1, t2, t3, segments, leaders = row
            tier = 1 if t1 else (2 if t2 else 3)
            
            segments_list = json.loads(segments) if segments else []
            leaders_list = json.loads(leaders) if leaders else []
            
            print(f"{email[:25]:<25} | T{tier} | {len(segments_list)} segs | {len(leaders_list)} leaders")
        
        cursor.close()
        snowflake_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error syncing to Snowflake: {e}")
        return False

def sync_incumbents_sample_to_snowflake():
    """Sync a sample of incumbents data to Snowflake for testing"""
    
    print("\n🔄 Syncing sample incumbents data to Snowflake...")
    
    # Get sample data from SQLite
    try:
        sqlite_conn = sqlite3.connect("succession_db.sqlite")
        
        # Get a representative sample from each segment
        query = """
            SELECT SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_FIRST_NAME,
                   PREFERRED_LAST_NAME, EMPLOYEE_ID, POSITION_ID,
                   POSITION_TITLE, MANAGEMENT_LEVEL, JOB_LEVEL,
                   DAYS_IN_MANAGEMENT_LEVEL, LEADER_NAME, HR_SEGMENT
            FROM incumbents
            WHERE SEGMENT_HIER_LEVEL_2_NAME IN (
                'Walt Disney Television', 'Disney Experiences', 
                'Walt Disney Studio Entertainment', 'Shared Services'
            )
            LIMIT 100
        """
        
        df = pd.read_sql_query(query, sqlite_conn)
        sqlite_conn.close()
        
        if df.empty:
            print("❌ No incumbents data found in SQLite")
            return False
        
        print(f"📊 Found {len(df)} incumbent records for sync")
        
    except Exception as e:
        print(f"❌ Error reading incumbents from SQLite: {e}")
        return False
    
    # Connect to Snowflake
    snowflake_conn = get_snowflake_connection()
    if not snowflake_conn:
        return False
    
    try:
        cursor = snowflake_conn.cursor()
        
        # Create incumbents table if it doesn't exist
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS HR_EXPLORATORY.HR_DE_SANDBOX.SL_VW_SP_INCUMBENTS (
                SEGMENT_HIER_LEVEL_2_NAME VARCHAR(255),
                PREFERRED_FIRST_NAME VARCHAR(255),
                PREFERRED_LAST_NAME VARCHAR(255),
                EMPLOYEE_ID VARCHAR(50),
                POSITION_ID VARCHAR(50),
                POSITION_TITLE VARCHAR(500),
                MANAGEMENT_LEVEL VARCHAR(100),
                JOB_LEVEL VARCHAR(50),
                DAYS_IN_MANAGEMENT_LEVEL NUMBER,
                LEADER_NAME VARCHAR(255),
                HR_SEGMENT VARCHAR(255)
            )
        """
        
        cursor.execute(create_table_sql)
        print("✅ Incumbents table created/verified in Snowflake")
        
        # Clear existing data
        cursor.execute("DELETE FROM HR_EXPLORATORY.HR_DE_SANDBOX.SL_VW_SP_INCUMBENTS")
        print("🗑️ Cleared existing incumbents data from Snowflake")
        
        # Insert data with explicit casting
        insert_sql = """
            INSERT INTO HR_EXPLORATORY.HR_DE_SANDBOX.SL_VW_SP_INCUMBENTS (
                SEGMENT_HIER_LEVEL_2_NAME, PREFERRED_FIRST_NAME, PREFERRED_LAST_NAME,
                EMPLOYEE_ID, POSITION_ID, POSITION_TITLE, MANAGEMENT_LEVEL,
                JOB_LEVEL, DAYS_IN_MANAGEMENT_LEVEL, LEADER_NAME, HR_SEGMENT
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s::NUMBER, %s, %s
            )
        """
        
        inserted_count = 0
        for _, row in df.iterrows():
            try:
                cursor.execute(insert_sql, (
                    row['SEGMENT_HIER_LEVEL_2_NAME'],
                    row['PREFERRED_FIRST_NAME'],
                    row['PREFERRED_LAST_NAME'],
                    row['EMPLOYEE_ID'],
                    row['POSITION_ID'],
                    row['POSITION_TITLE'],
                    row['MANAGEMENT_LEVEL'],
                    row['JOB_LEVEL'],
                    row['DAYS_IN_MANAGEMENT_LEVEL'] if pd.notna(row['DAYS_IN_MANAGEMENT_LEVEL']) else None,
                    row['LEADER_NAME'],
                    row['HR_SEGMENT']
                ))
                inserted_count += 1
                
            except Exception as e:
                print(f"❌ Error inserting incumbent {row['EMPLOYEE_ID']}: {e}")
        
        snowflake_conn.commit()
        print(f"✅ Inserted {inserted_count} incumbent records into Snowflake")
        
        # Verify and show distribution
        cursor.execute("""
            SELECT SEGMENT_HIER_LEVEL_2_NAME, COUNT(*) as count
            FROM HR_EXPLORATORY.HR_DE_SANDBOX.SL_VW_SP_INCUMBENTS
            GROUP BY SEGMENT_HIER_LEVEL_2_NAME
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        print(f"\n📊 SNOWFLAKE INCUMBENTS DISTRIBUTION:")
        for segment, count in results:
            print(f"  {segment}: {count} incumbents")
        
        cursor.close()
        snowflake_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error syncing incumbents to Snowflake: {e}")
        return False

def main():
    """Main function to sync all test data to Snowflake"""
    
    print("🚀 SYNCING TEST DATA TO SNOWFLAKE")
    print("=" * 50)
    
    # Check if snowflake-connector-python is available
    try:
        import snowflake.connector
    except ImportError:
        print("❌ snowflake-connector-python not installed")
        print("Install with: pip install snowflake-connector-python")
        return False
    
    success = True
    
    # Sync user access data
    if not sync_user_access_to_snowflake():
        success = False
    
    # Sync sample incumbents data
    if not sync_incumbents_sample_to_snowflake():
        success = False
    
    if success:
        print("\n🎉 ALL DATA SYNCED SUCCESSFULLY TO SNOWFLAKE!")
        print("\n📋 READY FOR TESTING:")
        print("1. Switch to Snowflake backend in the app")
        print("2. Test collaborative scenarios with multiple Tier 2 users")
        print("3. Verify Tier 1 can see all Tier 2 activity")
        print("4. Test latest record sharing across users")
    else:
        print("\n❌ Some data sync operations failed")
    
    return success

if __name__ == "__main__":
    main()
