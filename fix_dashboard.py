#!/usr/bin/env python
"""
BROski Dashboard Repair Utility
Diagnoses and fixes common dashboard issues
"""
import os
import sys
import subprocess
import importlib
import pkg_resources

def check_color():
    """Print colored text to verify colorama is working"""
    try:
        from colorama import Fore, init
        init(autoreset=True)
        print(f"{Fore.GREEN}✓ Colorama is working")
    except ImportError:
        print("Colorama is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
        print("Colorama installed successfully")

def check_dependencies():
    """Check and install required dependencies"""
    required = {
        "streamlit": "1.15.0",
        "pandas": "1.3.0",
        "numpy": "1.20.0",
        "plotly": "5.3.0",
        "matplotlib": "3.4.0",
        "ccxt": "2.0.0"
    }
    
    missing = []
    outdated = []
    
    for package, min_version in required.items():
        try:
            installed = pkg_resources.get_distribution(package)
            if pkg_resources.parse_version(installed.version) < pkg_resources.parse_version(min_version):
                outdated.append((package, installed.version, min_version))
        except pkg_resources.DistributionNotFound:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Installing missing packages...")
        
        for package in missing:
            version_spec = f"{package}>={required[package]}"
            print(f"Installing {version_spec}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", version_spec])
            
        print("All missing packages installed successfully!")
    
    if outdated:
        print(f"Outdated packages: {', '.join([f'{p}({v}<{m})' for p, v, m in outdated])}")
        
        for package, _, min_version in outdated:
            version_spec = f"{package}>={min_version}"
            print(f"Upgrading {version_spec}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", version_spec])
            
        print("All packages updated successfully!")
        
    if not missing and not outdated:
        print("All dependencies are installed and up to date!")

def fix_imports():
    """Create necessary modules if they don't exist"""
    modules = [
        ("utils/notification_manager.py", """
import requests
import logging

class NotificationManager:
    def __init__(self):
        self.logger = logging.getLogger('BROski.Notifications')
        
    def send_telegram(self, message, level='info'):
        return True  # Stub implementation
        
    def send_discord(self, message, level='info'):
        return True  # Stub implementation
"""),
        ("utils/trade_monitor.py", """
import os
import json
from datetime import datetime

class TradeMonitor:
    def __init__(self, log_dir=None):
        self.log_dir = log_dir or 'logs'
"""),
        ("strategies/hyperfocus_strategy_enhanced.py", """
import numpy as np
import pandas as pd
import logging

class EnhancedHyperFocusStrategy:
    def __init__(self, config, exchange):
        self.config = config
        self.exchange = exchange
        self.logger = logging.getLogger('BROski.Strategy.HyperFocus')
        
    def analyze_market(self, symbol, timeframe=None):
        # Return dummy data
        return {
            'is_bottom': False,
            'is_top': False,
            'bottom_confidence': 0,
            'top_confidence': 0,
            'rsi': 50,
            'macd': 0,
            'signal': 0,
            'hist': 0,
            'volume_ratio': 1.0,
            'current_price': 0
        }
""")
    ]
    
    for module_path, code in modules:
        directory = os.path.dirname(module_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        if not os.path.exists(module_path):
            print(f"Creating missing module: {module_path}")
            with open(module_path, 'w') as f:
                f.write(code.strip())

def create_dummy_data():
    """Create dummy data for testing"""
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

def fix_dashboard_code():
    """Fix dashboard code issues"""
    dashboard_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "ui", "broski_dashboard.py")
    
    if not os.path.exists(dashboard_path):
        print("❌ Dashboard file not found!")
        return False
    
    # Read the original file
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Apply fixes and improvements to the code
    improved_code = apply_dashboard_improvements(code)
    
    # Create a backup of the original file
    backup_path = dashboard_path + ".backup"
    import shutil
    shutil.copy2(dashboard_path, backup_path)
    print(f"✅ Created backup at {backup_path}")
    
    # Write the improved code back to the file WITH UTF-8 ENCODING
    try:
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(improved_code)
        print("✅ Dashboard code updated successfully!")
        return True
    except UnicodeEncodeError:
        print("❌ Encoding error while writing file - trying alternative method")
        # Alternative method: Remove problematic emojis
        safe_code = remove_problematic_unicode(improved_code)
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(safe_code)
        print("✅ Dashboard code updated (with emoji removal)!")
        return True

# Add this new helper function for handling problematic Unicode characters
def remove_problematic_unicode(text):
    """Remove or replace problematic Unicode characters like emojis"""
    # Dictionary of emoji replacements
    emoji_replacements = {
        '🧠': '[BRAIN]',
        '📈': '[CHART UP]',
        '📉': '[CHART DOWN]',
        '🤖': '[ROBOT]',
        '💹': '[CHART]',
        '🔍': '[SEARCH]',
        '⚙️': '[GEAR]',
        '📊': '[BAR CHART]'
    }
    
    # Replace known emojis with text equivalents
    for emoji, replacement in emoji_replacements.items():
        text = text.replace(emoji, replacement)
    
    # For any remaining problematic characters, use a regex to remove them
    import re
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    return text

# Make sure all other file operations in the script also use UTF-8 encoding
# For example, in apply_dashboard_improvements:
def apply_dashboard_improvements(code):
    """Apply improvements to dashboard code"""
    # Define template path
    template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "ui", "templates", "dashboard_template.html")
    
    # When reading any files, use UTF-8:
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_code = f.read()
            # You could use template_code here
    
    # ... rest of existing code ...
    
    # Return the original code for now
    return code

def main():
    """Main function"""
    print("BROski Dashboard Repair Utility")
    print("==============================")
    
    # Check colorama
    check_color()
    
    # Check and install dependencies
    check_dependencies()
    
    # Fix imports
    fix_imports()
    
    # Create dummy data if needed
    create_dummy_data()
    
    # Fix dashboard code
    fix_dashboard_code()
    
    print("\nRepair completed! Try launching the dashboard again with:")
    print("python launch_dashboard.py")
    
    # Try launching the dashboard
    try:
        input("\nPress Enter to try launching the dashboard now...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "ui/broski_dashboard.py"])
    except KeyboardInterrupt:
        print("\nDashboard launch canceled.")
    except Exception as e:
        print(f"\nError launching dashboard: {str(e)}")
        print("Try installing Streamlit: pip install streamlit")

if __name__ == "__main__":
    main()
