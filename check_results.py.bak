"""
BROski Bot 3.0 - CheckResults
DESCRIPTION NEEDED
"""
import os
import json
import time

def check_monitoring_results():
    print("Checking monitoring results...")
    
    # Check for signals file
    signals_file = os.path.join('data', 'signals.json')
    if os.path.exists(signals_file):
        with open(signals_file, 'r') as f:
            signals = json.load(f)
        
        print(f"Found signals for {len(signals)} symbols:")
        for symbol, data in signals.items():
            consensus = data.get('consensus', 'UNKNOWN')
            print(f"{symbol}: {consensus}")
    else:
        print("No signals file found yet. Let the bot run longer.")
    
    # Check for log files
    logs_dir = 'logs'
    if os.path.exists(logs_dir):
        log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
        if log_files:
            print(f"\nFound {len(log_files)} log files. Most recent logs:")
            # Sort by modification time, newest first
            log_files.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True)
            
            # Show tail of most recent log
            latest_log = os.path.join(logs_dir, log_files[0])
            with open(latest_log, 'r') as f:
                lines = f.readlines()
                for line in lines[-10:]:  # Last 10 lines
                    print(line.strip())
        else:
            print("No log files found.")

if __name__ == "__main__":
    check_monitoring_results()
