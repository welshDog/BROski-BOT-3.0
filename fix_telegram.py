#!/usr/bin/env python
"""
BROski Bot 3.0 - Telegram Configuration Fix Utility
Helps diagnose and fix common Telegram notification issues
"""
import os
import sys
import json
import requests
import time
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
    print(f"{Fore.CYAN}{Style.BRIGHT}          BROski Bot - Telegram Configuration Fix Utility")
    print(f"{Fore.CYAN}{'=' * 70}\n")

def get_current_config():
    """Get current Telegram configuration from config file"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    
    if not os.path.exists(config_path):
        return None, None
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        telegram_token = config.get('logging', {}).get('telegram_token', '')
        telegram_chat_id = config.get('logging', {}).get('telegram_chat_id', '')
        
        return telegram_token, telegram_chat_id
    except Exception as e:
        print(f"{Fore.RED}Error loading config: {str(e)}")
        return None, None

def verify_bot_token(token):
    """Verify that the bot token is valid"""
    if not token:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            bot_name = data.get('result', {}).get('username', 'Unknown')
            print(f"{Fore.GREEN}✓ Bot token is valid! Bot username: @{bot_name}")
            return True
        else:
            print(f"{Fore.RED}✗ Bot token is invalid: {data.get('description', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"{Fore.RED}✗ Error connecting to Telegram API: {str(e)}")
        return False

def get_bot_updates(token):
    """Get the most recent updates received by the bot to find valid chat IDs"""
    if not token:
        return []
    
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            return data.get('result', [])
        else:
            print(f"{Fore.RED}✗ Could not get bot updates: {data.get('description', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"{Fore.RED}✗ Error getting bot updates: {str(e)}")
        return []

def extract_chat_ids(updates):
    """Extract chat IDs from updates"""
    chat_ids = []
    
    for update in updates:
        # Extract from message or edited_message
        message = update.get('message', update.get('edited_message', {}))
        chat = message.get('chat', {})
        
        if chat:
            chat_id = chat.get('id')
            chat_type = chat.get('type', 'unknown')
            chat_title = chat.get('title', '')
            chat_username = chat.get('username', '')
            
            if chat_id:
                chat_info = {
                    'id': chat_id,
                    'type': chat_type,
                    'title': chat_title if chat_type == 'group' else '',
                    'username': chat_username if chat_type == 'private' else '',
                    'last_update': message.get('date', 0)
                }
                
                # Only add if not already in list
                if not any(c['id'] == chat_id for c in chat_ids):
                    chat_ids.append(chat_info)
    
    # Sort by most recent update
    chat_ids.sort(key=lambda x: x['last_update'], reverse=True)
    return chat_ids

def test_chat_id(token, chat_id):
    """Test sending a message to the provided chat ID"""
    if not token or not chat_id:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": f"🔧 BROski Bot configuration test message - {time.strftime('%H:%M:%S')}"
        }
        
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            print(f"{Fore.GREEN}✓ Test message sent successfully to chat ID: {chat_id}")
            return True
        else:
            print(f"{Fore.RED}✗ Failed to send test message: {result.get('description', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"{Fore.RED}✗ Error sending test message: {str(e)}")
        return False

def update_config(token, chat_id):
    """Update the configuration file with new Telegram settings"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        if 'logging' not in config:
            config['logging'] = {}
        
        config['logging']['telegram_token'] = token
        config['logging']['telegram_chat_id'] = chat_id
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"{Fore.GREEN}✓ Configuration updated successfully!")
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ Error updating configuration: {str(e)}")
        return False

def main():
    """Main function"""
    print_header()
    print(f"{Fore.WHITE}This utility will help resolve issues with Telegram notifications.\n")
    
    # Get current configuration
    current_token, current_chat_id = get_current_config()
    
    if current_token:
        print(f"{Fore.YELLOW}Current Telegram configuration:")
        print(f"{Fore.WHITE}Bot Token: {current_token[:5]}...{current_token[-5:]}")
        print(f"{Fore.WHITE}Chat ID: {current_chat_id}")
    else:
        print(f"{Fore.YELLOW}No existing Telegram configuration found.")
        current_token = ""
        current_chat_id = ""
    
    # Step 1: Verify or update bot token
    print(f"\n{Fore.CYAN}Step 1: Verify Bot Token")
    
    if current_token:
        is_valid = verify_bot_token(current_token)
        if not is_valid:
            print(f"\n{Fore.YELLOW}Current token is invalid. Do you want to enter a new token? (y/n)")
            if input(f"{Fore.WHITE}> ").lower() == 'y':
                token = input(f"{Fore.GREEN}Enter new Telegram bot token: {Fore.WHITE}")
                verify_bot_token(token)
            else:
                token = current_token
        else:
            token = current_token
    else:
        token = input(f"{Fore.GREEN}Enter your Telegram bot token: {Fore.WHITE}")
        verify_bot_token(token)
    
    # Step 2: Verify or update chat ID
    print(f"\n{Fore.CYAN}Step 2: Verify Chat ID")
    
    # Check if current chat ID works
    if current_chat_id:
        print(f"{Fore.YELLOW}Testing current chat ID: {current_chat_id}")
        works = test_chat_id(token, current_chat_id)
        
        if works:
            chat_id = current_chat_id
        else:
            print(f"{Fore.YELLOW}Current chat ID doesn't work. Looking for alternatives...")
            
            # Get recent updates to find valid chat IDs
            updates = get_bot_updates(token)
            chat_ids = extract_chat_ids(updates)
            
            if chat_ids:
                print(f"\n{Fore.YELLOW}Found {len(chat_ids)} potential chat IDs from bot history:")
                
                for idx, chat_info in enumerate(chat_ids):
                    chat_id_value = chat_info['id']
                    if chat_info['type'] == 'private':
                        display = f"Private chat with @{chat_info['username']}"
                    else:
                        display = f"Group '{chat_info['title']}'"
                    
                    print(f"{Fore.WHITE}{idx + 1}. {chat_id_value} - {display}")
                
                print(f"\n{Fore.YELLOW}Enter number to select chat ID or 0 to manually enter:")
                choice = input(f"{Fore.WHITE}> ")
                
                try:
                    choice = int(choice)
                    if 1 <= choice <= len(chat_ids):
                        chat_id = chat_ids[choice - 1]['id']
                    else:
                        chat_id = input(f"{Fore.GREEN}Enter chat ID manually: {Fore.WHITE}")
                except ValueError:
                    chat_id = input(f"{Fore.GREEN}Enter chat ID manually: {Fore.WHITE}")
            else:
                print(f"{Fore.RED}No chat history found with this bot.")
                print(f"{Fore.YELLOW}Try sending a message to your bot first, then run this utility again.")
                print(f"{Fore.YELLOW}Or enter a chat ID manually:")
                chat_id = input(f"{Fore.GREEN}Enter chat ID: {Fore.WHITE}")
    else:
        # Get recent updates to find valid chat IDs
        print(f"{Fore.YELLOW}Looking for valid chat IDs from your bot history...")
        updates = get_bot_updates(token)
        chat_ids = extract_chat_ids(updates)
        
        if chat_ids:
            print(f"\n{Fore.YELLOW}Found {len(chat_ids)} potential chat IDs:")
            
            for idx, chat_info in enumerate(chat_ids):
                chat_id_value = chat_info['id']
                if chat_info['type'] == 'private':
                    display = f"Private chat with @{chat_info['username']}"
                else:
                    display = f"Group '{chat_info['title']}'"
                
                print(f"{Fore.WHITE}{idx + 1}. {chat_id_value} - {display}")
            
            print(f"\n{Fore.YELLOW}Enter number to select chat ID or 0 to manually enter:")
            choice = input(f"{Fore.WHITE}> ")
            
            try:
                choice = int(choice)
                if 1 <= choice <= len(chat_ids):
                    chat_id = chat_ids[choice - 1]['id']
                else:
                    chat_id = input(f"{Fore.GREEN}Enter chat ID manually: {Fore.WHITE}")
            except ValueError:
                chat_id = input(f"{Fore.GREEN}Enter chat ID manually: {Fore.WHITE}")
        else:
            print(f"{Fore.RED}No chat history found with this bot.")
            print(f"{Fore.YELLOW}You need to send at least one message to your bot first.")
            print(f"{Fore.YELLOW}Please send a message to your bot, then enter your chat ID:")
            chat_id = input(f"{Fore.GREEN}Enter chat ID: {Fore.WHITE}")
    
    # Step 3: Test the chat ID
    print(f"\n{Fore.CYAN}Step 3: Testing Telegram Configuration")
    test_successful = test_chat_id(token, chat_id)
    
    if test_successful:
        print(f"\n{Fore.YELLOW}Do you want to update your configuration with these settings? (y/n)")
        if input(f"{Fore.WHITE}> ").lower() == 'y':
            update_config(token, chat_id)
        else:
            print(f"{Fore.YELLOW}Configuration not updated.")
    else:
        print(f"\n{Fore.RED}Telegram configuration test failed.")
        print(f"{Fore.YELLOW}Please ensure:")
        print(f"{Fore.WHITE}1. Your bot token is valid")
        print(f"{Fore.WHITE}2. You have sent at least one message to your bot")
        print(f"{Fore.WHITE}3. You are using the correct chat ID")
    
    input(f"\n{Fore.CYAN}Press Enter to continue...")

if __name__ == "__main__":
    main()
