#!/usr/bin/env python
"""
BROski Bot 3.0 - Brain Hub Launcher Fix
Fixes the imghdr module issue and launches Brain Hub
"""
import os
import sys
import subprocess
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def main():
    """Fix and launch the BROski Brain Hub"""
    print(f"{Fore.CYAN}=" * 70)
    print(f"{Fore.CYAN}BROski Bot - Brain Hub Fix Utility")
    print(f"{Fore.CYAN}=" * 70)
    
    dashboard_path = os.path.join("ui", "broski_brain_hub.py")
    
    # Check if the file exists
    if not os.path.exists(dashboard_path):
        print(f"{Fore.RED}Error: Brain Hub dashboard file not found at {dashboard_path}")
        return False
    
    # First, try to fix the missing dependency issue
    print(f"{Fore.YELLOW}Step 1: Reinstalling required dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "streamlit", "plotly", "pandas", "pillow"], check=True)
        print(f"{Fore.GREEN}✅ Packages upgraded successfully")
    except Exception as e:
        print(f"{Fore.RED}Warning: Package installation had issues: {str(e)}")
    
    # Verify if Python has the standard library module
    try:
        print(f"{Fore.YELLOW}Step 2: Checking Python standard library...")
        import importlib
        importlib.import_module('imghdr')
        print(f"{Fore.GREEN}✅ imghdr module is now available")
    except ImportError:
        print(f"{Fore.RED}Warning: imghdr module still not available. This is unusual.")
        print(f"{Fore.YELLOW}Will attempt alternate method to launch.")
    
    print(f"{Fore.GREEN}Starting BROski Brain Hub with simplified settings...")
    print(f"{Fore.YELLOW}This will open in your default web browser.")
    print(f"{Fore.YELLOW}Press Ctrl+C in this terminal to stop the Brain Hub.")
    
    try:
        # Launch the dashboard using Streamlit with minimal arguments
        print(f"{Fore.YELLOW}Using simplified launch command...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path], check=True)
        return True
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Brain Hub stopped.")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error launching Brain Hub: {str(e)}")
        
        # Provide troubleshooting advice
        print(f"\n{Fore.YELLOW}========== TROUBLESHOOTING ==========")
        print(f"{Fore.WHITE}1. Try installing Python 3.9 or 3.10 which should include all standard libraries")
        print(f"{Fore.WHITE}2. Create a new virtual environment: python -m venv new_venv")
        print(f"{Fore.WHITE}3. Activate it and install required packages")
        print(f"{Fore.WHITE}4. Try individual components (alerts_dashboard.py, performance_dashboard.py) instead")
        
        return False

if __name__ == "__main__":
    main()
