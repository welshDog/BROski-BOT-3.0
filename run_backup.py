#!/usr/bin/env python
"""
Quick script to run the dashboard backup
"""
import os
import sys

def run_backup():
    """Run the dashboard backup script"""
    try:
        print("Running BROski Dashboard backup...")
        
        # Check if backup script exists
        if os.path.exists("backup_dashboard.py"):
            # Execute the backup script
            os.system(f"{sys.executable} backup_dashboard.py")
            
            print("\nBackup completed successfully!")
            print("\nYou can find your backup in the 'backups' directory")
            print("The development roadmap is saved in 'docs/DASHBOARD_ROADMAP.md'")
        else:
            print("Error: backup_dashboard.py file not found!")
            print("Please make sure the file exists in the project directory.")
            
    except Exception as e:
        print(f"Error running backup: {str(e)}")

if __name__ == "__main__":
    run_backup()
