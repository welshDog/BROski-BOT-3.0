#!/usr/bin/env python
"""
Fix encoding issues in dashboard
"""
import os

def fix_encoding():
    """Fix UTF-8 encoding issues in dashboard file"""
    print("Fixing dashboard encoding issues...")
    
    # First update the fix_dashboard.py script to use UTF-8 encoding
    with open('fix_dashboard.py', 'r', encoding='utf-8', errors='replace') as f:
        dashboard_fix_code = f.read()
    
    # Replace the problematic line that doesn't specify encoding
    dashboard_fix_code = dashboard_fix_code.replace(
        "with open(dashboard_path, 'w') as f:",
        "with open(dashboard_path, 'w', encoding='utf-8') as f:"
    )
    
    # Write back with UTF-8 encoding
    with open('fix_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(dashboard_fix_code)
    
    print("Updated fix_dashboard.py to use UTF-8 encoding")
    
    # Also directly update the experimental_rerun to rerun in the dashboard
    if os.path.exists('ui/broski_dashboard.py'):
        try:
            with open('ui/broski_dashboard.py', 'r', encoding='utf-8', errors='replace') as f:
                dashboard_code = f.read()
            
            # Replace the experimental_rerun with rerun
            updated_code = dashboard_code.replace('st.experimental_rerun()', 'st.rerun()')
            
            with open('ui/broski_dashboard.py', 'w', encoding='utf-8') as f:
                f.write(updated_code)
                
            print("Updated ui/broski_dashboard.py to use st.rerun()")
        except Exception as e:
            print(f"Error updating dashboard: {e}")
    
    print("\nEncoding fixes complete. Now run fix_dashboard.py again:")
    print("python fix_dashboard.py")

if __name__ == "__main__":
    fix_encoding()
