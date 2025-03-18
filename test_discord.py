"""
BROski Bot 3.0 - TestDiscord
DESCRIPTION NEEDED
"""
3#!/usr/bin/env python
"""
BROski Bot 3.0 - Discord Notification Tester
Quick utility to test Discord webhook notifications
"""
import os
import sys
import json
import requests
import time
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print header"""
    clear_screen()
    print(f"{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}{Style.BRIGHT}                BROski Bot - Discord Test Utility")
    print(f"{Fore.CYAN}{'=' * 70}\n")

def get_discord_webhook():
    """Get Discord webhook from config"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config.get('logging', {}).get('discord_webhook', '')
    except Exception as e:
        print(f"{Fore.RED}Error reading config: {str(e)}")
    
    return ''

def send_test_message(webhook_url, test_type="basic"):
    """Send a test message to Discord"""
    if not webhook_url:
        print(f"{Fore.RED}No webhook URL provided.")
        return False
    
    try:
        if test_type == "basic":
            message = {
                "username": "BROski Bot",
                "content": "🤖 BROski Bot test message - If you can see this, your Discord notifications are working!"
            }
        elif test_type == "embed":
            message = {
                "username": "BROski Bot",
                "embeds": [
                    {
                        "title": "Discord Notification Test",
                        "description": "This is a test of the BROski Bot notification system",
                        "color": 3447003,  # Blue
                        "fields": [
                            {
                                "name": "Status",
                                "value": "✅ Working correctly"
                            },
                            {
                                "name": "Time",
                                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                        ]
                    }
                ]
            }
        elif test_type == "trade":
            message = {
                "username": "BROski Bot",
                "embeds": [
                    {
                        "title": "BUY SIGNAL",
                        "description": "A buy signal has been detected for BTC/USDT",
                        "color": 3066993,  # Green
                        "fields": [
                            {
                                "name": "Symbol",
                                "value": "BTC/USDT",
                                "inline": True
                            },
                            {
                                "name": "Price",
                                "value": "$52,345.75",
                                "inline": True
                            },
                            {
                                "name": "Signal Strength",
                                "value": "High",
                                "inline": True
                            },
                            {
                                "name": "Strategy",
                                "value": "HyperFocus",
                                "inline": True
                            }
                        ],
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
        elif test_type == "alert":
            message = {
                "username": "BROski Bot",
                "embeds": [
                    {
                        "title": "PRICE ALERT",
                        "description": "BTC/USDT price has crossed above $52,000.00",
                        "color": 16776960,  # Yellow
                        "fields": [
                            {
                                "name": "Symbol",
                                "value": "BTC/USDT",
                                "inline": True
                            },
                            {
                                "name": "Current Price",
                                "value": "$52,345.75",
                                "inline": True
                            },
                            {
                                "name": "Alert Type",
                                "value": "Price Threshold",
                                "inline": True
                            }
                        ],
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
        
        response = requests.post(webhook_url, json=message, timeout=10)
        
        if response.status_code in [200, 204]:
            print(f"{Fore.GREEN}✅ Test message sent successfully!")
            return True
        else:
            print(f"{Fore.RED}❌ Failed to send message. Response: {response.text}")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ Error sending message: {str(e)}")
        return False

def main():
    """Main function"""
    print_header()
    print(f"{Fore.WHITE}This utility tests Discord webhook notifications for BROski Bot.\n")
    
    # Get webhook URL
    webhook_url = get_discord_webhook()
    
    if webhook_url:
        print(f"{Fore.GREEN}Discord webhook found in config!")
    else:
        print(f"{Fore.YELLOW}No Discord webhook found in config.")
        webhook_url = input(f"{Fore.GREEN}Enter Discord webhook URL to test: {Fore.WHITE}")
    
    # Test different notification types
    print(f"\n{Fore.YELLOW}Which type of notification would you like to test?")
    print(f"{Fore.WHITE}1. Basic text message")
    print(f"{Fore.WHITE}2. Formatted embed message")
    print(f"{Fore.WHITE}3. Trade signal (example)")
    print(f"{Fore.WHITE}4. Price alert (example)")
    print(f"{Fore.WHITE}0. Exit")
    
    choice = input(f"\n{Fore.GREEN}Enter choice: {Fore.WHITE}")
    
    if choice == "1":
        send_test_message(webhook_url, "basic")
    elif choice == "2":
        send_test_message(webhook_url, "embed")
    elif choice == "3":
        send_test_message(webhook_url, "trade")
    elif choice == "4":
        send_test_message(webhook_url, "alert")
    elif choice == "0":
        print(f"{Fore.YELLOW}Exiting...")
        return
    
    input(f"\n{Fore.CYAN}Press Enter to continue...")

if __name__ == "__main__":
    main()
