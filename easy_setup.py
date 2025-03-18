"""
One-click setup script for BROski Bot 3.0.

This script automates the entire setup process including:
- Creating a virtual environment
- Installing all dependencies
- Setting up initial configuration
- Running system compatibility checks
- Installing optional dependencies

Run this script to get started with minimal effort.
"""

import os
import sys
import platform
import subprocess
import json
import shutil
from pathlib import Path
import time

# ANSI color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_status(message, status_type="info"):
    """Print a formatted status message."""
    prefix = {
        "success": f"{GREEN}✓ SUCCESS:{RESET}",
        "info": f"{BLUE}ℹ INFO:{RESET}",
        "warning": f"{YELLOW}⚠ WARNING:{RESET}",
        "error": f"{RED}✗ ERROR:{RESET}",
        "step": f"{BOLD}→ STEP:{RESET}"
    }.get(status_type, f"{BLUE}ℹ INFO:{RESET}")
    
    print(f"{prefix} {message}")


def run_command(command, cwd=None, env=None, check=True):
    """Run a shell command and handle errors."""
    print_status(f"Running: {' '.join(command)}", "info")
    try:
        process = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return True, process.stdout
    except subprocess.CalledProcessError as e:
        print_status(f"Command failed: {e}", "error")
        print_status(f"Error output: {e.stderr}", "error")
        return False, e.stderr


def is_venv():
    """Check if running inside a virtual environment."""
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )


def create_virtual_env():
    """Create a virtual environment for BROski Bot."""
    print_status("Creating virtual environment...", "step")
    
    # Check if virtual env already exists
    venv_path = Path(".venv")
    if venv_path.exists():
        print_status("Virtual environment already exists", "info")
        return True
    
    # Create virtual environment
    success, output = run_command([sys.executable, "-m", "venv", ".venv"])
    if success:
        print_status("Virtual environment created successfully", "success")
        return True
    else:
        print_status("Failed to create virtual environment", "error")
        return False


def activate_venv():
    """Return the appropriate activate command and environment for the current platform."""
    system = platform.system()
    
    env = os.environ.copy()
    activate_cmd = []
    
    if system == "Windows":
        activate_path = Path(".venv", "Scripts", "activate")
        activate_cmd = [str(activate_path)]
        # On Windows, we'll just modify the PATH to use the venv python
        env["PATH"] = str(Path(".venv", "Scripts")) + os.pathsep + env["PATH"]
    else:  # Linux/Mac
        activate_path = Path(".venv", "bin", "activate")
        activate_cmd = ["source", str(activate_path)]
        # On Unix, we'll use the venv python directly
        env["PATH"] = str(Path(".venv", "bin")) + os.pathsep + env["PATH"]
    
    python_path = ".venv/Scripts/python" if system == "Windows" else ".venv/bin/python"
    pip_path = ".venv/Scripts/pip" if system == "Windows" else ".venv/bin/pip"
    
    return activate_cmd, env, python_path, pip_path


def install_dependencies(pip_path):
    """Install all required dependencies."""
    print_status("Installing dependencies...", "step")
    
    # Make sure pip is up to date
    success, _ = run_command([pip_path, "install", "--upgrade", "pip"])
    if not success:
        print_status("Failed to upgrade pip, but continuing...", "warning")
    
    # Install requirements
    req_path = Path("docs", "requirements.txt")
    if req_path.exists():
        success, _ = run_command([pip_path, "install", "-r", str(req_path)])
        if success:
            print_status("Dependencies installed successfully", "success")
            return True
        else:
            print_status("Failed to install some dependencies", "error")
            return False
    else:
        print_status(f"Requirements file not found at {req_path}", "error")
        return False


def install_talib(pip_path):
    """Install TA-Lib, which can be tricky on some platforms."""
    print_status("Checking for TA-Lib installation...", "step")
    
    # First try importing to see if it's already installed
    try:
        import talib
        print_status("TA-Lib is already installed", "success")
        return True
    except ImportError:
        pass
    
    # Try to install using the helper script
    talib_helper = Path("utils", "install_talib.py")
    if talib_helper.exists():
        print_status("Installing TA-Lib using helper script...", "info")
        success, _ = run_command([sys.executable, str(talib_helper)])
        if success:
            print_status("TA-Lib installed successfully", "success")
            return True
    
    # If helper script failed or doesn't exist, try direct pip install
    print_status("Attempting to install TA-Lib via pip...", "info")
    success, _ = run_command([pip_path, "install", "ta-lib"])
    
    if success:
        print_status("TA-Lib installed successfully", "success")
        return True
    else:
        print_status("TA-Lib installation failed. You may need to install it manually.", "warning")
        print_status("See docs/INSTALLATION.md for TA-Lib installation instructions.", "info")
        return False


def create_sample_config():
    """Create a sample configuration file if none exists."""
    print_status("Setting up configuration...", "step")
    
    config_path = Path("config.json")
    if config_path.exists():
        print_status("Configuration file already exists", "info")
        return True
    
    # Create basic config template
    config = {
        "user": {
            "name": "BROski User"
        },
        "api": {
            "exchange": "MEXC",
            "key": "",
            "secret": "",
            "testnet": True
        },
        "trading": {
            "base_currency": "USDT",
            "risk_per_trade": 1.0,
            "max_open_trades": 3,
            "default_strategy": "MACD"
        },
        "strategies": {
            "MACD": {
                "enabled": True,
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9
            },
            "RSI": {
                "enabled": True,
                "period": 14,
                "overbought": 70,
                "oversold": 30
            },
            "HyperFocus": {
                "enabled": True,
                "timeframes": ["15m", "1h", "4h"],
                "correlation_threshold": 0.7
            }
        },
        "ui": {
            "theme": "dark",
            "refresh_interval": 60,
            "notifications_enabled": True
        },
        "feature_flags": {
            "enable_new_ui": True,
            "enable_perf_dashboard": True,
            "enable_strategy_v3": True,
            "enable_data_migration": True,
            "enable_ml_strategies": False
        }
    }
    
    # Write config to file
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print_status("Sample configuration created", "success")
        return True
    except Exception as e:
        print_status(f"Failed to create configuration: {e}", "error")
        return False


def run_system_check(python_path):
    """Run the system compatibility check."""
    print_status("Running system check...", "step")
    
    check_script = Path("utils", "check_system.py")
    if check_script.exists():
        success, output = run_command([python_path, str(check_script), "--compatibility"])
        if success:
            print_status("System check completed successfully", "success")
            return True
        else:
            print_status("System check reported issues", "warning")
            return False
    else:
        print_status("System check script not found", "warning")
        return True  # Continue anyway


def initialize_database(python_path):
    """Initialize/reset the database if needed."""
    print_status("Initializing database...", "step")
    
    db_init_script = Path("utils", "initialize_db.py")
    if db_init_script.exists():
        success, _ = run_command([python_path, str(db_init_script)])
        if success:
            print_status("Database initialized successfully", "success")
            return True
        else:
            print_status("Database initialization failed", "warning")
            return False
    else:
        print_status("Database initialization script not found, skipping", "info")
        return True  # Continue anyway


def create_startup_script():
    """Create a simple startup script based on the OS."""
    print_status("Creating startup script...", "step")
    
    system = platform.system()
    
    if system == "Windows":
        script_path = Path("start_broski.bat")
        script_content = '@echo off\n' \
                         'echo Starting BROski Bot 3.0...\n' \
                         'call .venv\\Scripts\\activate.bat\n' \
                         'python unified_launcher.py\n' \
                         'pause'
    else:  # Linux/Mac
        script_path = Path("start_broski.sh")
        script_content = '#!/bin/bash\n' \
                         'echo "Starting BROski Bot 3.0..."\n' \
                         'source .venv/bin/activate\n' \
                         'python unified_launcher.py'
    
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make the script executable on Unix systems
        if system != "Windows":
            os.chmod(script_path, 0o755)
        
        print_status(f"Startup script created: {script_path}", "success")
        return True
    except Exception as e:
        print_status(f"Failed to create startup script: {e}", "error")
        return False


def print_welcome_banner():
    """Print a welcome banner for BROski Bot."""
    banner = f"""
{BLUE}╔═══════════════════════════════════════════════╗{RESET}
{BLUE}║{RESET}             {BOLD}BROski Bot 3.0 Setup{RESET}             {BLUE}║{RESET}
{BLUE}╚═══════════════════════════════════════════════╝{RESET}

Welcome to the automated setup process for BROski Bot 3.0!
This script will configure everything you need to get started.

{YELLOW}* Virtual environment{RESET}
{YELLOW}* Dependencies installation{RESET}
{YELLOW}* Initial configuration{RESET}
{YELLOW}* System checks{RESET}
{YELLOW}* Startup script creation{RESET}

"""
    print(banner)


def print_completion_message(success, python_path):
    """Print a completion message with next steps."""
    if success:
        message = f"""
{GREEN}╔═══════════════════════════════════════════════╗{RESET}
{GREEN}║{RESET}        {BOLD}BROski Bot 3.0 Setup Complete!{RESET}        {GREEN}║{RESET}
{GREEN}╚═══════════════════════════════════════════════╝{RESET}

{BOLD}Next Steps:{RESET}

1. Review and update your configuration in {BLUE}config.json{RESET}
   - Add your exchange API keys
   - Adjust risk parameters
   - Configure your preferred strategies

2. Start BROski Bot using:
   {YELLOW}Windows:{RESET} start_broski.bat
   {YELLOW}Mac/Linux:{RESET} ./start_broski.sh

3. Check out the documentation:
   {BLUE}docs/GETTING_STARTED.md{RESET} for a quick introduction
   {BLUE}docs/USER_MANUAL.md{RESET} for complete usage details

{YELLOW}For any issues or questions, refer to the troubleshooting guide:{RESET}
{BLUE}docs/TROUBLESHOOTING.md{RESET}

Happy trading with BROski Bot 3.0!
"""
    else:
        message = f"""
{YELLOW}╔═══════════════════════════════════════════════╗{RESET}
{YELLOW}║{RESET}      {BOLD}BROski Bot 3.0 Setup Incomplete{RESET}        {YELLOW}║{RESET}
{YELLOW}╚═══════════════════════════════════════════════╝{RESET}

Some setup steps encountered issues. You may need to:

1. Check the error messages above
2. Refer to {BLUE}docs/TROUBLESHOOTING.md{RESET} for solutions
3. Try manual installation following {BLUE}docs/INSTALLATION.md{RESET}

You can also run individual setup components:

- Install dependencies: {YELLOW}{python_path} -m pip install -r docs/requirements.txt{RESET}
- Run system check: {YELLOW}{python_path} utils/check_system.py{RESET}
- Initialize database: {YELLOW}{python_path} utils/initialize_db.py{RESET}

If you need further assistance, please open an issue on GitHub.
"""
    
    print(message)


def main():
    """Main setup function that orchestrates all steps."""
    print_welcome_banner()
    
    # Get current directory
    project_root = Path.cwd()
    os.chdir(project_root)
    
    # Track overall success
    all_steps_successful = True
    
    # Steps to perform
    if not is_venv():
        venv_created = create_virtual_env()
        all_steps_successful = all_steps_successful and venv_created
        
        if venv_created:
            print_status("Please restart this script from your virtual environment:", "info")
            if platform.system() == "Windows":
                print(f"{YELLOW}.venv\\Scripts\\activate && python easy_setup.py{RESET}")
            else:
                print(f"{YELLOW}source .venv/bin/activate && python easy_setup.py{RESET}")
            return
    else:
        print_status("Running in virtual environment", "success")
    
    # Get activation commands
    _, _, python_path, pip_path = activate_venv()
    
    # Install dependencies
    deps_installed = install_dependencies(pip_path)
    all_steps_successful = all_steps_successful and deps_installed
    
    # Try to install TA-Lib
    talib_installed = install_talib(pip_path)
    # Don't fail the whole setup just because of TA-Lib
    
    # Create sample config
    config_created = create_sample_config()
    all_steps_successful = all_steps_successful and config_created
    
    # Run system check
    system_check_passed = run_system_check(python_path)
    all_steps_successful = all_steps_successful and system_check_passed
    
    # Initialize database
    db_initialized = initialize_database(python_path)
    all_steps_successful = all_steps_successful and db_initialized
    
    # Create startup script
    script_created = create_startup_script()
    all_steps_successful = all_steps_successful and script_created
    
    # Show completion message
    print_completion_message(all_steps_successful, python_path)


if __name__ == "__main__":
    main()
