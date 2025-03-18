"""
BROski Bot 3.0 - SetupDevEnvironment
DESCRIPTION NEEDED
"""
import os
import sys
import subprocess
from colorama import init, Fore

init(autoreset=True)

def setup_dev_environment():
    """Set up the development environment with all required packages"""
    print(Fore.CYAN + "Setting up BROski Bot 3.0 development environment...")
    
    # Install runtime dependencies
    print(Fore.YELLOW + "\nInstalling runtime dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "docs/requirements.txt"])
    
    # Install development dependencies
    print(Fore.YELLOW + "\nInstalling development tools...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "docs/dev_requirements.txt"])
    
    print(Fore.GREEN + "\n✅ Development environment setup complete!")
    print(Fore.CYAN + "You can now run tests with: pytest")

if __name__ == "__main__":
    setup_dev_environment()
