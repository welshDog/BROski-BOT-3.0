#!/usr/bin/env python
"""
Emergency Kill Script for BROski Bot
Stops all running bot processes and creates an emergency stop file
"""
import os
import sys
import signal
import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'emergency.log'),
    filemode='a'
)

logger = logging.getLogger(__name__)

def emergency_stop():
    """Execute emergency stop procedure"""
    logger.warning("EMERGENCY STOP ACTIVATED")
    print("\033[91m" + "🚨 EMERGENCY STOP ACTIVATED 🚨" + "\033[0m")
    print("Stopping all BROski Bot processes...")
    
    # Create emergency stop file
    try:
        stop_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'EMERGENCY_STOP')
        with open(stop_file, 'w') as f:
            f.write(f"Emergency stop activated at {datetime.datetime.now()}")
        logger.info(f"Created EMERGENCY_STOP file: {stop_file}")
        print(f"Created emergency stop file: {stop_file}")
    except Exception as e:
        logger.error(f"Failed to create emergency stop file: {str(e)}")
        print(f"Error creating emergency file: {str(e)}")
    
    # Find and kill processes
    try:
        import psutil
        killed = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(cmdline) if cmdline else ''
                
                # Check if this is a BROski Bot process
                if ('broski_bot' in cmdline_str.lower() or 
                    'start_bot.py' in cmdline_str or 
                    'broski_dashboard.py' in cmdline_str or 
                    'hyperfocus' in cmdline_str):
                    
                    if proc.pid != os.getpid():  # Don't kill ourselves
                        print(f"Terminating process {proc.pid}: {cmdline_str[:60]}...")
                        logger.info(f"Terminating process {proc.pid}: {cmdline_str[:60]}")
                        proc.terminate()
                        killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        print(f"Terminated {killed} processes.")
        logger.info(f"Terminated {killed} processes")
        
        if killed == 0:
            print("No active BROski Bot processes found.")
            logger.info("No active BROski Bot processes found")
    
    except ImportError:
        logger.error("psutil module not available, attempting alternative method")
        print("psutil not available, trying alternative method...")
        
        # Fallback to platform-specific commands
        if os.name == 'nt':  # Windows
            os.system('taskkill /f /fi "WINDOWTITLE eq BROski Bot*"')
            os.system('taskkill /f /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq *BROski*"')
        else:  # Linux/Mac
            os.system("pkill -f 'python.*broski'")
    
    print("\033[92m" + "Emergency stop completed!" + "\033[0m")
    logger.info("Emergency stop procedure completed")
    
    print("\nTo restart BROski Bot, you must:")
    print("1. Delete the EMERGENCY_STOP file")
    print("2. Restart the unified launcher")

if __name__ == "__main__":
    emergency_stop()
