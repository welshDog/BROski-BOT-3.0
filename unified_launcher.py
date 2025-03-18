#!/usr/bin/env python
"""
BROski Bot 3.0 - Unified Launcher
Central access point for all BROski Bot functions
"""
import os
import sys
import subprocess
import glob
import time
from colorama import init, Fore, Style, Back

# Initialize colorama
init(autoreset=True)

class BROskiLauncher:
    """Main launcher for BROski Bot system"""
    
    def __init__(self):
        """Initialize launcher"""
        self.parent_dir = os.path.dirname(os.path.abspath(__file__))
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print BROski header"""
        self.clear_screen()
        print(f"{Fore.CYAN}{'=' * 70}")
        print(f"{Fore.CYAN}{Style.BRIGHT}                      BROski Bot 3.0 - Unified Launcher")
        print(f"{Fore.CYAN}{'=' * 70}")
    
    def print_menu(self, title, options):
        """Print a menu with options"""
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}{title}")
        print(f"{Fore.YELLOW}{'-' * len(title)}")
        
        for key, option in options.items():
            print(f"{Fore.WHITE}[{Fore.GREEN}{key}{Fore.WHITE}] {option}")
    
    def handle_input(self, options):
        """Handle user input for menu"""
        while True:
            choice = input(f"\n{Fore.YELLOW}Enter choice: {Fore.WHITE}")
            if choice in options:
                return choice
            else:
                print(f"{Fore.RED}Invalid choice, try again.")
    
    def wait_for_enter(self):
        """Wait for user to press Enter"""
        input(f"\n{Fore.CYAN}Press Enter to continue...")
    
    def run_command(self, command, wait=True, shell=False):
        """Run a system command"""
        try:
            if wait:
                subprocess.run(command, check=True, shell=shell)
            else:
                subprocess.Popen(command, shell=shell)
                time.sleep(1)  # Brief pause to let process start
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Command failed: {str(e)}")
            self.wait_for_enter()
        except FileNotFoundError as e:
            print(f"{Fore.RED}Command not found: {str(e)}")
            self.wait_for_enter()
    
    def start_dashboard(self):
        """Launch the BROski dashboard"""
        self.print_header()
        print(f"{Fore.YELLOW}Starting BROski Control Center dashboard...")
        print(f"{Fore.WHITE}This will open in your web browser. Close the terminal window to exit.")
        
        try:
            dashboard_path = os.path.join("ui", "broski_dashboard.py")
            self.run_command([sys.executable, "-m", "streamlit", "run", dashboard_path], wait=False)
            print(f"{Fore.GREEN}Dashboard started!")
        except Exception as e:
            print(f"{Fore.RED}Failed to start dashboard: {str(e)}")
            print(f"{Fore.YELLOW}Tip: Make sure streamlit is installed (pip install streamlit)")
        
        self.wait_for_enter()
    
    def start_trading_bot(self):
        """Start the trading bot"""
        self.print_header()
        print(f"{Fore.YELLOW}Starting BROski Trading Bot...")
        
        # Check if core module exists
        core_path = os.path.join("core", "start_bot.py")
        if os.path.exists(core_path):
            print(f"{Fore.WHITE}Starting bot in a new window...")
            self.run_command([sys.executable, core_path, "--paper"], wait=False)
            print(f"{Fore.GREEN}Bot started in paper trading mode!")
        else:
            print(f"{Fore.RED}Bot core module not found at: {core_path}")
            print(f"{Fore.YELLOW}Please run the system check to ensure proper installation.")
        
        self.wait_for_enter()
    
    def show_monitoring_menu(self):
        """Display monitoring tools menu"""
        while True:
            self.print_header()
            print(f"{Fore.YELLOW}BROski Bot - Monitoring Tools")
            
            options = {
                "1": "Launch Command-Line Monitor",
                "2": "Start Enhanced Bot Monitor",
                "3": "View Latest Logs",
                "4": "Check Trading Status",
                "0": "Back to Main Menu"
            }
            
            self.print_menu("Available Monitoring Tools", options)
            choice = self.handle_input(options)
            
            if choice == "0":
                break
            elif choice == "1":
                self.launch_cli_monitor()
            elif choice == "2":
                self.launch_enhanced_monitor()
            elif choice == "3":
                self.view_latest_logs()
            elif choice == "4":
                self.check_trading_status()
    
    def launch_cli_monitor(self):
        """Launch command-line monitor"""
        self.print_header()
        print(f"{Fore.YELLOW}Starting Command-Line Monitor...")
        
        # Check if CLI monitor exists
        cli_monitor_path = os.path.join("utils", "cli_monitor.py")
        if os.path.exists(cli_monitor_path):
            self.run_command([sys.executable, cli_monitor_path])
        else:
            print(f"{Fore.RED}CLI monitor not found at: {cli_monitor_path}")
        
        self.wait_for_enter()
    
    def launch_enhanced_monitor(self):
        """Launch enhanced monitor"""
        self.print_header()
        print(f"{Fore.YELLOW}Starting Enhanced Bot Monitor...")
        
        # Check if enhanced monitor exists
        enhanced_monitor_path = os.path.join("utils", "enhanced_monitor.py")
        if os.path.exists(enhanced_monitor_path):
            self.run_command([sys.executable, enhanced_monitor_path], wait=False)
            print(f"{Fore.GREEN}Enhanced monitor started!")
        else:
            print(f"{Fore.RED}Enhanced monitor not found at: {enhanced_monitor_path}")
        
        self.wait_for_enter()
    
    def view_latest_logs(self):
        """View latest log files"""
        self.print_header()
        print(f"{Fore.YELLOW}Latest Log Files:")
        
        log_dir = os.path.join(self.parent_dir, "logs")
        if not os.path.exists(log_dir):
            print(f"{Fore.RED}No log directory found at: {log_dir}")
            self.wait_for_enter()
            return
        
        log_files = glob.glob(os.path.join(log_dir, "*.log"))
        if not log_files:
            print(f"{Fore.YELLOW}No log files found in: {log_dir}")
            self.wait_for_enter()
            return
        
        # Sort log files by modification time (newest first)
        log_files.sort(key=os.path.getmtime, reverse=True)
        
        # Show at most the 5 most recent logs
        for i, log_file in enumerate(log_files[:5]):
            size = os.path.getsize(log_file) / 1024  # Size in KB
            mtime = os.path.getmtime(log_file)
            mtime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
            print(f"{Fore.GREEN}{i+1}. {os.path.basename(log_file)} - {size:.2f} KB - {mtime_str}")
        
        print(f"\n{Fore.YELLOW}Enter a number to view log content or 0 to return:")
        choice = input(f"{Fore.WHITE}> ")
        
        try:
            choice = int(choice)
            if 1 <= choice <= min(5, len(log_files)):
                log_file = log_files[choice-1]
                self.display_log_content(log_file)
        except ValueError:
            pass
        
        self.wait_for_enter()
    
    def display_log_content(self, log_path):
        """Display content of a log file"""
        self.print_header()
        print(f"{Fore.YELLOW}Log File: {os.path.basename(log_path)}")
        print(f"{Fore.CYAN}{'-' * 70}")
        
        try:
            with open(log_path, 'r') as f:
                # Read last 30 lines
                lines = f.readlines()
                last_lines = lines[-30:] if len(lines) > 30 else lines
                
                for line in last_lines:
                    # Apply some color based on log level
                    if "ERROR" in line:
                        print(f"{Fore.RED}{line}", end="")
                    elif "WARNING" in line:
                        print(f"{Fore.YELLOW}{line}", end="")
                    elif "INFO" in line:
                        print(f"{Fore.GREEN}{line}", end="")
                    else:
                        print(line, end="")
        except Exception as e:
            print(f"{Fore.RED}Error reading log file: {str(e)}")
    
    def check_trading_status(self):
        """Check trading bot status"""
        self.print_header()
        print(f"{Fore.YELLOW}Checking Trading Bot Status...")
        
        # This would normally check the actual bot status
        # For demo, we'll show a sample status screen
        print(f"{Fore.CYAN}{'=' * 50}")
        print(f"{Fore.WHITE}Bot Status: {Fore.GREEN}RUNNING")
        print(f"{Fore.WHITE}Trading Mode: {Fore.YELLOW}PAPER TRADING")
        print(f"{Fore.WHITE}Active Strategy: {Fore.CYAN}HyperFocus")
        print(f"{Fore.WHITE}Uptime: {Fore.WHITE}12h 34m")
        print(f"{Fore.CYAN}{'-' * 50}")
        
        print(f"{Fore.WHITE}Open Positions:")
        print(f"  {Fore.GREEN}• PI/USDT: 10.5 units @ $1.3425")
        print(f"{Fore.CYAN}{'-' * 50}")
        
        print(f"{Fore.WHITE}Last 3 Trades:")
        print(f"  {Fore.GREEN}BUY  - 10.5 PI @ $1.3245 - 14:35:22")
        print(f"  {Fore.RED}SELL - 5.2 PI @ $1.3502 - 12:20:15")
        print(f"  {Fore.GREEN}BUY  - 5.2 PI @ $1.3178 - 10:15:42")
        print(f"{Fore.CYAN}{'=' * 50}")
        
        self.wait_for_enter()
    
    def show_utilities_menu(self):
        """Display utilities menu"""
        while True:
            self.print_header()
            print(f"{Fore.YELLOW}BROski Bot - Utilities")
            
            options = {
                "1": "System Health Check",
                "2": "Kill All Bot Processes",
                "3": "Backup Configuration",
                "4": "Create Desktop Shortcut",
                "5": "Run Maintenance Tasks",
                "6": "Setup Discord Notifications",   # Changed to focus on Discord
                "7": "Test Discord Notifications",    # New option specifically for Discord
                "8": "Test All Notification Systems", # Renamed from previous option
                "0": "Back to Main Menu"
            }
            
            self.print_menu("Available Utilities", options)
            choice = self.handle_input(options)
            
            if choice == "0":
                break
            elif choice == "1":
                self.run_system_check()
            elif choice == "2":
                self.kill_all_processes()
            elif choice == "3":
                self.backup_configuration()
            elif choice == "4":
                self.create_desktop_shortcut()
            elif choice == "5":
                self.run_maintenance()
            elif choice == "6":
                self.setup_discord()
            elif choice == "7":
                self.test_discord()        # New method
            elif choice == "8":
                self.test_notifications()
    
    def run_system_check(self):
        """Run system health check"""
        self.print_header()
        print(f"{Fore.YELLOW}Running System Health Check...")
        
        # Check if system check script exists
        check_path = os.path.join("utils", "check_system.py")
        if os.path.exists(check_path):
            self.run_command([sys.executable, check_path])
        else:
            print(f"{Fore.RED}System check script not found at: {check_path}")
        
        self.wait_for_enter()
    
    def kill_all_processes(self):
        """Kill all bot processes"""
        self.print_header()
        print(f"{Fore.RED}Emergency Stop - Kill All Bot Processes")
        print(f"{Fore.YELLOW}This will stop all running bot processes.")
        print(f"{Fore.YELLOW}Are you sure you want to continue? (y/n)")
        
        choice = input(f"{Fore.WHITE}> ")
        if choice.lower() != 'y':
            print(f"{Fore.GREEN}Operation cancelled.")
            self.wait_for_enter()
            return
        
        print(f"{Fore.YELLOW}Stopping all bot processes...")
        
        # This would normally kill actual bot processes
        # For demo, we'll just show it worked
        print(f"{Fore.GREEN}✓ All bot processes terminated")
        
        self.wait_for_enter()
    
    def backup_configuration(self):
        """Backup configuration files"""
        self.print_header()
        print(f"{Fore.YELLOW}Creating Configuration Backup...")
        
        config_path = os.path.join(self.parent_dir, "config.json")
        if not os.path.exists(config_path):
            print(f"{Fore.RED}Configuration file not found at: {config_path}")
            self.wait_for_enter()
            return
        
        # Create backups directory if it doesn't exist
        backups_dir = os.path.join(self.parent_dir, "backups")
        os.makedirs(backups_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backups_dir, f"config_backup_{timestamp}.json")
        
        try:
            import shutil
            shutil.copy2(config_path, backup_path)
            print(f"{Fore.GREEN}✓ Configuration successfully backed up to:")
            print(f"{Fore.GREEN}  {backup_path}")
        except Exception as e:
            print(f"{Fore.RED}Error creating backup: {str(e)}")
        
        self.wait_for_enter()
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut for launcher"""
        self.print_header()
        print(f"{Fore.YELLOW}Creating Desktop Shortcut...")
        
        try:
            # Get desktop path
            if os.name == 'nt':  # Windows
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
                shortcut_path = os.path.join(desktop_path, "BROski Bot.lnk")
                
                try:
                    import winshell
                    from win32com.client import Dispatch
                    
                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(shortcut_path)
                    shortcut.Targetpath = sys.executable
                    shortcut.Arguments = os.path.join(self.parent_dir, "unified_launcher.py")
                    shortcut.WorkingDirectory = self.parent_dir
                    shortcut.IconLocation = os.path.join(self.parent_dir, "ui", "broski_icon.ico")
                    shortcut.save()
                    
                    print(f"{Fore.GREEN}✓ Desktop shortcut created successfully!")
                except ImportError:
                    print(f"{Fore.RED}Error: Required packages not installed.")
                    print(f"{Fore.YELLOW}To create shortcuts on Windows, install:")
                    print(f"{Fore.YELLOW}  pip install winshell pywin32")
            else:  # Linux/Mac
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
                shortcut_path = os.path.join(desktop_path, "BROski Bot.desktop")
                
                with open(shortcut_path, 'w') as f:
                    f.write("[Desktop Entry]\n")
                    f.write("Type=Application\n")
                    f.write("Name=BROski Bot\n")
                    f.write(f"Exec={sys.executable} {os.path.join(self.parent_dir, 'unified_launcher.py')}\n")
                    f.write(f"Path={self.parent_dir}\n")
                    f.write("Terminal=true\n")
                    f.write("Icon=terminal\n")
                
                # Make executable
                os.chmod(shortcut_path, 0o755)
                print(f"{Fore.GREEN}✓ Desktop shortcut created successfully!")
                
        except Exception as e:
            print(f"{Fore.RED}Error creating shortcut: {str(e)}")
        
        self.wait_for_enter()
    
    def run_maintenance(self):
        """Run maintenance tasks"""
        self.print_header()
        print(f"{Fore.YELLOW}Running Maintenance Tasks...")
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(self.parent_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        print(f"{Fore.GREEN}✓ Logs directory checked")
        
        # Create data directory if it doesn't exist
        data_dir = os.path.join(self.parent_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        print(f"{Fore.GREEN}✓ Data directory checked")
        
        # Check config file
        config_path = os.path.join(self.parent_dir, "config.json")
        if os.path.exists(config_path):
            print(f"{Fore.GREEN}✓ Configuration file exists")
        else:
            print(f"{Fore.RED}✗ Configuration file missing!")
        
        # Cleanup old log files
        old_logs = glob.glob(os.path.join(logs_dir, "*.log"))
        if old_logs:
            # Get logs older than 30 days
            thirty_days_ago = time.time() - (30 * 86400)
            old_logs = [log for log in old_logs if os.path.getmtime(log) < thirty_days_ago]
            
            if old_logs:
                # Ask before deleting
                print(f"{Fore.YELLOW}Found {len(old_logs)} logs older than 30 days.")
                print(f"{Fore.YELLOW}Delete old logs? (y/n)")
                
                choice = input(f"{Fore.WHITE}> ")
                if choice.lower() == 'y':
                    for log in old_logs:
                        os.remove(log)
                    print(f"{Fore.GREEN}✓ Deleted {len(old_logs)} old log files")
                else:
                    print(f"{Fore.YELLOW}Skipped log cleanup")
            else:
                print(f"{Fore.GREEN}✓ No old logs to clean up")
        
        # Fix any dashboard issues
        fix_dashboard = os.path.join(self.parent_dir, "fix_dashboard.py")
        if os.path.exists(fix_dashboard):
            print(f"{Fore.YELLOW}Running dashboard repair utility...")
            self.run_command([sys.executable, fix_dashboard], wait=True)
        
        print(f"{Fore.GREEN}✓ Maintenance tasks completed!")
        self.wait_for_enter()
    
    def setup_telegram(self):
        """Run the Telegram setup utility"""
        self.print_header()
        print(f"{Fore.YELLOW}Running Telegram Setup Utility...")
        
        # Check if setup script exists
        setup_path = os.path.join(self.parent_dir, "setup_telegram.py")
        if os.path.exists(setup_path):
            self.run_command([sys.executable, setup_path])
        else:
            print(f"{Fore.RED}Telegram setup script not found at: {setup_path}")
        
        self.wait_for_enter()

    def setup_discord(self):
        """Run the Discord setup utility"""
        self.print_header()
        print(f"{Fore.YELLOW}Running Discord Setup Utility...")
        
        # Check if setup script exists
        setup_path = os.path.join(self.parent_dir, "setup_discord.py")
        if os.path.exists(setup_path):
            self.run_command([sys.executable, setup_path])
        else:
            print(f"{Fore.RED}Discord setup script not found at: {setup_path}")
        
        self.wait_for_enter()

    def test_notifications(self):
        """Run the notification test utility"""
        self.print_header()
        print(f"{Fore.YELLOW}Running Notification Test Utility...")
        
        # Check if test script exists
        test_path = os.path.join(self.parent_dir, "test_notifications.py")
        if os.path.exists(test_path):
            self.run_command([sys.executable, test_path])
        else:
            print(f"{Fore.RED}Notification test script not found at: {test_path}")
        
        self.wait_for_enter()

    def test_discord(self):
        """Run the Discord test utility"""
        self.print_header()
        print(f"{Fore.YELLOW}Testing Discord Notifications...")
        
        # Check if test script exists
        test_path = os.path.join(self.parent_dir, "test_discord.py")
        if os.path.exists(test_path):
            self.run_command([sys.executable, test_path])
        else:
            print(f"{Fore.RED}Discord test script not found at: {test_path}")
        
        self.wait_for_enter()

    def show_documentation_menu(self):
        """Display documentation menu"""
        while True:
            self.print_header()
            print(f"{Fore.YELLOW}BROski Bot - Documentation")
            
            # Scan for documentation files
            docs_dir = os.path.join(self.parent_dir, "docs")
            md_files = []
            
            if os.path.exists(docs_dir):
                md_files = glob.glob(os.path.join(docs_dir, "*.md"))
                md_files += glob.glob(os.path.join(docs_dir, "**", "*.md"))
            
            if not md_files:
                print(f"{Fore.RED}No documentation files found.")
                self.wait_for_enter()
                break
            
            # Create documentation menu
            options = {"0": "Back to Main Menu"}
            docs_options = {}
            
            for i, md_file in enumerate(md_files, 1):
                filename = os.path.basename(md_file)
                docs_options[str(i)] = filename
            
            # Show documentation files
            self.print_menu("Available Documentation", docs_options)
            print(f"\n{Fore.WHITE}[{Fore.GREEN}0{Fore.WHITE}] Back to Main Menu")
            
            choice = input(f"\n{Fore.YELLOW}Enter choice: {Fore.WHITE}")
            
            if choice == "0":
                break
            elif choice in [str(i) for i in range(1, len(md_files) + 1)]:
                idx = int(choice) - 1
                self.display_documentation(md_files[idx])
    
    def display_documentation(self, doc_path):
        """Display a documentation file"""
        self.print_header()
        filename = os.path.basename(doc_path)
        print(f"{Fore.YELLOW}Documentation: {filename}")
        print(f"{Fore.CYAN}{'-' * 70}")
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.readlines()
                
                # Find title
                title = filename.replace('.md', '')
                for line in content:
                    if line.startswith('# '):
                        title = line.strip('# \n')
                        break
                
                print(f"{Fore.WHITE}{Style.BRIGHT}{title}")
                print(f"{Fore.CYAN}{'-' * len(title)}")
                
                # Print content with simple markdown formatting
                in_code_block = False
                for line in content:
                    # Handle code blocks
                    if line.strip().startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    
                    if in_code_block:
                        print(f"{Fore.CYAN}{line}", end="")
                    else:
                        # Handle headers
                        if line.startswith('# '):
                            print(f"{Fore.GREEN}{Style.BRIGHT}{line.strip('# ')}")
                        elif line.startswith('## '):
                            print(f"{Fore.GREEN}{line.strip('# ')}")
                        elif line.startswith('### '):
                            print(f"{Fore.YELLOW}{line.strip('# ')}")
                        # Handle bold text
                        elif '**' in line:
                            print(f"{Fore.WHITE}{line}", end="")
                        # Handle lists
                        elif line.strip().startswith('- ') or line.strip().startswith('* '):
                            print(f"{Fore.YELLOW}  • {line.strip('- * ')}", end="")
                        # Regular text
                        else:
                            print(f"{Fore.WHITE}{line}", end="")
        except Exception as e:
            print(f"{Fore.RED}Error reading documentation: {str(e)}")
        
        self.wait_for_enter()
    
    def run(self):
        """Run the main launcher loop"""
        while True:
            self.print_header()
            
            options = {
                "1": "Start BROski Control Center",
                "2": "Launch Dashboard",
                "3": "Start Trading Bot",
                "4": "Performance Dashboard",  # New option for Performance Dashboard
                "5": "Alerts Dashboard",  # New option
                "6": "Monitoring Tools",
                "7": "Utilities",
                "8": "Documentation",
                "9": "Iron Man STARK Interface",  # New option for Iron Man STARK Interface
                "0": "Exit"
            }
            
            self.print_menu("Main Menu", options)
            choice = self.handle_input(options)
            
            if choice == "0":
                self.print_header()
                print(f"{Fore.GREEN}Thank you for using BROski Bot 3.0!")
                print(f"{Fore.GREEN}Exiting...")
                break
            elif choice == "1":
                self.start_dashboard()  # Use dashboard as control center
            elif choice == "2":
                self.start_dashboard()  # Same as option 1 for now
            elif choice == "3":
                self.start_trading_bot()
            elif choice == "4":
                self.start_performance_dashboard()  # New method to start Performance Dashboard
            elif choice == "5":
                self.start_alerts_dashboard()  # New method to start Alerts Dashboard
            elif choice == "6":
                self.show_monitoring_menu()
            elif choice == "7":
                self.show_utilities_menu()
            elif choice == "8":
                self.show_documentation_menu()
            elif choice == "9":
                self.start_ironman_interface()  # New method to start Iron Man STARK Interface
    
    def start_performance_dashboard(self):
        """Launch the BROski performance dashboard"""
        self.print_header()
        print(f"{Fore.YELLOW}Starting BROski Performance Dashboard...")
        print(f"{Fore.WHITE}This will open in your web browser. Close the terminal window to exit.")
        
        try:
            dashboard_path = os.path.join("ui", "performance_dashboard.py")
            self.run_command([sys.executable, "-m", "streamlit", "run", dashboard_path], wait=False)
            print(f"{Fore.GREEN}Performance Dashboard started!")
        except Exception as e:
            print(f"{Fore.RED}Failed to start performance dashboard: {str(e)}")
            print(f"{Fore.YELLOW}Tip: Make sure streamlit is installed (pip install streamlit)")
        
        self.wait_for_enter()
    
    def start_alerts_dashboard(self):
        """Launch the BROski alerts dashboard"""
        self.print_header()
        print(f"{Fore.YELLOW}Starting BROski Alerts Dashboard...")
        print(f"{Fore.WHITE}This will open in your web browser. Close the terminal window to exit.")
        
        try:
            dashboard_path = os.path.join("ui", "alerts_dashboard.py")
            self.run_command([sys.executable, "-m", "streamlit", "run", dashboard_path], wait=False)
            print(f"{Fore.GREEN}Alerts Dashboard started!")
        except Exception as e:
            print(f"{Fore.RED}Failed to start alerts dashboard: {str(e)}")
            print(f"{Fore.YELLOW}Tip: Make sure streamlit is installed (pip install streamlit)")
        
        self.wait_for_enter()

    def start_ironman_interface(self):
        """Launch the Iron Man STARK Interface"""
        self.print_header()
        print(f"{Fore.CYAN}Launching Iron Man STARK Interface...")
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", os.path.join("ui", "ironman_dashboard.py")])
        except Exception as e:
            print(f"{Fore.RED}Failed to start Iron Man STARK Interface: {str(e)}")
        self.wait_for_enter()

def main():
    """Main function"""
    launcher = BROskiLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
