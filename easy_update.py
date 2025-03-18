#!/usr/bin/env python
"""
BROski Bot - Easy Update and Maintenance Tool
Handles common maintenance tasks in one place
"""
import os
import sys
import json
import shutil
import subprocess
import time
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init(autoreset=True)

# Project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_DIR, 'config.json')

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the BROski Bot header"""
    clear_screen()
    print(Fore.CYAN + """
▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄    ▄  ▄▄▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌  ▐░▌▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░▌ ▐░▌ ▐░█▀▀▀▀▀▀▀▀▀ 
▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌▐░▌          ▐░▌▐░▌  ▐░▌          
▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░▌░▌   ▐░█▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░▌    ▐░░░░░░░░░░░▌
▐░█▀▀▀▀█░█▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░▌       ▐░▌ ▀▀▀▀▀▀▀▀▀█░▌▐░▌░▌   ▐░█▀▀▀▀▀▀▀▀▀ 
▐░▌     ▐░▌  ▐░▌       ▐░▌▐░▌       ▐░▌          ▐░▌▐░▌▐░▌  ▐░▌          
▐░▌      ▐░▌ ▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄█░▌ ▄▄▄▄▄▄▄▄▄█░▌▐░▌ ▐░▌ ▐░█▄▄▄▄▄▄▄▄▄ 
▐░▌       ▐░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌  ▐░▌▐░░░░░░░░░░░▌
 ▀         ▀  ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀    ▀  ▀▀▀▀▀▀▀▀▀▀▀ 
        """ + Fore.YELLOW + " Easy Update & Maintenance" + Fore.RESET)
    print(Fore.CYAN + "=" * 70 + Fore.RESET)

def update_dependencies():
    """Update all dependencies to latest versions"""
    print(Fore.CYAN + "\nUpdating dependencies...\n")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '-r', 
                             os.path.join(PROJECT_DIR, 'docs', 'requirements.txt')])
        print(Fore.GREEN + "✓ Dependencies updated successfully!")
    except Exception as e:
        print(Fore.RED + f"✗ Error updating dependencies: {str(e)}")
    
    input(Fore.CYAN + "\nPress Enter to continue..." + Fore.RESET)

def clean_logs():
    """Clean old log files"""
    print(Fore.CYAN + "\nCleaning old log files...\n")
    
    logs_dir = os.path.join(PROJECT_DIR, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(Fore.YELLOW + "Created logs directory (it didn't exist)")
        input(Fore.CYAN + "\nPress Enter to continue..." + Fore.RESET)
        return
    
    try:
        log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
        if not log_files:
            print(Fore.YELLOW + "No log files found.")
            input(Fore.CYAN + "\nPress Enter to continue..." + Fore.RESET)
            return
            
        # Sort by modification time (oldest first)
        log_files.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)))
        
        # Keep only the 10 most recent logs
        if len(log_files) > 10:
            for old_log in log_files[:-10]:
                os.remove(os.path.join(logs_dir, old_log))
            
            print(Fore.GREEN + f"✓ Removed {len(log_files) - 10} old log files")
        else:
            print(Fore.GREEN + "✓ No cleanup needed (less than 10 log files)")
            
    except Exception as e:
        print(Fore.RED + f"✗ Error cleaning logs: {str(e)}")
    
    input(Fore.CYAN + "\nPress Enter to continue..." + Fore.RESET)

def backup_config():
    """Backup configuration files"""
    print(Fore.CYAN + "\nBacking up configuration...\n")
    
    backup_dir = os.path.join(PROJECT_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    try:
        # Create timestamp for backup file
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'config_{timestamp}.json')
        
        # Copy config to backup location
        shutil.copy2(CONFIG_PATH, backup_file)
        
        print(Fore.GREEN + f"✓ Configuration backed up to: {backup_file}")
    except Exception as e:
        print(Fore.RED + f"✗ Error backing up configuration: {str(e)}")
    
    input(Fore.CYAN + "\nPress Enter to continue..." + Fore.RESET)

def check_system():
    """Run system check"""
    print(Fore.CYAN + "\nRunning system check...\n")
    
    try:
        check_script = os.path.join(PROJECT_DIR, 'utils', 'check_system.py')
        subprocess.call([sys.executable, check_script])
    except Exception as e:
        print(Fore.RED + f"✗ Error running system check: {str(e)}")
    
    input(Fore.CYAN + "\nPress Enter to continue..." + Fore.RESET)

def select_trading_style():
    """Run trading style selector"""
    print(Fore.CYAN + "\nLaunching trading style selector...\n")
    
    try:
        selector_script = os.path.join(PROJECT_DIR, 'utils', 'trading_style_selector.py')
        subprocess.call([sys.executable, selector_script])
    except Exception as e:
        print(Fore.RED + f"✗ Error running trading style selector: {str(e)}")

def launch_bot():
    """Launch the bot"""
    print(Fore.CYAN + "\nLaunching BROski Bot...\n")
    
    try:
        launcher_script = os.path.join(PROJECT_DIR, 'unified_launcher.py')
        
        if os.name == 'nt':  # Windows
            subprocess.Popen([sys.executable, launcher_script], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Mac
            subprocess.Popen([sys.executable, launcher_script])
            
        print(Fore.GREEN + "✓ BROski Bot launched!")
    except Exception as e:
        print(Fore.RED + f"✗ Error launching bot: {str(e)}")
    
    input(Fore.CYAN + "\nPress Enter to continue..." + Fore.RESET)

def main_menu():
    """Display main menu and handle user selection"""
    while True:
        print_header()
        
        print(Fore.CYAN + "\nEasy Maintenance Options:\n")
        print(Fore.WHITE + "1. " + Fore.GREEN + "Update Dependencies")
        print(Fore.WHITE + "2. " + Fore.GREEN + "Clean Old Log Files")
        print(Fore.WHITE + "3. " + Fore.GREEN + "Backup Configuration")
        print(Fore.WHITE + "4. " + Fore.GREEN + "Run System Check")
        print(Fore.WHITE + "5. " + Fore.GREEN + "Select Trading Style")
        print(Fore.WHITE + "6. " + Fore.GREEN + "Launch BROski Bot")
        print(Fore.WHITE + "0. " + Fore.RED + "Exit")
        
        choice = input(Fore.CYAN + "\nEnter your choice: " + Fore.RESET)
        
        if choice == "1":
            update_dependencies()
        elif choice == "2":
            clean_logs()
        elif choice == "3":
            backup_config()
        elif choice == "4":
            check_system()
        elif choice == "5":
            select_trading_style()
        elif choice == "6":
            launch_bot()
        elif choice == "0":
            print(Fore.YELLOW + "\nExiting Easy Update & Maintenance. Goodbye!")
            sys.exit(0)
        else:
            print(Fore.RED + "\nInvalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
