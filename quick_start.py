#!/usr/bin/env python
# Quick Start script for BROski Bot 3.0
"""
BROski Bot 3.0 - QuickStart
DESCRIPTION NEEDED
"""
import os
import sys
import json
import time
import importlib
import subprocess
from colorama import Fore, Style, init as colorama_init

# Initialize colorama
colorama_init(autoreset=True)

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
        """ + Fore.YELLOW + " Crypto Trading Bot - Quick Start" + Fore.RESET)
    print(Fore.CYAN + "=" * 70 + Fore.RESET)

def check_dependencies():
    """Check if all required dependencies are installed"""
    print(Fore.CYAN + "\nChecking dependencies...\n")
    
    try:
        # Load required packages from requirements file
        req_path = os.path.join(PROJECT_DIR, 'docs', 'requirements.txt')
        
        if os.path.exists(req_path):
            # Read and parse the requirements properly, stripping comments
            packages = []
            with open(req_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    # Extract just the package requirement part, not the comment
                    package = line.split('#')[0].strip()
                    if package:
                        packages.append(package)
        else:
            packages = ["ccxt", "pandas", "numpy", "matplotlib", "colorama", "requests"]
        
        # Check each package
        missing_packages = []
        
        for package in packages:
            # Extract just the package name without version specifiers for importing
            package_name = package.split('>=')[0].split('==')[0].split('<')[0].strip()
            try:
                __import__(package_name)
                print(Fore.GREEN + f"✓ {package_name} is installed")
            except ImportError:
                missing_packages.append(package)
                print(Fore.RED + f"✗ {package_name} is missing")
        
        # Install missing packages if any
        if missing_packages:
            print(Fore.YELLOW + "\nSome packages are missing. Installing now...")
            
            for package in missing_packages:
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    print(Fore.GREEN + f"✓ Successfully installed {package}")
                except Exception as e:
                    print(Fore.RED + f"✗ Failed to install {package}: {str(e)}")
                    return False
        
        print(Fore.GREEN + "\nAll dependencies are installed!")
        return True
    
    except Exception as e:
        print(Fore.RED + f"Error checking dependencies: {str(e)}")
        return False

def setup_configuration():
    """Set up the bot configuration"""
    print(Fore.CYAN + "\nSetting up configuration...\n")
    
    try:
        # Check if config file exists
        if os.path.exists(CONFIG_PATH):
            # Read config file with comment support
            try:
                with open(CONFIG_PATH, 'r') as f:
                    # Remove comments and parse JSON
                    config_str = f.read()
                    
                    # Remove JavaScript-style comments
                    import re
                    config_str = re.sub(r'//.*?\n', '\n', config_str)
                    
                    # Try to parse the JSON
                    try:
                        config = json.loads(config_str)
                    except json.JSONDecodeError:
                        # If standard parsing fails, try using a different approach
                        from json import JSONDecoder
                        import re
                        
                        def strip_comments(text):
                            """Strip C-style comments from text"""
                            def replacer(match):
                                s = match.group(0)
                                if s.startswith('/'):
                                    return " " # Replace with a space
                                else:
                                    return s
                            pattern = r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"'
                            regex = re.compile(pattern, re.MULTILINE | re.DOTALL)
                            return regex.sub(replacer, text)
                            
                        # Try with comment stripping
                        clean_config = strip_comments(config_str)
                        config = json.loads(clean_config)
                
            except Exception as e:
                print(Fore.YELLOW + f"Could not parse existing config file: {str(e)}")
                print(Fore.YELLOW + "Creating a new configuration...")
                config = {}
            
            # Check if API key is set - FIXED CONFIG STRUCTURE
            if config.get('exchange', {}).get('api_key'):
                print(Fore.GREEN + "Configuration file already exists and appears to be set up.")
                
                update_config = input(Fore.YELLOW + "Would you like to update your configuration? (y/n): " + Fore.RESET).lower()
                if update_config != 'y':
                    return True
            
            # If we reached here, either config file exists but needs updating, or user wants to update
            print(Fore.YELLOW + "Let's set up your configuration...")
        else:
            # Create default config - ALIGNED WITH CONFIG.JSON STRUCTURE
            config = {
                "version": "3.0.0",
                "exchange": {
                    "name": "mexc",
                    "api_key": "",
                    "api_secret": "",
                    "sandbox_mode": True
                },
                "trading": {
                    "base_symbol": "BTC",
                    "quote_symbol": "USDT",
                    "trade_amount": 10.0,
                    "max_position_size": 50.0,
                    "stop_loss": 2.0,
                    "take_profit": 3.0,
                    "auto_trade": False,
                    "trade_interval": 15,
                    "max_open_trades": 3
                },
                "strategies": {
                    "active_strategy": "ml_strategy",
                    "rsi_strategy": {
                        "enabled": False,
                        "timeframe": "1h",
                        "overbought": 70,
                        "oversold": 30,
                        "rsi_length": 14
                    },
                    "ml_strategy": {
                        "enabled": True,
                        "model_path": "data/models/default_model.pkl",
                        "confidence_threshold": 0.65
                    }
                },
                "risk_management": {
                    "max_drawdown": 10,
                    "max_daily_trades": 5
                }
            }
            
            print(Fore.YELLOW + "Creating a new configuration file...")
        
        # Get user inputs for important configuration items - FIXED CONFIG STRUCTURE
        config['exchange']['api_key'] = input(Fore.CYAN + "Enter your MEXC API Key: " + Fore.RESET) or config['exchange'].get('api_key', '')
        config['exchange']['api_secret'] = input(Fore.CYAN + "Enter your MEXC Secret Key: " + Fore.RESET) or config['exchange'].get('api_secret', '')
        
        # Trading pair
        default_base = config['trading'].get('base_symbol', 'BTC')
        default_quote = config['trading'].get('quote_symbol', 'USDT')
        base_input = input(Fore.CYAN + f"Enter base symbol (default: {default_base}): " + Fore.RESET)
        quote_input = input(Fore.CYAN + f"Enter quote symbol (default: {default_quote}): " + Fore.RESET)
        
        if base_input:
            config['trading']['base_symbol'] = base_input
        if quote_input:
            config['trading']['quote_symbol'] = quote_input
        
        # Default trading amount
        default_amount = config['trading'].get('trade_amount', 10.0)
        amount_input = input(Fore.CYAN + f"Enter default trading amount (default: {default_amount}): " + Fore.RESET)
        if amount_input:
            try:
                config['trading']['trade_amount'] = float(amount_input)
            except ValueError:
                print(Fore.RED + "Invalid amount. Using default.")
        
        # Save the config
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(Fore.GREEN + f"\nConfiguration saved to {CONFIG_PATH}")
        return True
    
    except Exception as e:
        print(Fore.RED + f"Error setting up configuration: {str(e)}")
        return False

def create_directories():
    """Create necessary directories for the bot"""
    print(Fore.CYAN + "\nCreating necessary directories...\n")
    
    try:
        # Create directories
        directories = ['logs', 'data', 'backups']
        
        for directory in directories:
            dir_path = os.path.join(PROJECT_DIR, directory)
            os.makedirs(dir_path, exist_ok=True)
            print(Fore.GREEN + f"✓ Created directory: {directory}")
        
        print(Fore.GREEN + "\nAll directories created!")
        return True
    
    except Exception as e:
        print(Fore.RED + f"Error creating directories: {str(e)}")
        return False

def launch_bot():
    """Launch the BROski Bot"""
    print(Fore.CYAN + "\nLaunching BROski Bot...\n")
    
    try:
        # Launch the unified launcher
        launcher_path = os.path.join(PROJECT_DIR, 'unified_launcher.py')
        
        if os.path.exists(launcher_path):
            print(Fore.GREEN + "Starting BROski Bot Unified Launcher...")
            
            if os.name == 'nt':  # Windows
                subprocess.Popen([sys.executable, launcher_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:  # Linux/Mac
                subprocess.Popen([sys.executable, launcher_path])
                
            print(Fore.GREEN + "BROski Bot launched successfully!")
            return True
        else:
            print(Fore.RED + f"Error: Could not find the launcher at {launcher_path}")
            return False
    
    except Exception as e:
        print(Fore.RED + f"Error launching bot: {str(e)}")
        return False

def setup_wizard():
    """Run the setup wizard"""
    print_header()
    print(Fore.YELLOW + "\nWelcome to the BROski Bot Setup Wizard!")
    print(Fore.YELLOW + "This wizard will guide you through setting up your crypto trading bot.\n")
    
    steps = [
        ("Checking dependencies", check_dependencies),
        ("Creating directories", create_directories),
        ("Setting up configuration", setup_configuration),
        ("Launching BROski Bot", launch_bot)
    ]
    
    success = True
    for step_name, step_func in steps:
        print(Fore.CYAN + f"\n{step_name}...")
        if not step_func():
            print(Fore.RED + f"\nFailed at step: {step_name}")
            success = False
            break
        time.sleep(1)
    
    if success:
        print(Fore.GREEN + "\n🎉 Setup completed successfully! BROski Bot is now running.")
        print(Fore.GREEN + "Use the unified launcher to control all aspects of your bot.\n")
    else:
        print(Fore.RED + "\n❌ Setup failed. Please check the errors above and try again.")
        print(Fore.YELLOW + "You can manually launch the bot by running 'python unified_launcher.py'\n")
    
    input(Fore.CYAN + "Press Enter to exit the setup wizard..." + Fore.RESET)

if __name__ == "__main__":
    setup_wizard()
