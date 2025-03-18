#!/usr/bin/env python
"""
Quick test runner for BROski Bot 3.0
Runs a simple trading simulation to verify system functionality
"""
import os
import sys
import json
import time
import colorama
from colorama import Fore, Style
import traceback

# Initialize colorama
colorama.init(autoreset=True)

def run_quick_test():
    """Run a quick test of the trading functionality"""
    print(Fore.CYAN + "=" * 60)
    print(Fore.CYAN + "BROski Bot 3.0 - Quick Test Runner")
    print(Fore.CYAN + "=" * 60)
    
    # 1. Check configuration
    print(Fore.YELLOW + "\nStep 1: Checking configuration...")
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
            print(Fore.GREEN + "✓ Configuration loaded successfully")
            
            # Extract important config values
            exchange_name = config.get('exchange', {}).get('name')
            base_symbol = config.get('trading', {}).get('base_symbol')
            quote_symbol = config.get('trading', {}).get('quote_symbol')
            active_strategy = config.get('strategies', {}).get('active_strategy')
            
            print(Fore.GREEN + f"✓ Using {exchange_name} exchange")
            print(Fore.GREEN + f"✓ Trading pair: {quote_symbol}/{base_symbol}")
            print(Fore.GREEN + f"✓ Active strategy: {active_strategy}")
    except Exception as e:
        print(Fore.RED + f"✗ Error loading configuration: {str(e)}")
        return
    
    # 2. Import required modules
    print(Fore.YELLOW + "\nStep 2: Importing trading modules...")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Try importing key modules
        import ccxt
        print(Fore.GREEN + "✓ CCXT module imported")
        
        # Import our modules depending on what exists
        try:
            from core.broski_engine import BROskiEngine
            engine_class = BROskiEngine
            print(Fore.GREEN + "✓ BROskiEngine class imported")
        except ImportError:
            try:
                from core.start_bot import setup_exchange
                engine_function = setup_exchange
                print(Fore.GREEN + "✓ setup_exchange function imported")
            except ImportError:
                print(Fore.RED + "✗ Could not find trading engine implementation")
                return
    except Exception as e:
        print(Fore.RED + f"✗ Error importing modules: {str(e)}")
        traceback.print_exc()
        return
    
    # 3. Test exchange connection
    print(Fore.YELLOW + "\nStep 3: Testing exchange connection...")
    try:
        exchange_config = config.get('exchange', {})
        exchange = getattr(ccxt, exchange_name.lower())({
            'apiKey': exchange_config.get('api_key', ''),
            'secret': exchange_config.get('api_secret', ''),
            'enableRateLimit': True
        })
        
        print(Fore.GREEN + "✓ Exchange instance created")
        
        # Check if we need sandbox mode
        if exchange_config.get('sandbox_mode', False):
            if hasattr(exchange, 'set_sandbox_mode'):
                exchange.set_sandbox_mode(True)
                print(Fore.GREEN + "✓ Sandbox mode enabled")
            else:
                print(Fore.YELLOW + "⚠ Exchange does not support sandbox mode")
        
        # Test connection by loading markets
        markets = exchange.load_markets()
        print(Fore.GREEN + f"✓ Connected to exchange - {len(markets)} markets available")
        
        # Test specific trading pair
        symbol = f"{quote_symbol}/{base_symbol}"
        if symbol in markets:
            print(Fore.GREEN + f"✓ Trading pair {symbol} is available")
            
            # Get ticker
            ticker = exchange.fetch_ticker(symbol)
            print(Fore.GREEN + f"✓ Current price: {ticker['last']}")
        else:
            print(Fore.RED + f"✗ Trading pair {symbol} not found on {exchange_name}")
            available_pairs = [pair for pair in markets.keys() if base_symbol in pair][:5]
            print(Fore.YELLOW + f"Available pairs with {base_symbol}: {', '.join(available_pairs)}")
            return
    except Exception as e:
        print(Fore.RED + f"✗ Error connecting to exchange: {str(e)}")
        return
    
    # 4. Run a simple price check cycle
    print(Fore.YELLOW + "\nStep 4: Running price monitoring cycle...")
    
    try:
        print(Fore.CYAN + f"\nMonitoring {symbol} for 30 seconds (press Ctrl+C to stop)...")
        start_time = time.time()
        
        # Monitor price for 30 seconds
        while time.time() - start_time < 30:
            try:
                ticker = exchange.fetch_ticker(symbol)
                price = ticker['last']
                bid = ticker.get('bid', 'N/A')
                ask = ticker.get('ask', 'N/A')
                
                print(f"{Fore.CYAN}[{time.strftime('%H:%M:%S')}] "
                      f"{Fore.WHITE}Price: {Fore.GREEN}{price} "
                      f"{Fore.WHITE}Bid: {Fore.YELLOW}{bid} "
                      f"{Fore.WHITE}Ask: {Fore.YELLOW}{ask}")
                
                time.sleep(5)  # Check every 5 seconds
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\nTest stopped by user")
                break
            except Exception as e:
                print(Fore.RED + f"Error fetching price: {str(e)}")
                time.sleep(5)
        
        print(Fore.GREEN + "\n✓ Price monitoring completed")
    except Exception as e:
        print(Fore.RED + f"✗ Error during price monitoring: {str(e)}")
    
    # 5. Final summary
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.GREEN + "Quick test completed!")
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + "Next steps:")
    print(Fore.WHITE + "1. Run the full bot: python unified_launcher.py")
    print(Fore.WHITE + "2. Check strategy implementation for your active strategy")
    print(Fore.WHITE + "3. Run a backtest to validate strategy performance")
    print(Fore.CYAN + "=" * 60)

if __name__ == "__main__":
    run_quick_test()
