#!/usr/bin/env python
"""
BROski Bot 3.0 - Enhanced Backtest Runner
Runs the enhanced backtest with parameter optimization
"""
import os
import sys
import argparse
from colorama import init, Fore, Style
from utils.enhanced_backtest import EnhancedBacktester

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)


# Initialize colorama
init(autoreset=True)

def main():
    """Main function to run enhanced backtest"""
    parser = argparse.ArgumentParser(description="BROski Bot 3.0 - Enhanced Backtester")
    parser.add_argument("--symbol", type=str, help="Trading symbol (e.g., PI/USDT)")
    parser.add_argument("--days", type=int, default=90, help="Number of days to backtest")
    parser.add_argument("--timeframe", type=str, default="15m", help="Timeframe (e.g., 15m, 1h, 4h)")
    parser.add_argument("--optimize", action="store_true", help="Run parameter optimization")
    parser.add_argument("--no-plots", action="store_true", help="Skip generating plots")
    parser.add_argument("--no-reports", action="store_true", help="Skip generating HTML reports")
    
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}=" * 70)
    print(f"{Fore.CYAN}BROski Bot 3.0 - Enhanced Backtester")
    print(f"{Fore.CYAN}=" * 70)
    
    # Create enhanced backtester
    backtester = EnhancedBacktester()
    
    # Run enhanced validation
    success, results = backtester.run_enhanced_validation(
        save_plots=not args.no_plots,
        save_reports=not args.no_reports,
        optimize=args.optimize
    )
    
    if success:
        print(f"\n{Fore.GREEN}Backtest completed successfully!")
        print(f"{Fore.GREEN}Strategy shows promising results.")
    else:
        print(f"\n{Fore.YELLOW}Backtest completed.")
        print(f"{Fore.YELLOW}Strategy needs improvement before live trading.")

if __name__ == "__main__":
    main()
