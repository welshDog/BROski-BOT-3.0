#!/usr/bin/env python
"""
Remove EMERGENCY_STOP file to allow bot to start
"""
import os
import sys
import time
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def main():
    """Find and remove EMERGENCY_STOP file"""
    # Get the project root directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    emergency_file = os.path.join(project_dir, 'EMERGENCY_STOP')
    
    print(Fore.CYAN + "BROski Bot - Emergency Stop File Removal Utility")
    print(Fore.CYAN + "=" * 50)
    
    if os.path.exists(emergency_file):
        print(Fore.YELLOW + f"Found EMERGENCY_STOP file at: {emergency_file}")
        print(Fore.YELLOW + "This file prevents the bot from starting as a safety measure.")
        
        confirm = input(Fore.YELLOW + "Remove this file and allow the bot to start? (y/n): ")
        
        if confirm.lower() == 'y':
            try:
                # Remove the file
                os.remove(emergency_file)
                print(Fore.GREEN + "✅ EMERGENCY_STOP file successfully removed!")
                print(Fore.GREEN + "You can now start the bot.")
            except Exception as e:
                print(Fore.RED + f"Error removing file: {str(e)}")
                print(Fore.RED + "You may need administrator privileges.")
                return False
        else:
            print(Fore.YELLOW + "Operation cancelled. EMERGENCY_STOP file remains in place.")
            return False
    else:
        print(Fore.GREEN + "No EMERGENCY_STOP file found. The bot should start normally.")
    
    return True

if __name__ == "__main__":
    success = main()
    
    # Keep terminal open on Windows
    if os.name == 'nt':
        if not success:
            print(Fore.YELLOW + "\nPress Enter to exit...")
            input()
