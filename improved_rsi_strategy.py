#!/usr/bin/env python
"""
BROski Bot 3.0 - Improved RSI Trading Strategy
An optimized RSI strategy with trend filters and dynamic parameters
"""
import os
import sys
import logging
import argparse
from colorama import init, Fore, Style
import pandas as pd
import numpy as np
import pandas_ta as ta  # Alternative to TA-Lib
from datetime import datetime, timedelta

# Initialize colorama
init(autoreset=True)

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Import components from direct_trader
from direct_trader import DirectTrader

class ImprovedRsiTrader(DirectTrader):
    """Enhanced RSI trading strategy with better filters"""
    
    def __init__(self, config_path=None):
        super().__init__(config_path)
        self.strategy = "improved_rsi"
        
        # Optimized default parameters
        self.strategy_params = {
            "rsi_period": 14,
            "rsi_oversold": 35,  # Higher than traditional 30
            "rsi_overbought": 70,
            "sma_filter_period": 50,
            "volatility_filter": True,
            "stop_loss_pct": 2.0,  # 2% stop loss
            "take_profit_pct": 4.0  # 4% take profit
        }
        
        self.logger.info(f"Improved RSI Trader initialized with params: {self.strategy_params}")
    
    def _generate_signals(self, df):
        """Generate trading signals with improved filters"""
        # Calculate RSI using pandas-ta instead of manual calculation
        rsi_period = self.strategy_params.get("rsi_period", 14)
        df['rsi'] = ta.rsi(df['close'], length=rsi_period)
        
        # Calculate trend filter
        filter_period = self.strategy_params.get("sma_filter_period", 50)
        df['sma_filter'] = ta.sma(df['close'], length=filter_period)
        df['is_uptrend'] = df['close'] > df['sma_filter']
        
        # Volatility filter using ATR
        if self.strategy_params.get("volatility_filter", True):
            df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
            
            # Volatility as percentage of price
            df['volatility_pct'] = (df['atr'] / df['close']) * 100
            
            # Only trade when volatility is reasonable (not extreme)
            df['good_volatility'] = (df['volatility_pct'] > 0.5) & (df['volatility_pct'] < 3.0)
        else:
            df['good_volatility'] = True
        
        # Define oversold/overbought levels
        oversold = self.strategy_params.get("rsi_oversold", 35)
        overbought = self.strategy_params.get("rsi_overbought", 70)
        
        # Initial signals
        # BUY: RSI oversold + uptrend + good volatility
        # SELL: RSI overbought (regardless of other conditions)
        df['signal'] = 0
        df.loc[(df['rsi'] < oversold) & df['is_uptrend'] & df['good_volatility'], 'signal'] = 1  
        df.loc[df['rsi'] > overbought, 'signal'] = -1
        
        # Generate entry/exit points (not just signal direction)
        df['position'] = df['signal'].replace(0, np.nan).fillna(method='ffill').fillna(0)
        df['position_changed'] = df['position'].diff() != 0
        df['entry_exit'] = np.where(df['position_changed'], df['position'], 0)
        
        return df
        
    def run_backtest(self, symbol, days=90, timeframe='1h', initial_capital=10000, commission=0.001):
        """Run backtest with stop loss and take profit logic"""
        print(f"{Fore.CYAN}Running improved RSI backtest for {symbol}")
        
        # Get standard data and indicators
        df = self.load_historical_data(symbol, days, timeframe)
        df = self._calculate_indicators(df)
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
        
        # Get stop loss and take profit percentages
        stop_loss_pct = self.strategy_params.get("stop_loss_pct", 2.0) / 100
        take_profit_pct = self.strategy_params.get("take_profit_pct", 4.0) / 100
        
        # For tracking open trades with stops/targets
        current_trade = None
        
        # Simulate trading
        for i in range(len(df)):
            if i < 50:  # Skip initial candles for indicator calculation
                continue
                
            row = df.iloc[i]
            timestamp = df.index[i]
            
            # Update position value
            if account['position'] > 0:
                account['position_value'] = account['position'] * row['close']
            else:
                account['position_value'] = 0
                
            # Calculate equity
            account['equity'] = account['cash'] + account['position_value']
            account['equity_curve'].append({
                'timestamp': timestamp,
                'equity': account['equity']
            })
            
            # Check stop loss / take profit if we have an open position
            if current_trade is not None and account['position'] > 0:
                entry_price = current_trade['price']
                current_price = row['close']
                
                # Check stop loss
                stop_price = entry_price * (1 - stop_loss_pct)
                if current_price <= stop_price:
                    print(f"{Fore.RED}Stop loss triggered at {current_price:.2f}")
                    
                    # Calculate sell value
                    sell_value = account['position'] * current_price
                    fee = sell_value * commission
                    account['cash'] += sell_value - fee
                    
                    # Record trade
                    account['trades'].append({
                        'timestamp': timestamp,
                        'type': 'SELL-STOP',
                        'price': current_price,
                        'size': account['position'],
                        'value': sell_value,
                        'fee': fee
                    })
                    
                    # Reset position
                    account['position'] = 0
                    account['position_value'] = 0
                    current_trade = None
                    continue
                
                # Check take profit
                target_price = entry_price * (1 + take_profit_pct)
                if current_price >= target_price:
                    print(f"{Fore.GREEN}Take profit triggered at {current_price:.2f}")
                    
                    # Calculate sell value
                    sell_value = account['position'] * current_price
                    fee = sell_value * commission
                    account['cash'] += sell_value - fee
                    
                    # Record trade
                    account['trades'].append({
                        'timestamp': timestamp,
                        'type': 'SELL-TP',
                        'price': current_price,
                        'size': account['position'],
                        'value': sell_value,
                        'fee': fee
                    })
                    
                    # Reset position
                    account['position'] = 0
                    account['position_value'] = 0
                    current_trade = None
                    continue
            
            # Check for regular entry/exit signals
            if row['entry_exit'] == 1 and account['position'] == 0:  # Buy signal
                # Position sizing - use 90% of available cash
                position_size = (account['cash'] * 0.9) / row['close']
                fee = position_size * row['close'] * commission
                
                # Update account
                account['cash'] -= position_size * row['close'] + fee
                account['position'] = position_size
                
                # Record trade
                trade = {
                    'timestamp': timestamp,
                    'type': 'BUY',
                    'price': row['close'],
                    'size': position_size,
                    'value': position_size * row['close'],
                    'fee': fee
                }
                account['trades'].append(trade)
                current_trade = trade
                
            elif row['entry_exit'] == -1 and account['position'] > 0:  # Sell signal
                # Calculate sell value
                sell_value = account['position'] * row['close']
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
                current_trade = None
        
        # Final equity calculation
        if account['position'] > 0:
            account['position_value'] = account['position'] * df.iloc[-1]['close']
        account['equity'] = account['cash'] + account['position_value']
        
        # Calculate results
        results = self._calculate_backtest_results(account, initial_capital, df)
        
        # Store and print results
        self.backtest_results[symbol] = results
        self._print_backtest_results(results)
        
        return results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='BROski Bot - Improved RSI Trading Strategy')
    
    parser.add_argument('--symbol', type=str, default='BTC/USDT',
                      help='Symbol to backtest')
    parser.add_argument('--days', type=int, default=90,
                      help='Number of days to backtest')
    parser.add_argument('--timeframe', type=str, default='1h',
                      choices=['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
                      help='Timeframe for backtesting')
    parser.add_argument('--capital', type=float, default=10000,
                      help='Initial capital for backtesting')
    parser.add_argument('--plot', action='store_true',
                      help='Plot backtest results')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create and run improved trader
    trader = ImprovedRsiTrader()
    trader.run_backtest(args.symbol, args.days, args.timeframe, args.capital)
    
    # Plot if requested
    if args.plot:
        trader.plot_results(args.symbol)
    
    print(f"\n{Fore.GREEN}Improved RSI strategy backtest completed!")

if __name__ == "__main__":
    main()
