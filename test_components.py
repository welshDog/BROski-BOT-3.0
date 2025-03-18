#!/usr/bin/env python
"""
BROski Bot 3.0 - Component Testing Utility
Run quick tests on various bot components
"""
import os
import sys
import json
import time
import argparse
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

def print_header(title):
    """Print formatted header"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}{title}")
    print(f"{Fore.CYAN}{'=' * 70}")

def load_config():
    """Load configuration file"""
    try:
        with open(os.path.join(parent_dir, 'config.json'), 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error loading config: {str(e)}")
        return None

def test_exchange_connection():
    """Test connection to the exchange API"""
    print_header("Testing Exchange Connection")
    
    try:
        import ccxt
        config = load_config()
        
        if not config:
            return False
            
        exchange_name = config.get('exchange', {}).get('name', '').lower()
        api_key = config.get('exchange', {}).get('api_key', '')
        api_secret = config.get('exchange', {}).get('api_secret', '')
        
        print(f"{Fore.YELLOW}Connecting to {exchange_name}...")
        
        exchange = getattr(ccxt, exchange_name)({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True
        })
        
        # Test public API
        print(f"{Fore.YELLOW}Testing public API...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"{Fore.GREEN}✓ Public API working - BTC/USDT price: ${ticker['last']}")
        
        # Test private API
        print(f"{Fore.YELLOW}Testing private API...")
        balance = exchange.fetch_balance()
        print(f"{Fore.GREEN}✓ Private API working - Account connected")
        
        # Test symbol availability
        symbols = config.get('symbols', [])
        if symbols:
            print(f"{Fore.YELLOW}Testing configured symbols...")
            for symbol in symbols:
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    print(f"{Fore.GREEN}✓ {symbol} is valid - Current price: ${ticker['last']}")
                except Exception as e:
                    print(f"{Fore.RED}✗ {symbol} ERROR: {str(e)}")
        
        return True
                
    except ImportError:
        print(f"{Fore.RED}✗ CCXT library not installed. Run: pip install ccxt")
        return False
    except Exception as e:
        print(f"{Fore.RED}✗ Connection failed: {str(e)}")
        return False

def test_strategy_signals():
    """Test strategy signal generation"""
    print_header("Testing Strategy Signal Generation")
    
    try:
        from strategies.hyperfocus_strategy_enhanced import EnhancedHyperFocusStrategy
        import ccxt
        import pandas as pd
        
        config = load_config()
        if not config:
            return False
            
        exchange_name = config.get('exchange', {}).get('name', '').lower()
        try:
            exchange = getattr(ccxt, exchange_name)({'enableRateLimit': True})
        except:
            print(f"{Fore.RED}✗ Could not initialize exchange. Using dummy data instead.")
            return False
            
        strategy = EnhancedHyperFocusStrategy(config, exchange)
        
        # Test with primary trading pair
        symbols = config.get('symbols', ['BTC/USDT'])
        timeframe = config['strategies']['hyperfocus_strategy']['timeframe']
        
        print(f"{Fore.YELLOW}Generating signals for {symbols[0]} on {timeframe} timeframe...")
        result = strategy.analyze_market(symbols[0])
        
        if result:
            print(f"{Fore.GREEN}✓ Signal generation successful")
            print(f"  Current price: ${result['current_price']}")
            print(f"  Bottom detected: {result['is_bottom']} (Confidence: {result['bottom_confidence']:.1f}%)")
            print(f"  Top detected: {result['is_top']} (Confidence: {result['top_confidence']:.1f}%)")
            print(f"  RSI: {result['rsi']:.2f}")
            return True
        else:
            print(f"{Fore.RED}✗ Signal generation failed")
            return False
            
    except ImportError:
        print(f"{Fore.RED}✗ Required libraries not installed")
        return False
    except Exception as e:
        print(f"{Fore.RED}✗ Error testing strategy: {str(e)}")
        return False

def test_notifications():
    """Test notification systems"""
    print_header("Testing Notification Systems")
    
    try:
        from utils.notification_manager import NotificationManager
        
        notifier = NotificationManager()
        
        # Test Telegram
        print(f"{Fore.YELLOW}Testing Telegram notifications...")
        telegram_result = notifier.send_telegram("This is a test notification from BROski Bot", "info")
        
        if telegram_result:
            print(f"{Fore.GREEN}✓ Telegram notification sent successfully")
        else:
            print(f"{Fore.RED}✗ Telegram notification failed")
        
        # Test Discord
        print(f"{Fore.YELLOW}Testing Discord notifications...")
        discord_result = notifier.send_discord("This is a test notification from BROski Bot", "info")
        
        if discord_result:
            print(f"{Fore.GREEN}✓ Discord notification sent successfully")
        else:
            print(f"{Fore.RED}✗ Discord notification failed")
            
        return telegram_result or discord_result
        
    except ImportError:
        print(f"{Fore.RED}✗ Notification manager not available")
        return False
    except Exception as e:
        print(f"{Fore.RED}✗ Error testing notifications: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="BROski Bot 3.0 Component Testing")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--exchange", action="store_true", help="Test exchange connection")
    parser.add_argument("--strategy", action="store_true", help="Test strategy signal generation")
    parser.add_argument("--notify", action="store_true", help="Test notification systems")
    
    args = parser.parse_args()
    
    if not any([args.all, args.exchange, args.strategy, args.notify]):
        parser.print_help()
        return
    
    results = {}
    
    if args.all or args.exchange:
        results['exchange'] = test_exchange_connection()
    
    if args.all or args.strategy:
        results['strategy'] = test_strategy_signals()
    
    if args.all or args.notify:
        results['notifications'] = test_notifications()
    
    # Print summary
    print_header("Test Results Summary")
    
    for component, result in results.items():
        status = f"{Fore.GREEN}PASSED" if result else f"{Fore.RED}FAILED"
        print(f"{component.capitalize()}: {status}")

if __name__ == "__main__":
    main()
