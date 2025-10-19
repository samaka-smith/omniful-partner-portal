#!/usr/bin/env python3
"""Add description column to targets table"""

import sqlite3
import os

def migrate():
    # Try both possible database locations
    db_paths = [
        'partner_portal.db',
        'src/database/app.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"Found database at: {db_path}")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            try:
                # Check if description column already exists
                cursor.execute("PRAGMA table_info(targets)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'description' in columns:
                    print(f"✓ description column already exists in targets table ({db_path})")
                else:
                    # Add description column
                    cursor.execute("ALTER TABLE targets ADD COLUMN description TEXT")
                    conn.commit()
                    print(f"✓ Added description column to targets table ({db_path})")
                
            except Exception as e:
                print(f"Error during migration for {db_path}: {e}")
                conn.rollback()
            finally:
                conn.close()
    
    print("\nMigration completed!")

if __name__ == '__main__':
    migrate()
