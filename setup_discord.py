#!/usr/bin/env python
"""
BROski Bot 3.0 - Discord Setup Utility
Sets up Discord webhook notifications for BROski Bot
"""
import os
import sys
import json
import requests
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
    print(f"{Fore.CYAN}{Style.BRIGHT}                BROski Bot - Discord Setup Utility")
    print(f"{Fore.CYAN}{'=' * 70}\n")

def test_discord_webhook(webhook_url):
    """Test Discord webhook by sending a test message"""
    print(f"{Fore.YELLOW}Testing Discord webhook...")
    
    try:
        message = {
            "content": "🤖 BROski Bot test message - If you can see this, your Discord notifications are working!",
            "username": "BROski Bot",
            "embeds": [
                {
                    "title": "Notification System Test",
                    "description": "This is a test of the BROski Bot notification system",
                    "color": 5814783,  # RGB color in decimal (this is a light blue)
                    "fields": [
                        {
                            "name": "Status",
                            "value": "✅ Working correctly"
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(webhook_url, json=message, timeout=10)
        
        if response.status_code in [200, 204]:
            print(f"{Fore.GREEN}✅ Discord connection successful! Check your Discord channel for a test message.")
            return True
        else:
            print(f"{Fore.RED}❌ Discord connection failed. Response: {response.text}")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ Error connecting to Discord: {str(e)}")
        return False

def main():
    """Main function to set up Discord notifications"""
    print_header()
    print(f"{Fore.WHITE}This utility will help you set up Discord notifications for BROski Bot.\n")
    
    # Instructions
    print(f"{Fore.YELLOW}To set up Discord notifications, you need a webhook URL:")
    print(f"{Fore.WHITE}1. Open Discord and go to the server where you want notifications")
    print(f"{Fore.WHITE}2. Edit the channel where notifications should be sent")
    print(f"{Fore.WHITE}3. Select 'Integrations' > 'Webhooks' > 'New Webhook'")
    print(f"{Fore.WHITE}4. Customize name and avatar if desired, then copy the webhook URL\n")
    
    # Get webhook URL
    webhook_url = input(f"{Fore.GREEN}Enter your Discord webhook URL: {Fore.WHITE}")
    
    # Test connection
    success = test_discord_webhook(webhook_url)
    
    if success:
        # Update config file
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        
        try:
            # Read existing config
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Ensure logging section exists
            if 'logging' not in config:
                config['logging'] = {}
            
            # Add Discord config
            config['logging']['discord_webhook'] = webhook_url
            
            # Save config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"\n{Fore.GREEN}✅ Discord configuration saved to config.json")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error saving configuration: {str(e)}")
    
    input(f"\n{Fore.CYAN}Press Enter to continue...")

if __name__ == "__main__":
    main()
