#!/usr/bin/env python
"""
BROski Bot 3.0 - Direct Trading System
A simplified trading system that generates reliable trading signals
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
import matplotlib.pyplot as plt
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Try to import ccxt for data access
try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    print(f"{Fore.YELLOW}Warning: CCXT not installed. Will use sample data.")

class DirectTrader:
    """Direct trading system that implements profitable strategies"""
    
    def __init__(self, config_path=None):
        """Initialize the trader"""
        self.logger = logging.getLogger("BROski.DirectTrader")
        
        # Load configuration
        self.config_path = config_path or os.path.join(parent_dir, 'config.json')
        self.config = self._load_config()
        
        # Data cache to avoid re-downloading data
        self.data_cache = {}
        
        # Results of backtests
        self.backtest_results = {}
        
        # Settings
        self.strategy = "moving_average_crossover"  # Default strategy
        self.strategy_params = {
            "fast_period": 10,
            "slow_period": 30,
            "rsi_oversold": 30,
            "rsi_overbought": 70
        }
        
        # Override with config if available
        if 'strategy' in self.config:
            self.strategy = self.config['strategy'].get('name', self.strategy)
            self.strategy_params.update(self.config['strategy'].get('params', {}))
            
        self.logger.info(f"DirectTrader initialized with strategy: {self.strategy}")
        
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
    
    def load_historical_data(self, symbol: str, days: int = 30, timeframe: str = '1h') -> pd.DataFrame:
        """Load historical OHLCV data"""
        # Check if we've already loaded this data
        cache_key = f"{symbol}_{timeframe}_{days}"
        if cache_key in self.data_cache:
            return self.data_cache[cache_key]
        
        # Try to use CCXT to download data if available
        if CCXT_AVAILABLE:
            try:
                # Get exchange configuration
                exchange_id = self.config.get('exchange', {}).get('id', 'binance')
                
                # Initialize exchange
                exchange_class = getattr(ccxt, exchange_id)
                exchange = exchange_class({
                    'enableRateLimit': True
                })
                
                # Calculate start time
                since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
                
                # Fetch OHLCV data
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
                
                # Convert to DataFrame
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                # Cache the data
                self.data_cache[cache_key] = df
                
                print(f"{Fore.GREEN}Loaded {len(df)} candles for {symbol} ({timeframe})")
                return df
                
            except Exception as e:
                self.logger.error(f"Error fetching data via CCXT: {str(e)}")
                print(f"{Fore.RED}Error fetching data via CCXT: {str(e)}")
        
        # Fall back to generating sample data
        print(f"{Fore.YELLOW}Using sample data for {symbol}")
        df = self._generate_sample_data(symbol, days, timeframe)
        
        # Cache the data
        self.data_cache[cache_key] = df
        
        return df
    
    def _generate_sample_data(self, symbol: str, days: int = 30, timeframe: str = '1h') -> pd.DataFrame:
        """Generate sample OHLCV data for testing"""
        # Determine number of candles based on timeframe
        tf_minutes = {'1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60, '4h': 240, '1d': 1440}
        minutes = tf_minutes.get(timeframe, 60)
        candles = int((days * 24 * 60) / minutes)
        
        # Get base price based on symbol
        base_prices = {
            "BTC/USDT": 50000,
            "ETH/USDT": 3000,
            "PI/USDT": 1.35,
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
            
            # Add mean reversion
            if price < base_price * 0.7 or price > base_price * 1.3:
                price = price * 0.95 if price > base_price else price * 1.05
            
            # Generate OHLC with deliberate patterns for signal generation
            daily_volatility = price * np.random.uniform(0.005, 0.03)
            open_price = price * (1 + np.random.normal(0, 0.01))
            close = price
            high = max(open_price, close) + abs(np.random.normal(0, daily_volatility))
            low = min(open_price, close) - abs(np.random.normal(0, daily_volatility))
            
            # Ensure high is highest and low is lowest
            high = max(high, open_price, close)
            low = min(low, open_price, close)
            
            # Generate volume with correlation to price movement
            volume = base_price * 10 * (1 + np.random.normal(0, 0.5)) * (1 + abs(daily_return) * 10)
            
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
        """Calculate technical indicators for trading strategies"""
        # Simple Moving Averages
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # Strategy-specific moving averages
        fast_period = self.strategy_params.get("fast_period", 10)
        slow_period = self.strategy_params.get("slow_period", 30)
        df[f'sma_{fast_period}'] = df['close'].rolling(window=fast_period).mean()
        df[f'sma_{slow_period}'] = df['close'].rolling(window=slow_period).mean()
        
        # Exponential Moving Averages
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['histogram'] = df['macd'] - df['signal']
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).fillna(0)
        loss = -delta.where(delta < 0, 0).fillna(0)
        
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        df['bb_std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
        
        # Price rate of change
        df['roc'] = df['close'].pct_change(periods=10) * 100
        
        # Average true range
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.rolling(window=14).mean()
        
        return df
    
    def _generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on the selected strategy"""
        df['signal'] = 0  # 0 = no signal, 1 = buy, -1 = sell
        
        if self.strategy == "moving_average_crossover":
            fast_period = self.strategy_params.get("fast_period", 10)
            slow_period = self.strategy_params.get("slow_period", 30)
            
            # Crossover signals
            df['signal'] = np.where(
                df[f'sma_{fast_period}'] > df[f'sma_{slow_period}'], 
                1, 
                np.where(df[f'sma_{fast_period}'] < df[f'sma_{slow_period}'], -1, 0)
            )
            
        elif self.strategy == "rsi_strategy":
            oversold = self.strategy_params.get("rsi_oversold", 30)
            overbought = self.strategy_params.get("rsi_overbought", 70)
            
            # RSI signals
            df['signal'] = np.where(
                df['rsi'] < oversold, 
                1,  # Buy when RSI is oversold
                np.where(df['rsi'] > overbought, -1, 0)  # Sell when RSI is overbought
            )
            
        elif self.strategy == "macd_strategy":
            # MACD crossover signals
            df['prev_macd'] = df['macd'].shift(1)
            df['prev_signal'] = df['signal'].shift(1)
            
            # Buy when MACD crosses above signal line
            df['buy_signal'] = (df['macd'] > df['signal']) & (df['prev_macd'] <= df['prev_signal'])
            
            # Sell when MACD crosses below signal line
            df['sell_signal'] = (df['macd'] < df['signal']) & (df['prev_macd'] >= df['prev_signal'])
            
            # Convert to signal column
            df['signal'] = np.where(df['buy_signal'], 1, np.where(df['sell_signal'], -1, 0))
            
        elif self.strategy == "dual_strategy":
            # Combine MA crossover with RSI confirmation
            fast_period = self.strategy_params.get("fast_period", 10)
            slow_period = self.strategy_params.get("slow_period", 30)
            oversold = self.strategy_params.get("rsi_oversold", 30)
            overbought = self.strategy_params.get("rsi_overbought", 70)
            
            # MA crossover
            df['ma_signal'] = np.where(
                df[f'sma_{fast_period}'] > df[f'sma_{slow_period}'], 
                1, 
                np.where(df[f'sma_{fast_period}'] < df[f'sma_{slow_period}'], -1, 0)
            )
            
            # Buy when MA signal is buy AND RSI is not overbought
            df['signal'] = np.where(
                (df['ma_signal'] == 1) & (df['rsi'] < overbought),
                1,
                np.where((df['ma_signal'] == -1) & (df['rsi'] > oversold), -1, 0)
            )
        
        # Generate entry/exit points (not just signal direction)
        df['position'] = df['signal'].replace(0, np.nan).fillna(method='ffill').fillna(0)
        df['position_changed'] = df['position'].diff() != 0
        df['entry_exit'] = np.where(df['position_changed'], df['position'], 0)
        
        return df
    
    def run_backtest(self, symbol: str, days: int = 30, timeframe: str = '1h',
                     initial_capital: float = 10000, commission: float = 0.001):
        """Run a backtest for the selected strategy and symbol"""
        print(f"{Fore.CYAN}Running backtest for {symbol} over {days} days ({timeframe} timeframe)")
        
        # Step 1: Load historical data
        print(f"{Fore.YELLOW}Loading historical data...")
        df = self.load_historical_data(symbol, days, timeframe)
        
        # Step 2: Calculate indicators
        print(f"{Fore.YELLOW}Calculating technical indicators...")
        df = self._calculate_indicators(df)
        
        # Step 3: Generate signals
        print(f"{Fore.YELLOW}Generating trading signals...")
        df = self._generate_signals(df)
        
        # Count signals
        buy_signals = (df['entry_exit'] == 1).sum()
        sell_signals = (df['entry_exit'] == -1).sum() 
        print(f"{Fore.GREEN}Generated {buy_signals} buy signals and {sell_signals} sell signals")
        
        # Initialize backtest state
        account = {
            'cash': initial_capital,
            'position': 0,
            'position_value': 0,
            'equity': initial_capital,
            'trades': [],
            'equity_curve': []
        }
        
        # Step 4: Simulate trading based on signals
        print(f"{Fore.YELLOW}Simulating trades...")
        
        for i in range(len(df)):
            if i < max(50, self.strategy_params.get("slow_period", 30) + 10):
                # Skip initial candles while indicators are calculating
                continue
                
            row = df.iloc[i]
            timestamp = df.index[i]
            
            # Update position value
            if account['position'] > 0:
                account['position_value'] = account['position'] * row['close']
            else:
                account['position_value'] = 0
                
            # Calculate current equity
            account['equity'] = account['cash'] + account['position_value']
            
            # Record equity curve point
            account['equity_curve'].append({
                'timestamp': timestamp,
                'equity': account['equity']
            })
            
            # Check if we have a signal
            if row['entry_exit'] == 1:  # Buy signal
                if account['position'] == 0:  # Only buy if we don't already have a position
                    # Calculate position size (all in)
                    pos_size = account['cash'] * 0.98 / row['close']  # Leave some cash for fees
                    
                    # Apply commission
                    fee = pos_size * row['close'] * commission
                    account['cash'] -= pos_size * row['close'] + fee
                    account['position'] = pos_size
                    
                    # Record trade
                    account['trades'].append({
                        'timestamp': timestamp,
                        'type': 'BUY',
                        'price': row['close'],
                        'size': pos_size,
                        'value': pos_size * row['close'],
                        'fee': fee
                    })
                    
            elif row['entry_exit'] == -1:  # Sell signal
                if account['position'] > 0:  # Only sell if we have a position
                    # Calculate sell value
                    sell_value = account['position'] * row['close']
                    
                    # Apply commission
                    fee = sell_value * commission
                    account['cash'] += sell_value - fee
                    
                    # Record trade
                    account['trades'].append({
                        'timestamp': timestamp,
                        'type': 'SELL',
                        'price': row['close'],
                        'size': account['position'],
                        'value': sell_value,
                        'fee': fee
                    })
                    
                    # Reset position
                    account['position'] = 0
                    account['position_value'] = 0
        
        # Final equity calculation
        if account['position'] > 0:
            account['position_value'] = account['position'] * df.iloc[-1]['close']
        account['equity'] = account['cash'] + account['position_value']
        
        # Calculate backtest results
        results = self._calculate_backtest_results(account, initial_capital, df)
        
        # Store results
        self.backtest_results[symbol] = results
        
        # Print results
        self._print_backtest_results(results)
        
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
    
    def optimize_strategy(self):
        """Find the best parameters for the selected strategy"""
        print(f"{Fore.CYAN}Optimizing strategy parameters...")
        
        # Different parameter sets to test
        if self.strategy == "moving_average_crossover":
            param_sets = [
                {"fast_period": 5, "slow_period": 20},
                {"fast_period": 8, "slow_period": 20},
                {"fast_period": 9, "slow_period": 21},
                {"fast_period": 10, "slow_period": 30},
                {"fast_period": 12, "slow_period": 26},
                {"fast_period": 15, "slow_period": 50},
                {"fast_period": 20, "slow_period": 50}
            ]
        elif self.strategy == "rsi_strategy":
            param_sets = [
                {"rsi_oversold": 20, "rsi_overbought": 80},
                {"rsi_oversold": 25, "rsi_overbought": 75},
                {"rsi_oversold": 30, "rsi_overbought": 70},
                {"rsi_oversold": 35, "rsi_overbought": 65},
                {"rsi_oversold": 40, "rsi_overbought": 60}
            ]
        else:
            print(f"{Fore.RED}Strategy '{self.strategy}' doesn't have predefined parameter sets for optimization")
            return None
            
        print(f"{Fore.GREEN}Testing {len(param_sets)} parameter combinations")
        
        # Run backtest with each parameter set
        results = []
        
        for params in param_sets:
            # Update parameters
            old_params = self.strategy_params.copy()
            self.strategy_params.update(params)
            
            # Run backtest with current parameters
            try:
                print(f"\n{Fore.YELLOW}Testing parameters: {params}")
                backtest_result = self.run_backtest("BTC/USDT", days=30, timeframe="1h")
                
                # Store results
                results.append({
                    "params": params,
                    "return_pct": backtest_result.get('return_pct', 0),
                    "profit_factor": backtest_result.get('profit_factor', 0),
                    "win_rate": backtest_result.get('win_rate', 0),
                    "trades": backtest_result.get('trades', 0),
                    "sharpe_ratio": backtest_result.get('sharpe_ratio', 0)
                })
            except Exception as e:
                print(f"{Fore.RED}Error testing parameters {params}: {str(e)}")
            
            # Restore original parameters
            self.strategy_params = old_params
        
        # Sort results by return percentage
        results.sort(key=lambda x: x["return_pct"], reverse=True)
        
        # Display top results
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.CYAN}{Style.BRIGHT} OPTIMIZATION RESULTS")
        print(f"{Fore.CYAN}{'=' * 60}")
        
        for i, result in enumerate(results[:5]):  # Show top 5
            print(f"\n{Fore.WHITE}Rank {i+1}:")
            print(f"{Fore.CYAN}Parameters: {result['params']}")
            print(f"{Fore.WHITE}Return: {Fore.GREEN if result['return_pct'] > 0 else Fore.RED}{result['return_pct']:.2f}%")
            print(f"{Fore.WHITE}Win Rate: {result['win_rate']:.2f}%")
            print(f"{Fore.WHITE}Profit Factor: {result['profit_factor']:.2f}")
            print(f"{Fore.WHITE}Trades: {result['trades']}")
            print(f"{Fore.WHITE}Sharpe Ratio: {result['sharpe_ratio']:.2f}")
        
        # Return best parameters
        if results:
            best_params = results[0]["params"]
            print(f"\n{Fore.GREEN}Best parameters: {best_params}")
            return best_params
        else:
            print(f"{Fore.RED}No valid results found")
            return None
        
def main():
    """Main function to run direct trader"""
    parser = argparse.ArgumentParser(description='BROski Bot - Direct Trading System')
    
    parser.add_argument('--strategy', type=str, default='moving_average_crossover',
                      choices=['moving_average_crossover', 'rsi_strategy', 'macd_strategy', 'dual_strategy'],
                      help='Trading strategy to use')
    parser.add_argument('--symbol', type=str, default='BTC/USDT',
                      help='Symbol to backtest')
    parser.add_argument('--days', type=int, default=60,
                      help='Number of days to backtest')
    parser.add_argument('--timeframe', type=str, default='1h',
                      choices=['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
                      help='Timeframe for backtesting')
    parser.add_argument('--capital', type=float, default=10000,
                      help='Initial capital for backtesting')
    parser.add_argument('--optimize', action='store_true',
                      help='Optimize strategy parameters')
    parser.add_argument('--plot', action='store_true',
                      help='Plot backtest results')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create trader
    trader = DirectTrader()
    trader.strategy = args.strategy
    
    # Optimize strategy if requested
    if args.optimize:
        best_params = trader.optimize_strategy()
        if best_params:
            trader.strategy_params.update(best_params)
    
    # Run backtest
    trader.run_backtest(args.symbol, args.days, args.timeframe, args.capital)
    
    # Plot results if requested
    if args.plot:
        trader.plot_results(args.symbol)
    
    print(f"\n{Fore.GREEN}Direct trader completed successfully!")

if __name__ == "__main__":
    main()
