"""
BROski Bot 3.0 - BroskiController
DESCRIPTION NEEDED
"""
import os
import sys
import json
import time
import logging
import threading
import datetime
from pathlib import Path

# Set up paths for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.broski_engine import BROskiEngine
from strategies.strategy_manager import StrategyManager
from utils.notification_service import NotificationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/broski_bot.log')
    ]
)

class BROskiController:
    """Main controller for BROski Trading Bot"""
    
    def __init__(self, config_path=None):
        self.logger = logging.getLogger('BROski.Controller')
        self.logger.info("Initializing BROski Bot Controller...")
        
        # Create logs directory if it doesn't exist
        Path('logs').mkdir(exist_ok=True)
        
        # Initialize core components
        self.engine = BROskiEngine(config_path)
        self.strategy_manager = StrategyManager(self.engine)
        self.notification_service = NotificationService(self.engine.config)
        
        # Trading settings
        self.monitoring_interval = self.engine.config.get('monitoring', {}).get('interval_seconds', 60)
        self.auto_trading = self.engine.config.get('trading', {}).get('auto_trading', False)
        self.trading_thread = None
        self.running = False
        
        self.logger.info("BROski Bot Controller initialized successfully")
    
    def start(self):
        """Start the trading controller"""
        if self.running:
            self.logger.warning("Trading controller is already running")
            return False
            
        self.running = True
        if self.auto_trading:
            self.engine.start_trading()
            message = "BROski Bot started with auto-trading enabled"
        else:
            message = "BROski Bot started in monitoring mode (auto-trading disabled)"
            
        self.logger.info(message)
        self.notification_service.send_notification(message)
        
        # Start the trading loop in a separate thread
        self.trading_thread = threading.Thread(target=self._trading_loop)
        self.trading_thread.daemon = True
        self.trading_thread.start()
        
        return True
    
    def stop(self):
        """Stop the trading controller"""
        if not self.running:
            self.logger.warning("Trading controller is not running")
            return False
            
        self.running = False
        if self.auto_trading:
            self.engine.stop_trading()
            
        message = "BROski Bot stopped"
        self.logger.info(message)
        self.notification_service.send_notification(message)
        
        # Wait for the trading thread to complete
        if self.trading_thread and self.trading_thread.is_alive():
            self.trading_thread.join(timeout=5)
            
        return True
    
    def _trading_loop(self):
        """Main trading loop that monitors markets and executes strategies"""
        self.logger.info("Trading loop started")
        
        while self.running:
            try:
                # Get list of symbols to monitor
                symbols = self.engine.config.get('symbols', ['BTC/USDT', 'ETH/USDT'])
                
                # Scan markets for trading signals
                results = self.strategy_manager.scan_all_markets(symbols)
                
                # Process results and potentially execute trades
                self._process_trading_signals(results)
                
                # Wait for next cycle
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in trading loop: {str(e)}")
                # Sleep a bit before retrying
                time.sleep(10)
    
    def _process_trading_signals(self, market_results):
        """Process trading signals and execute trades if auto-trading is enabled"""
        for symbol, result in market_results.items():
            consensus = result.get('consensus')
            
            self.logger.info(f"{symbol} - Signal: {consensus}")
            
            # If auto trading is enabled and we have a clear signal
            if self.auto_trading and consensus in ["BUY", "SELL"]:
                try:
                    # Get account balance to determine trade amount
                    balance = self.engine.fetch_balance()
                    if not balance:
                        self.logger.warning(f"Could not fetch balance, skipping trade for {symbol}")
                        continue
                    
                    # Get trading parameters for this symbol
                    default_amount_usd = self.engine.config['trading']['default_amount_usd']
                    
                    if consensus == "BUY":
                        # Check if we have enough USDT
                        usdt_balance = balance.get('free', {}).get('USDT', 0)
                        if usdt_balance < default_amount_usd:
                            self.logger.warning(f"Insufficient USDT balance ({usdt_balance}) for trade")
                            continue
                        
                        # Execute buy order
                        self.logger.info(f"Executing BUY order for {symbol}")
                        order = self.engine.execute_trade(symbol, 'buy', default_amount_usd / self._get_current_price(symbol))
                        
                        if order:
                            message = f"✅ BUY order executed for {symbol}: {order['id']}"
                            self.notification_service.send_notification(message)
                    
                    elif consensus == "SELL":
                        # Parse the base currency from symbol (e.g., 'BTC' from 'BTC/USDT')
                        base_currency = symbol.split('/')[0]
                        
                        # Check if we have any of the base currency to sell
                        base_balance = balance.get('free', {}).get(base_currency, 0)
                        if base_balance <= 0:
                            self.logger.warning(f"No {base_currency} balance to sell")
                            continue
                        
                        # Execute sell order
                        self.logger.info(f"Executing SELL order for {symbol}")
                        order = self.engine.execute_trade(symbol, 'sell', base_balance)
                        
                        if order:
                            message = f"✅ SELL order executed for {symbol}: {order['id']}"
                            self.notification_service.send_notification(message)
                            
                except Exception as e:
                    error_msg = f"Error executing trade for {symbol}: {str(e)}"
                    self.logger.error(error_msg)
                    self.notification_service.send_notification(f"⚠️ {error_msg}")
    
    def _get_current_price(self, symbol, exchange_id='mexc'):
        """Get current price for a symbol"""
        try:
            ticker = self.engine.exchanges[exchange_id].fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            self.logger.error(f"Error fetching price for {symbol}: {str(e)}")
            return None
    
    def get_status(self):
        """Get the current status of the bot"""
        engine_status = self.engine.get_status()
        
        return {
            **engine_status,
            'auto_trading': self.auto_trading,
            'monitoring_interval': self.monitoring_interval,
            'bot_running': self.running
        }
    
    def toggle_auto_trading(self, enabled=None):
        """Enable or disable auto-trading"""
        if enabled is None:
            # Toggle the current state
            enabled = not self.auto_trading
            
        self.auto_trading = enabled
        
        if self.auto_trading:
            self.engine.start_trading()
            message = "Auto-trading enabled"
        else:
            self.engine.stop_trading()
            message = "Auto-trading disabled (monitoring only)"
            
        self.logger.info(message)
        self.notification_service.send_notification(message)
        
        return self.auto_trading
    
    def run_backtest(self, strategy_name, symbol, days=30):
        """Run backtest for a specific strategy"""
        self.logger.info(f"Running backtest for {strategy_name} on {symbol} for {days} days")
        
        results = self.strategy_manager.backtest_strategy(strategy_name, symbol, days)
        
        if results:
            message = (
                f"Backtest results for {strategy_name} on {symbol}:\n"
                f"Initial capital: ${results['initial_capital']:.2f}\n"
                f"Final value: ${results['final_value']:.2f}\n"
                f"Profit/loss: ${results['profit_loss']:.2f} ({results['roi_percent']:.2f}%)\n"
                f"Total trades: {results['trades']}\n"
                f"Win rate: {results['win_rate'] * 100:.2f}%"
            )
            
            self.logger.info(message)
            self.notification_service.send_notification(message)
            
        return results
