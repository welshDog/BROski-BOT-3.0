#!/usr/bin/env python
"""
BROski Bot 3.0 - Telegram Setup Utility
Sets up Telegram notifications for BROski Bot
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
    print(f"{Fore.CYAN}{Style.BRIGHT}                BROski Bot - Telegram Setup Utility")
    print(f"{Fore.CYAN}{'=' * 70}\n")

def test_telegram_connection(bot_token, chat_id):
    """Test Telegram connection by sending a test message"""
    print(f"{Fore.YELLOW}Testing Telegram connection...")
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        message = "🤖 BROski Bot test message - If you can see this, your notifications are working!"
        data = {
            "chat_id": chat_id,
            "text": message
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print(f"{Fore.GREEN}✅ Telegram connection successful! Check your Telegram for a test message.")
            return True
        else:
            print(f"{Fore.RED}❌ Telegram connection failed. Response: {response.text}")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ Error connecting to Telegram: {str(e)}")
        return False

def main():
    """Main function to set up Telegram notifications"""
    print_header()
    print(f"{Fore.WHITE}This utility will help you set up Telegram notifications for BROski Bot.\n")
    
    # Instructions
    print(f"{Fore.YELLOW}First, you need to create a Telegram bot and get its token:")
    print(f"{Fore.WHITE}1. Open Telegram and search for @BotFather")
    print(f"{Fore.WHITE}2. Send the command /newbot to BotFather")
    print(f"{Fore.WHITE}3. Follow instructions to create a bot and get a token")
    print(f"{Fore.WHITE}4. Start a conversation with your new bot\n")
    
    # Get bot token
    bot_token = input(f"{Fore.GREEN}Enter your Telegram bot token: {Fore.WHITE}")
    
    print(f"\n{Fore.YELLOW}Now, you need to get your chat ID:")
    print(f"{Fore.WHITE}1. Search for @userinfobot in Telegram")
    print(f"{Fore.WHITE}2. Start chat and send any message")
    print(f"{Fore.WHITE}3. It will reply with your chat ID\n")
    
    # Get chat ID
    chat_id = input(f"{Fore.GREEN}Enter your Telegram chat ID: {Fore.WHITE}")
    
    # Test connection
    success = test_telegram_connection(bot_token, chat_id)
    
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
            
            # Add Telegram config
            config['logging']['telegram_token'] = bot_token
            config['logging']['telegram_chat_id'] = chat_id
            
            # Save config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"\n{Fore.GREEN}✅ Telegram configuration saved to config.json")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error saving configuration: {str(e)}")
    
    input(f"\n{Fore.CYAN}Press Enter to continue...")

if __name__ == "__main__":
    main()
