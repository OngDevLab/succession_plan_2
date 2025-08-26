#!/usr/bin/env python3
"""
Script to import TBL_SL_EMPLOYEE.csv into SQLite database
This will create a new table called 'employees' to replace the old structure
"""

import pandas as pd
import sqlite3
import os

def import_csv_to_sqlite():
    """Import the CSV file into SQLite database"""
    
    # File paths
    csv_file = "TBL_SL_EMPLOYEE.csv"
    db_file = "succession_db.sqlite"
    
    print(f"Starting import of {csv_file} to {db_file}")
    
    try:
        # Read the CSV file
        print("Reading CSV file...")
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} rows from CSV")
        
        # Display column info
        print("\nCSV Columns:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # Connect to SQLite database
        print(f"\nConnecting to SQLite database: {db_file}")
        conn = sqlite3.connect(db_file)
        
        # Drop the table if it exists and create new one
        print("Dropping existing 'employees' table if it exists...")
        conn.execute("DROP TABLE IF EXISTS employees")
        
        # Import the dataframe to SQLite
        print("Creating new 'employees' table and importing data...")
        df.to_sql('employees', conn, index=False, if_exists='replace')
        
        # Create indexes for better search performance
        print("Creating indexes for search optimization...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_employee_id ON employees(EMPLOYEE_ID)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_last_name ON employees(PREFERRED_LAST_NAME)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_first_name ON employees(PREFERRED_FIRST_NAME)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_full_name ON employees(PREFERRED_FIRST_NAME, PREFERRED_LAST_NAME)")
        
        # Commit changes
        conn.commit()
        
        # Verify the import
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        print(f"Successfully imported {count} records to 'employees' table")
        
        # Show sample data
        print("\nSample data from imported table:")
        cursor.execute("""
            SELECT PREFERRED_FIRST_NAME, PREFERRED_LAST_NAME, EMPLOYEE_ID, 
                   POSITION_TITLE, LEADER_NAME, MANAGEMENT_LEVEL, JOB_LEVEL
            FROM employees 
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        print("First Name | Last Name | Employee ID | Position Title | Manager | Mgmt Level | Job Level")
        print("-" * 100)
        for row in rows:
            print(f"{row[0]:<10} | {row[1]:<9} | {row[2]:<11} | {row[3]:<20} | {row[4]:<15} | {row[5]:<10} | {row[6]}")
        
        conn.close()
        print(f"\nImport completed successfully!")
        
    except Exception as e:
        print(f"Error during import: {e}")
        return False
    
    return True

if __name__ == "__main__":
    import_csv_to_sqlite()
