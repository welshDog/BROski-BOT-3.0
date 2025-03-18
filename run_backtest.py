#!/usr/bin/env python
"""
BROski Bot 3.0 - Backtest Runner
Helper script to run backtests with verbose logging
"""
import os
import sys
import logging
import argparse

# Set up logging before imports
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Now import the backtest components
from backtest_signals import SignalBacktester

def main():
    """Run backtest with verbose logging"""
    parser = argparse.ArgumentParser(description='BROski Bot - Verbose Backtest Runner')
    
    parser.add_argument('--symbols', type=str, default='BTC/USDT',
                        help='Comma-separated list of symbols to backtest')
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days to backtest')
    parser.add_argument('--timeframe', type=str, default='1h',
                       choices=['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
                       help='Timeframe for backtesting')
    parser.add_argument('--capital', type=float, default=10000,
                        help='Initial capital for backtesting')
    parser.add_argument('--plot', action='store_true',
                        help='Plot results after backtest')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Parse symbols
    symbols = args.symbols.split(',')
    
    # Create backtester
    backtester = SignalBacktester()
    
    # Run backtest (with verbose output from DEBUG logging)
    for symbol in symbols:
        print(f"Running backtest for {symbol}...")
        backtester.run_backtest(symbol, days=args.days, timeframe=args.timeframe, initial_capital=args.capital)
    
    # Plot if requested
    if args.plot and symbols:
        backtester.plot_results(symbols[0])

if __name__ == "__main__":
    main()
