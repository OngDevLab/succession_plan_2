#!/usr/bin/env python3
"""
Script to add REMOVED column to the succession_plans table
"""

import sqlite3
import os

def add_removed_column():
    """Add REMOVED column to succession_plans table"""
    
    db_file = "succession_plans.sqlite"
    
    print(f"Adding REMOVED column to {db_file}")
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if REMOVED column already exists
        cursor.execute("PRAGMA table_info(succession_plans)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'REMOVED' in columns:
            print("REMOVED column already exists")
        else:
            # Add REMOVED column with default value FALSE
            cursor.execute("ALTER TABLE succession_plans ADD COLUMN REMOVED BOOLEAN DEFAULT FALSE")
            print("Added REMOVED column with default value FALSE")
        
        # Update all existing records to have REMOVED = FALSE if NULL
        cursor.execute("UPDATE succession_plans SET REMOVED = FALSE WHERE REMOVED IS NULL")
        updated_rows = cursor.rowcount
        print(f"Updated {updated_rows} existing records to set REMOVED = FALSE")
        
        conn.commit()
        
        # Verify the change
        cursor.execute("SELECT COUNT(*) FROM succession_plans WHERE REMOVED = FALSE")
        count = cursor.fetchone()[0]
        print(f"Total records with REMOVED = FALSE: {count}")
        
        conn.close()
        print("Successfully added REMOVED column!")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    add_removed_column()
