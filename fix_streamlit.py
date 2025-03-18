#!/usr/bin/env python
"""
Fix Streamlit rerun method in dashboard
"""
import os

def update_dashboard():
    """Update experimental_rerun to rerun in dashboard file"""
    dashboard_path = "ui/broski_dashboard.py"
    
    try:
        # Read with explicit UTF-8 encoding
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the deprecated function
        updated = content.replace('st.experimental_rerun()', 'st.rerun()')
        
        # Write with explicit UTF-8 encoding
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(updated)
            
        print(f"✓ Successfully updated dashboard code")
        print(f"  Changed 'st.experimental_rerun()' to 'st.rerun()'")
        
    except FileNotFoundError:
        print(f"Error: Dashboard file not found at {dashboard_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    update_dashboard()
