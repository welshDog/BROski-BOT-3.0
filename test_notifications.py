#!/usr/bin/env python
"""
BROski Bot 3.0 - Notification Test Utility
Tests different notification channels and formats
"""
import os
import sys
import logging
import time
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

from utils.notification_manager import NotificationManager

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print header"""
    clear_screen()
    print(f"{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}{Style.BRIGHT}                BROski Bot - Notification Test Utility")
    print(f"{Fore.CYAN}{'=' * 70}\n")

def main():
    """Main function to test notifications"""
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print_header()
    print(f"{Fore.WHITE}This utility will test different notification types and channels.")
    
    # Create notification manager
    notifier = NotificationManager()
    
    # Check for configured notification channels
    print(f"\n{Fore.YELLOW}Checking notification channels:")
    
    channels = []
    if notifier.discord_enabled:
        channels.append(f"{Fore.GREEN}✓ Discord (ACTIVE)")
    else:
        channels.append(f"{Fore.RED}✗ Discord (not configured)")
        print(f"{Fore.YELLOW}Discord notifications are recommended! Select option 5 to set up.")

    if notifier.telegram_enabled:
        channels.append(f"{Fore.GREEN}✓ Telegram")
    else:
        channels.append(f"{Fore.WHITE}✗ Telegram (optional)")

    channels.append(f"{Fore.GREEN}✓ Console (always enabled)")
    
    for channel in channels:
        print(channel)
    
    # Menu system
    while True:
        print(f"\n{Fore.YELLOW}Select a test to run:")
        print(f"{Fore.WHITE}1. Test basic notification")
        print(f"{Fore.WHITE}2. Test different notification levels")
        print(f"{Fore.WHITE}3. Test trade notification")
        print(f"{Fore.WHITE}4. Test alert notification")
        print(f"{Fore.WHITE}5. Setup missing notification channels")
        print(f"{Fore.WHITE}0. Exit")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Fore.WHITE}")
        
        if choice == "1":
            print(f"{Fore.YELLOW}Testing basic notification...")
            notifier.send_notification(
                "This is a test of the notification system",
                level="info",
                title="Test Notification"
            )
            print(f"{Fore.GREEN}Test sent! Check your notification channels.")
            
        elif choice == "2":
            print(f"{Fore.YELLOW}Testing different notification levels...")
            
            # Sleep between notifications to avoid rate limits
            notifier.send_notification("This is an info message", level="info", title="Info Test")
            time.sleep(1)
            
            notifier.send_notification("This is a success message", level="success", title="Success Test")
            time.sleep(1)
            
            notifier.send_notification("This is a warning message", level="warning", title="Warning Test")
            time.sleep(1)
            
            notifier.send_notification("This is an error message", level="error", title="Error Test")
            time.sleep(1)
            
            notifier.send_notification("This is a critical message", level="critical", title="Critical Test")
            print(f"{Fore.GREEN}Tests sent! Check your notification channels.")
            
        elif choice == "3":
            print(f"{Fore.YELLOW}Testing trade notification...")
            
            # Test trade notification
            test_trade = {
                "type": "buy",
                "symbol": "BTC/USDT",
                "price": 52000.15,
                "amount": 0.05,
                "cost": 2600.01,
                "fee": 2.60
            }
            notifier.send_trade_notification(test_trade)
            
            time.sleep(1)
            
            test_trade = {
                "type": "sell",
                "symbol": "ETH/USDT",
                "price": 3500.75,
                "amount": 0.25,
                "cost": 875.19,
                "fee": 0.88
            }
            notifier.send_trade_notification(test_trade)
            
            print(f"{Fore.GREEN}Tests sent! Check your notification channels.")
            
        elif choice == "4":
            print(f"{Fore.YELLOW}Testing alert notification...")
            
            # Create a mock alert object
            class MockAlert:
                def __init__(self):
                    self.name = "Price Alert"
                    self.symbol = "BTC/USDT"
                    self.price = 52000.0
                    self.condition = "above"
                    self.enabled = True
                    self.id = "mock-alert-1234"
                    self.created_at = "2023-03-10T12:00:00"
                    self.last_triggered = "2023-03-10T15:30:00"
                    self.trigger_count = 1
            
            alert = MockAlert()
            notifier.send_alert_notification(alert)
            
            print(f"{Fore.GREEN}Test sent! Check your notification channels.")
            
        elif choice == "5":
            print(f"{Fore.YELLOW}Setting up notification channels...")
            
            if not notifier.telegram_enabled:
                setup_telegram = input(f"{Fore.WHITE}Set up Telegram notifications? (y/n): ")
                if setup_telegram.lower() == 'y':
                    subprocess_cmd = [sys.executable, os.path.join(parent_dir, "setup_telegram.py")]
                    os.system(' '.join(subprocess_cmd))
            
            if not notifier.discord_enabled:
                setup_discord = input(f"{Fore.WHITE}Set up Discord notifications? (y/n): ")
                if setup_discord.lower() == 'y':
                    subprocess_cmd = [sys.executable, os.path.join(parent_dir, "setup_discord.py")]
                    os.system(' '.join(subprocess_cmd))
            
            # Reload notification manager after setup
            notifier = NotificationManager()
            print(f"{Fore.GREEN}Notification manager reloaded with new settings.")
            
        elif choice == "0":
            print(f"{Fore.YELLOW}Exiting notification test utility.")
            break
        
        # Wait for user to acknowledge
        input(f"\n{Fore.CYAN}Press Enter to continue...")

if __name__ == "__main__":
    main()
