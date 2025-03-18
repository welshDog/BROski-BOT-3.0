#!/usr/bin/env python
"""
BROski Bot 3.0 - Alerts Dashboard Launcher
Quick utility to start the alerts dashboard
"""
import os
import sys
import subprocess
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def main():
    """Launch the alerts dashboard"""
    print(f"{Fore.CYAN}=" * 70)
    print(f"{Fore.CYAN}BROski Bot - Alerts Dashboard Launcher")
    print(f"{Fore.CYAN}=" * 70)
    
    dashboard_path = os.path.join("ui", "alerts_dashboard.py")
    
    # Check if the file exists
    if not os.path.exists(dashboard_path):
        print(f"{Fore.RED}Error: Alerts dashboard file not found at {dashboard_path}")
        return False
    
    print(f"{Fore.GREEN}Starting Alerts Dashboard...")
    print(f"{Fore.YELLOW}This will open in your default web browser.")
    print(f"{Fore.YELLOW}Press Ctrl+C in this terminal to stop the dashboard.")
    
    try:
        # Launch the dashboard using Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path], check=True)
        return True
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Alerts dashboard stopped.")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error launching dashboard: {str(e)}")
        print(f"{Fore.YELLOW}Make sure streamlit is installed: pip install streamlit plotly pandas")
        return False

if __name__ == "__main__":
    main()
