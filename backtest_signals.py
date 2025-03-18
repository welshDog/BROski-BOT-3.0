#!/usr/bin/env python
"""
BROski Bot 3.0 - Alerts to Signals Backtesting Tool
Tests profitability of alert-based trading strategies on historical data
"""
import os
import sys
import json
import logging
import argparse
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
import matplotlib.pyplot as plt
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Import our components
from utils.signal_generator import SignalGenerator
from utils.alerts_manager import AlertsManager
from utils.auto_trader import AutoTrader
from utils.technical_indicators import TechnicalIndicators

# Check if ccxt is available
try:
    import ccxt
    ccxt_available = True
except ImportError:
    ccxt_available = False
    print("CCXT library not available. Some functionality will be limited.")

class SignalBacktester:
    """Backtests trading signals generated from alerts on historical data"""
    
    def __init__(self, config_path=None):
        """Initialize the backtester"""
        self.logger = logging.getLogger("BROski.Backtester")
        
        # Load configuration
        self.config_path = config_path or os.path.join(parent_dir, 'config.json')
        self.config = self._load_config()
        
        # Initialize components
        self.alerts_manager = AlertsManager()
        self.signal_generator = SignalGenerator(self.config_path, self.alerts_manager)
        
        # Auto trader for paper trades simulation
        self.auto_trader = AutoTrader(self.config_path, self.signal_generator)
        
        # Data cache to avoid re-downloading data
        self.data_cache = {}
        
        # Results of backtests
        self.backtest_results = {}
        
        # Settings
        self.default_initial_capital = 10000
        self.default_timeframe = '1h'
        self.default_days = 30

        # Force signal thresholds to be more sensitive for testing
        self.signal_generator.signal_thresholds = {
            'buy': 1,   # Only need 1 signal for a buy (instead of 2)
            'sell': 1,  # Only need 1 signal for a sell (instead of 2)
            'exit': 1   # Keep at 1
        }
        self.logger.info(f"Signal thresholds adjusted for testing: {self.signal_generator.signal_thresholds}")
        
    def _load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return config
            return {}
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return {}
    
    def load_historical_data(self, symbol: str, days: int, timeframe: str) -> pd.DataFrame:
        """Load historical data for backtesting"""
        try:
            # Try to fetch from CCXT if available
            if ccxt_available:
                self.logger.info(f"Fetching data for {symbol} ({timeframe}, {days} days)")
                
                # Get exchange from config instead of hardcoding
                exchange_id = self.config.get('exchange', {}).get('name', 'mexc')  # Default to mexc
                
                # Initialize exchange
                exchange_class = getattr(ccxt, exchange_id)
                
                # Add API credentials if in config
                exchange_config = {'enableRateLimit': True}
                if 'api_key' in self.config.get('exchange', {}) and 'api_secret' in self.config.get('exchange', {}):
                    exchange_config.update({
                        'apiKey': self.config['exchange']['api_key'],
                        'secret': self.config['exchange']['api_secret']
                    })
                
                exchange = exchange_class(exchange_config)
                
                # Calculate since
                since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
                
                # Fetch OHLCV data
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    
                    self.logger.info(f"Fetched {len(df)} candles for {symbol}")
                    return df
                
                except Exception as e:
                    self.logger.error(f"Error fetching data via CCXT: {str(e)}")
                    print(f"Error fetching data via CCXT: {str(e)}")
                    
                    # If we failed to fetch data, generate sample data for testing
                    print(f"Using sample data for {symbol}")
                    return self._generate_sample_data(symbol, days, timeframe)
        
        except Exception as e:
            self.logger.error(f"Error loading historical data: {str(e)}")
        
        # Generate sample data as fallback
        print(f"Generating sample data for {symbol}")
        return self._generate_sample_data(symbol, days, timeframe)
    
    def _generate_sample_data(self, symbol: str, days: int = 30, timeframe: str = '1h') -> pd.DataFrame:
        """Generate sample OHLCV data for testing"""
        from datetime import timedelta
        import numpy as np
        
        # Determine number of candles based on timeframe
        tf_minutes = {'1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60, '4h': 240, '1d': 1440}
        minutes = tf_minutes.get(timeframe, 60)
        candles = int((days * 24 * 60) / minutes)
        
        # Get base price based on symbol
        base_prices = {
            "BTC/USDT": 50000,
            "ETH/USDT": 3000,
            "PI/USDT": 1.35,
            "BNB/USDT": 600,
            "ADA/USDT": 1.20,
            "SOL/USDT": 100
        }
        base_price = base_prices.get(symbol, 100)
        
        # Generate timestamps
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        timestamps = pd.date_range(start=start_date, end=end_date, periods=candles)
        
        # Generate price series with randomness but with a trend
        trend = np.random.choice([-1, 1])  # Random trend direction
        price = base_price
        closes = []
        opens = []
        highs = []
        lows = []
        volumes = []
        
        # Add some cyclical patterns to make it more realistic for trading
        for i in range(candles):
            # Random walk with drift and cyclical components
            cycle1 = np.sin(i/20) * 0.005  # 20-period cycle
            cycle2 = np.sin(i/50) * 0.01   # 50-period cycle
            daily_return = np.random.normal(0.0001 * trend, 0.02) + cycle1 + cycle2
            price = price * (1 + daily_return)
            
            # Generate OHLC
            daily_volatility = price * np.random.uniform(0.005, 0.03)
            open_price = price * (1 + np.random.normal(0, 0.01))
            close = price
            high = max(open_price, close) + abs(np.random.normal(0, daily_volatility))
            low = min(open_price, close) - abs(np.random.normal(0, daily_volatility))
            
            # Ensure high is highest and low is lowest
            high = max(high, open_price, close)
            low = min(low, open_price, close)
            
            # Generate volume with correlation to price movement
            volume = base_price * 100 * (1 + np.random.normal(0, 0.5)) * (1 + abs(daily_return) * 10)
            
            opens.append(open_price)
            closes.append(close)
            highs.append(high)
            lows.append(low)
            volumes.append(volume)
            
            # Change trend occasionally
            if np.random.random() < 0.02:  # 2% chance of trend change
                trend = -trend
        
        # Create DataFrame
        df = pd.DataFrame({
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': volumes
        }, index=timestamps)
        
        return df
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate various technical indicators using pandas-ta"""
        # Use our technical indicators module with default settings
        df = TechnicalIndicators.add_indicators(df, {
            'rsi': {'length': 14},
            'macd': {'fast': 12, 'slow': 26, 'signal': 9},
            'bbands': {'length': 20, 'std': 2}, 
            'sma': {'length': 20},  # Replace standard SMA calculation
            'sma': {'length': 50},  # Add another SMA
            'ema': {'length': 12},  # Add EMA
            'ema': {'length': 26},  # Add another EMA
            'adx': {'length': 14}   # Add ADX for trend strength
        })
        
        # Keep the ATR calculation since it's already well-implemented
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.rolling(window=14).mean()
        
        return df
    
    def _generate_alerts_from_data(self, df: pd.DataFrame, symbol: str) -> List:
        """Generate alerts from historical data for backtesting"""
        # Clear existing alerts from the manager
        self.alerts_manager.clear_alerts()
        
        # Create alert rules based on our signal_rules.json
        signal_rules_path = os.path.join(parent_dir, 'config', 'signal_rules.json')
        try:
            if os.path.exists(signal_rules_path):
                with open(signal_rules_path, 'r') as f:
                    signal_rules = json.load(f)
            else:
                signal_rules = self.signal_generator._default_signal_rules()
        except Exception as e:
            self.logger.error(f"Error loading signal rules: {str(e)}")
            signal_rules = self.signal_generator._default_signal_rules()
        
        # List to store triggered alerts for each candle
        all_triggered_alerts = []
        
        # Simulate each candle
        for i in range(len(df)):
            if i < 50:  # Skip initial candles while indicators are calculating
                continue
                
            candle = df.iloc[i]
            prev_candle = df.iloc[i-1]
            
            # Market data structure
            market_data = {
                "symbol": symbol,
                "price": candle['close'],
                "open": candle['open'],
                "high": candle['high'],
                "low": candle['low'],
                "volume": candle['volume'],
                "timestamp": df.index[i].timestamp(),
                "indicators": {
                    "rsi": candle['rsi'],
                    "macd": candle['macd'],
                    "signal": candle['signal'],
                    "histogram": candle['histogram'],
                    "sma_20": candle['sma_20'],
                    "sma_50": candle['sma_50']
                },
                "price_history": [
                    {"timestamp": df.index[j].timestamp(), "price": df.iloc[j]['close']} 
                    for j in range(max(0, i-24), i+1)
                ],
                "volume_history": [
                    {"timestamp": df.index[j].timestamp(), "volume": df.iloc[j]['volume']} 
                    for j in range(max(0, i-24), i+1)
                ],
                "patterns": {}  # No patterns for now
            }
            
            # Generate alerts based on price movements
            
            # Price alerts on significant levels
            significant_levels = [
                # Round numbers
                round(candle['close'] * 0.9, 0),
                round(candle['close'] * 1.1, 0),
                # Technical levels based on recent price action
                df.iloc[max(0, i-50):i+1]['high'].max(),
                df.iloc[max(0, i-50):i+1]['low'].min(),
                # Moving average crosses
                candle['sma_20'],
                candle['sma_50']
            ]
            
            # Clear old alerts
            self.alerts_manager.clear_alerts()
            
            # Generate price alerts
            for level in significant_levels:
                if prev_candle['close'] < level <= candle['close']:
                    alert_name = f"{symbol} Price Above {level:.2f}"
                    self.alerts_manager.add_alert_from_dict({
                        "type": "PriceAlert",
                        "name": alert_name,
                        "symbol": symbol,
                        "price": level,
                        "condition": "above"
                    })
                elif prev_candle['close'] > level >= candle['close']:
                    alert_name = f"{symbol} Price Below {level:.2f}"
                    self.alerts_manager.add_alert_from_dict({
                        "type": "PriceAlert",
                        "name": alert_name,
                        "symbol": symbol,
                        "price": level,
                        "condition": "below"
                    })
            
            # RSI alerts
            if prev_candle['rsi'] < 30 and candle['rsi'] >= 30:
                self.alerts_manager.add_alert_from_dict({
                    "type": "IndicatorAlert",
                    "name": f"{symbol} RSI Oversold Exit",
                    "symbol": symbol,
                    "indicator": "rsi",
                    "condition": "above",
                    "value": 30
                })
            elif prev_candle['rsi'] > 70 and candle['rsi'] <= 70:
                self.alerts_manager.add_alert_from_dict({
                    "type": "IndicatorAlert",
                    "name": f"{symbol} RSI Overbought Exit",
                    "symbol": symbol,
                    "indicator": "rsi",
                    "condition": "below",
                    "value": 70
                })
            elif prev_candle['rsi'] < 70 and candle['rsi'] >= 70:
                self.alerts_manager.add_alert_from_dict({
                    "type": "IndicatorAlert",
                    "name": f"{symbol} RSI Overbought Entry",
                    "symbol": symbol,
                    "indicator": "rsi",
                    "condition": "above",
                    "value": 70
                })
            elif prev_candle['rsi'] > 30 and candle['rsi'] <= 30:
                self.alerts_manager.add_alert_from_dict({
                    "type": "IndicatorAlert",
                    "name": f"{symbol} RSI Oversold Entry",
                    "symbol": symbol,
                    "indicator": "rsi",
                    "condition": "below",
                    "value": 30
                })
            
            # MACD alerts
            if prev_candle['macd'] < prev_candle['signal'] and candle['macd'] >= candle['signal']:
                self.alerts_manager.add_alert_from_dict({
                    "type": "IndicatorAlert",
                    "name": f"{symbol} MACD Bullish Cross",
                    "symbol": symbol,
                    "indicator": "macd",
                    "condition": "cross_above",
                    "value": candle['signal']
                })
            elif prev_candle['macd'] > prev_candle['signal'] and candle['macd'] <= candle['signal']:
                self.alerts_manager.add_alert_from_dict({
                    "type": "IndicatorAlert",
                    "name": f"{symbol} MACD Bearish Cross",
                    "symbol": symbol,
                    "indicator": "macd",
                    "condition": "cross_below",
                    "value": candle['signal']
                })
            
            # Add volume spike alert if volume is 2x the average
            avg_volume = df.iloc[max(0, i-20):i]['volume'].mean()
            if candle['volume'] > avg_volume * 2:
                self.alerts_manager.add_alert_from_dict({
                    "type": "VolumeAlert",
                    "name": f"{symbol} Volume Spike",
                    "symbol": symbol,
                    "volume_multiple": candle['volume'] / avg_volume,
                    "lookback": 20
                })

            # Generate more frequent test alerts for backtesting
            if i % 5 == 0:  # Every 5 candles
                test_price = candle['close'] * 0.99  # Just below current price
                test_alert_name = f"{symbol} Test Below Alert {i}"
                self.alerts_manager.add_alert_from_dict({
                    "type": "PriceAlert",
                    "name": test_alert_name,
                    "symbol": symbol,
                    "price": test_price,
                    "condition": "below"
                })
                self.logger.info(f"Created test alert: {test_alert_name}, price={test_price}")
                
                # Also add a test 'above' alert
                test_price_above = candle['close'] * 1.01  # Just above current price
                test_alert_name_above = f"{symbol} Test Above Alert {i}"
                self.alerts_manager.add_alert_from_dict({
                    "type": "PriceAlert",
                    "name": test_alert_name_above, 
                    "symbol": symbol,
                    "price": test_price_above,
                    "condition": "above"
                })
                self.logger.info(f"Created test alert: {test_alert_name_above}, price={test_price_above}")
            
            # Now check for triggered alerts
            triggered = self.alerts_manager.check_alerts(market_data)
            if triggered:
                all_triggered_alerts.append({
                    "timestamp": df.index[i],
                    "price": candle['close'],
                    "alerts": triggered
                })
        
        return all_triggered_alerts
    
    def run_backtest(self, symbol: str, days: int = 30, timeframe: str = '1h',
                   initial_capital: float = 10000, commission: float = 0.001):
        """Run a backtest for a symbol over a number of days"""
        print(f"{Fore.CYAN}Running backtest for {symbol} over {days} days ({timeframe} timeframe)")
        
        # Step 1: Load historical data
        print(f"{Fore.YELLOW}Loading historical data...")
        df = self.load_historical_data(symbol, days, timeframe)
        
        # Step 2: Calculate indicators
        print(f"{Fore.YELLOW}Calculating technical indicators...")
        df = self._calculate_indicators(df)
        
        # Step 3: Generate alerts from historical data
        print(f"{Fore.YELLOW}Generating historical alerts...")
        triggered_alerts = self._generate_alerts_from_data(df, symbol)
        print(f"{Fore.GREEN}Generated {len(triggered_alerts)} alert events")
        
        # Initialize backtest state
        account = {
            'cash': initial_capital,
            'position': 0,
            'position_value': 0,
            'equity': initial_capital,
            'trades': [],
            'equity_curve': []
        }
        
        # Step 4: Simulate trading based on signals from alerts
        print(f"{Fore.YELLOW}Simulating trades...")
        
        # Simulate each candle
        for i in range(len(df)):
            if i < 50:  # Skip initial candles while indicators are calculating
                continue
                
            candle = df.iloc[i]
            candle_time = df.index[i]
            
            # Update position value
            if account['position'] > 0:
                account['position_value'] = account['position'] * candle['close']
            else:
                account['position_value'] = 0
                
            # Calculate current equity
            account['equity'] = account['cash'] + account['position_value']
            
            # Record equity curve point
            account['equity_curve'].append({
                'timestamp': candle_time,
                'equity': account['equity']
            })
            
            # Find alerts for current candle
            candle_alerts = []
            for alert_event in triggered_alerts:
                if alert_event['timestamp'] == candle_time:
                    candle_alerts = alert_event['alerts']
                    break
            
            if not candle_alerts:
                continue
            
            # Generate signals from alerts
            market_data = {
                "symbol": symbol,
                "price": candle['close'],
                "open": candle['open'],
                "high": candle['high'],
                "low": candle['low'],
                "volume": candle['volume'],
                "timestamp": candle_time.timestamp(),
                "indicators": {
                    "rsi": candle['rsi'],
                    "macd": candle['macd'],
                    "signal": candle['signal'],
                    "histogram": candle['histogram'],
                    "sma_20": candle['sma_20'],
                    "sma_50": candle['sma_50']
                }
            }
            
            # Set alerts in alerts_manager for signal generation
            self.alerts_manager.clear_alerts()
            for alert in candle_alerts:
                self.alerts_manager.add_alert(alert)
            
            # Generate signals
            signals = self.signal_generator.check_signals(market_data)
            
            # Execute signals
            for signal_symbol, signal in signals.items():
                if signal_symbol != symbol:
                    continue
                    
                # Handle BUY signal
                if signal == "BUY" and account['position'] == 0:
                    # Calculate position size (all in)
                    pos_size = account['cash'] * 0.98 / candle['close']  # Leave some cash for fees
                    
                    # Apply commission
                    fee = pos_size * candle['close'] * commission
                    account['cash'] -= pos_size * candle['close'] + fee
                    account['position'] = pos_size
                    
                    # Record trade
                    account['trades'].append({
                        'timestamp': candle_time,
                        'type': 'BUY',
                        'price': candle['close'],
                        'size': pos_size,
                        'value': pos_size * candle['close'],
                        'fee': fee
                    })
                    
                # Handle SELL signal
                elif (signal == "SELL" or signal == "EXIT") and account['position'] > 0:
                    # Calculate sell value
                    sell_value = account['position'] * candle['close']
                    
                    # Apply commission
                    fee = sell_value * commission
                    account['cash'] += sell_value - fee
                    
                    # Record trade
                    account['trades'].append({
                        'timestamp': candle_time,
                        'type': 'SELL',
                        'price': candle['close'],
                        'size': account['position'],
                        'value': sell_value,
                        'fee': fee
                    })
                    
                    # Reset position
                    account['position'] = 0
                    account['position_value'] = 0
        
        # Final equity calculation for last candle
        final_candle = df.iloc[-1]
        if account['position'] > 0:
            account['position_value'] = account['position'] * final_candle['close']
        else:
            account['position_value'] = 0
            
        account['equity'] = account['cash'] + account['position_value']
        
        # Calculate backtest results
        results = self._calculate_backtest_results(account, initial_capital, df)
        
        # Store results
        self.backtest_results[symbol] = results
        
        # Print results
        self._print_backtest_results(results)
        
        # Return results
        return results
    
    def _calculate_backtest_results(self, account, initial_capital, df):
        """Calculate detailed results from backtest"""
        results = {
            'initial_capital': initial_capital,
            'final_equity': account['equity'],
            'return': account['equity'] - initial_capital,
            'return_pct': (account['equity'] / initial_capital - 1) * 100,
            'trades': len(account['trades']),
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0,
            'total_loss': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'equity_curve': account['equity_curve'],
            'trade_details': account['trades'],
            'max_drawdown': 0,
            'max_drawdown_pct': 0,
            'sharpe_ratio': 0,
            'profit_factor': 0
        }
        
        # Calculate trade stats
        if len(account['trades']) >= 2:
            # Pair buy and sell trades to calculate P&L
            open_position = None
            completed_trades = []
            
            for trade in account['trades']:
                if trade['type'] == 'BUY':
                    open_position = trade
                elif trade['type'] == 'SELL' and open_position:
                    # Calculate P&L
                    buy_value = open_position['value']
                    sell_value = trade['value']
                    pnl = sell_value - buy_value
                    
                    # Account for fees
                    pnl -= open_position['fee'] + trade['fee']
                    
                    # Record completed trade
                    completed_trades.append({
                        'entry': open_position['timestamp'],
                        'exit': trade['timestamp'],
                        'entry_price': open_position['price'],
                        'exit_price': trade['price'],
                        'size': open_position['size'],
                        'pnl': pnl,
                        'pnl_pct': (pnl / buy_value) * 100,
                    })
                    
                    # Reset open position
                    open_position = None
            
            # Calculate stats from completed trades
            if completed_trades:
                results['winning_trades'] = sum(1 for t in completed_trades if t['pnl'] > 0)
                results['losing_trades'] = sum(1 for t in completed_trades if t['pnl'] <= 0)
                
                results['win_rate'] = results['winning_trades'] / len(completed_trades) * 100 if completed_trades else 0
                
                results['total_profit'] = sum(t['pnl'] for t in completed_trades if t['pnl'] > 0)
                results['total_loss'] = sum(abs(t['pnl']) for t in completed_trades if t['pnl'] <= 0)
                
                if results['winning_trades'] > 0:
                    results['avg_win'] = results['total_profit'] / results['winning_trades']
                    results['largest_win'] = max(t['pnl'] for t in completed_trades if t['pnl'] > 0)
                
                if results['losing_trades'] > 0:
                    results['avg_loss'] = results['total_loss'] / results['losing_trades']
                    results['largest_loss'] = max(abs(t['pnl']) for t in completed_trades if t['pnl'] <= 0)
                
                if results['total_loss'] > 0:
                    results['profit_factor'] = results['total_profit'] / results['total_loss']
                    
                results['avg_trade_pnl'] = sum(t['pnl'] for t in completed_trades) / len(completed_trades)
                results['completed_trades'] = completed_trades
        
        # Calculate drawdown
        if account['equity_curve']:
            equity_values = [point['equity'] for point in account['equity_curve']]
            max_equity = initial_capital
            drawdown = 0
            drawdown_pct = 0
            
            for equity in equity_values:
                if equity > max_equity:
                    max_equity = equity
                
                current_drawdown = max_equity - equity
                current_drawdown_pct = (current_drawdown / max_equity) * 100 if max_equity > 0 else 0
                
                drawdown = max(drawdown, current_drawdown)
                drawdown_pct = max(drawdown_pct, current_drawdown_pct)
            
            results['max_drawdown'] = drawdown
            results['max_drawdown_pct'] = drawdown_pct
        
        # Calculate Sharpe ratio if we have enough data
        if len(account['equity_curve']) > 1:
            # Extract daily returns
            equity_series = pd.Series([p['equity'] for p in account['equity_curve']])
            daily_returns = equity_series.pct_change().dropna()
            
            if len(daily_returns) > 0:
                avg_return = daily_returns.mean()
                std_return = daily_returns.std()
                
                if std_return > 0:
                    # Annualized Sharpe ratio assuming 252 trading days
                    results['sharpe_ratio'] = (avg_return / std_return) * (252 ** 0.5)
        
        return results
    
    def _print_backtest_results(self, results):
        """Print detailed backtest results"""
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.CYAN}{Style.BRIGHT} BACKTEST RESULTS")
        print(f"{Fore.CYAN}{'=' * 60}\n")
        
        print(f"{Fore.WHITE}Initial Capital:     {Fore.YELLOW}${results['initial_capital']:.2f}")
        print(f"{Fore.WHITE}Final Equity:        {Fore.YELLOW}${results['final_equity']:.2f}")
        
        if results['return'] >= 0:
            print(f"{Fore.WHITE}Net Profit:          {Fore.GREEN}${results['return']:.2f} ({results['return_pct']:.2f}%)")
        else:
            print(f"{Fore.WHITE}Net Loss:            {Fore.RED}${results['return']:.2f} ({results['return_pct']:.2f}%)")
        
        print(f"{Fore.WHITE}Max Drawdown:        {Fore.RED}${results['max_drawdown']:.2f} ({results['max_drawdown_pct']:.2f}%)")
        print(f"{Fore.WHITE}Sharpe Ratio:        {Fore.YELLOW}{results['sharpe_ratio']:.2f}")
        
        print(f"\n{Fore.WHITE}Total Trades:        {Fore.YELLOW}{results['trades']}")
        
        if results.get('winning_trades', 0) > 0 or results.get('losing_trades', 0) > 0:
            win_rate = results.get('win_rate', 0)
            win_color = Fore.GREEN if win_rate > 50 else (Fore.YELLOW if win_rate >= 40 else Fore.RED)
            print(f"{Fore.WHITE}Win Rate:            {win_color}{win_rate:.2f}%")
            print(f"{Fore.WHITE}Winning Trades:      {Fore.GREEN}{results['winning_trades']}")
            print(f"{Fore.WHITE}Losing Trades:       {Fore.RED}{results['losing_trades']}")
            
            profit_factor = results.get('profit_factor', 0)
            pf_color = Fore.GREEN if profit_factor > 1.5 else (Fore.YELLOW if profit_factor >= 1 else Fore.RED)
            print(f"{Fore.WHITE}Profit Factor:       {pf_color}{profit_factor:.2f}")
            
            if results.get('avg_win', 0) > 0:
                print(f"{Fore.WHITE}Average Win:         {Fore.GREEN}${results['avg_win']:.2f}")
            if results.get('avg_loss', 0) > 0:
                print(f"{Fore.WHITE}Average Loss:        {Fore.RED}${results['avg_loss']:.2f}")
            
            # Calculate risk-reward ratio
            if results.get('avg_loss', 0) > 0:
                risk_reward = results.get('avg_win', 0) / results.get('avg_loss', 0)
                print(f"{Fore.WHITE}Risk-Reward Ratio:   {Fore.YELLOW}{risk_reward:.2f}")

    def plot_results(self, symbol=None):
        """Plot backtest results with Matplotlib"""
        if symbol is None and len(self.backtest_results) > 0:
            symbol = list(self.backtest_results.keys())[0]
        
        if symbol not in self.backtest_results:
            print(f"{Fore.RED}No backtest results found for {symbol}")
            return
        
        results = self.backtest_results[symbol]
        
        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [2, 1]})
        
        # Plot 1: Equity Curve
        if results['equity_curve']:
            timestamps = [point['timestamp'] for point in results['equity_curve']]
            equity = [point['equity'] for point in results['equity_curve']]
            
            ax1.plot(timestamps, equity, 'b-', label='Equity')
            
            # Add buy and sell markers
            for trade in results['trade_details']:
                if trade['type'] == 'BUY':
                    ax1.plot(trade['timestamp'], trade['value'] + trade['fee'], 'g^', markersize=8)
                elif trade['type'] == 'SELL':
                    ax1.plot(trade['timestamp'], trade['value'] - trade['fee'], 'rv', markersize=8)
            
            ax1.set_title(f"{symbol} Backtest Results - Equity Curve")
            ax1.set_xlabel('Time')
            ax1.set_ylabel('Account Value ($)')
            ax1.grid(True)
            ax1.legend()
        
        # Plot 2: Trade P&L Distribution
        if results.get('completed_trades'):
            pnl_values = [trade['pnl'] for trade in results['completed_trades']]
            
            # Create histogram
            ax2.hist(pnl_values, bins=20, color='skyblue', edgecolor='black')
            
            # Add vertical line at zero
            ax2.axvline(x=0, color='r', linestyle='--')
            
            ax2.set_title('Trade P&L Distribution')
            ax2.set_xlabel('Profit/Loss ($)')
            ax2.set_ylabel('Frequency')
            ax2.grid(True)
        
        # Adjust layout and show plot
        plt.tight_layout()
        plt.show()
    
    def save_results_to_csv(self, symbol=None, filename=None):
        """Save backtest results to CSV file"""
        if symbol is None and len(self.backtest_results) > 0:
            symbol = list(self.backtest_results.keys())[0]
        
        if symbol not in self.backtest_results:
            print(f"{Fore.RED}No backtest results found for {symbol}")
            return False
            
        results = self.backtest_results[symbol]
        
        if filename is None:
            # Create filename with symbol and date
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"backtest_{symbol.replace('/', '_')}_{date_str}.csv"
        
        # Save trade details to CSV
        if results.get('completed_trades'):
            try:
                # Convert to DataFrame and save
                trades_df = pd.DataFrame(results['completed_trades'])
                trades_df.to_csv(filename, index=False)
                print(f"{Fore.GREEN}Saved backtest results to {filename}")
                return True
            except Exception as e:
                self.logger.error(f"Error saving results to CSV: {str(e)}")
                print(f"{Fore.RED}Error saving results to CSV: {str(e)}")
        else:
            print(f"{Fore.YELLOW}No completed trades to save for {symbol}")
            
        return False
    
    def run_multi_symbol_backtest(self, symbols, days=30, timeframe='1h', initial_capital=10000):
        """Run backtest on multiple symbols and compare results"""
        all_results = {}
        
        for symbol in symbols:
            print(f"\n{Fore.CYAN}{'=' * 60}")
            print(f"{Fore.CYAN}{Style.BRIGHT} RUNNING BACKTEST FOR {symbol}")
            print(f"{Fore.CYAN}{'=' * 60}")
            
            # Run backtest for this symbol
            results = self.run_backtest(symbol, days, timeframe, initial_capital)
            all_results[symbol] = results
        
        # Compare results
        self._compare_symbol_results(all_results)
        
        return all_results
    
    def _compare_symbol_results(self, results):
        """Compare and display results for multiple symbols"""
        if not results:
            return
            
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.CYAN}{Style.BRIGHT} SYMBOL COMPARISON")
        print(f"{Fore.CYAN}{'=' * 60}\n")
        
        # Prepare summary data
        summary = []
        
        for symbol, result in results.items():
            summary.append({
                'Symbol': symbol,
                'Return %': result.get('return_pct', 0),
                'Win Rate': result.get('win_rate', 0),
                'Trades': result.get('trades', 0),
                'Profit Factor': result.get('profit_factor', 0),
                'Max DD %': result.get('max_drawdown_pct', 0),
                'Sharpe': result.get('sharpe_ratio', 0)
            })
        
        # Convert to DataFrame for easier display
        if summary:
            summary_df = pd.DataFrame(summary)
            
            # Sort by return percentage
            summary_df = summary_df.sort_values('Return %', ascending=False)
            
            # Print formatted summary
            headers = list(summary_df.columns)
            row_format = "{:<10} {:<10} {:<10} {:<8} {:<15} {:<10} {:<10}"
            
            print(row_format.format(*headers))
            print("-" * 75)
            
            for _, row in summary_df.iterrows():
                values = [
                    row['Symbol'],
                    f"{row['Return %']:.2f}%",
                    f"{row['Win Rate']:.2f}%",
                    str(row['Trades']),
                    f"{row['Profit Factor']:.2f}",
                    f"{row['Max DD %']:.2f}%",
                    f"{row['Sharpe']:.2f}"
                ]
                print(row_format.format(*values))

def main():
    """Main function to run backtests from command line"""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='BROski Bot - Alerts to Signals Backtester')
    
    parser.add_argument('--symbols', type=str, default='BTC/USDT',
                        help='Comma-separated list of symbols to backtest')
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days to backtest')
    parser.add_argument('--timeframe', type=str, default='1h', choices=['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
                        help='Timeframe for backtesting')
    parser.add_argument('--capital', type=float, default=10000,
                        help='Initial capital for backtesting')
    parser.add_argument('--commission', type=float, default=0.001,
                        help='Commission rate (0.001 = 0.1%)')
    parser.add_argument('--plot', action='store_true',
                        help='Plot backtest results')
    parser.add_argument('--save', action='store_true',
                        help='Save backtest results to CSV')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create backtester
    backtester = SignalBacktester()
    
    # Parse symbols
    symbols = args.symbols.split(',')
    
    # Run backtest
    if len(symbols) == 1:
        # Single symbol backtest
        results = backtester.run_backtest(symbols[0], args.days, args.timeframe, args.capital, args.commission)
        
        # Plot results if requested
        if args.plot:
            backtester.plot_results(symbols[0])
        
        # Save results if requested
        if args.save:
            backtester.save_results_to_csv(symbols[0])
    else:
        # Multi-symbol backtest
        results = backtester.run_multi_symbol_backtest(symbols, args.days, args.timeframe, args.capital)
        
        # Plot and save for the best performing symbol
        if results:
            # Find best performing symbol by return percentage
            best_symbol = max(results.keys(), key=lambda s: results[s].get('return_pct', 0))
            
            if args.plot:
                backtester.plot_results(best_symbol)
            
            if args.save:
                backtester.save_results_to_csv(best_symbol)
    
    print(f"\n{Fore.GREEN}Backtest completed successfully!")

if __name__ == "__main__":
    main()
    print(f"\n{Fore.GREEN}Backtest completed successfully!")
