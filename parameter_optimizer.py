#!/usr/bin/env python
"""
BROski Bot 3.0 - Strategy Parameter Optimizer
Uses grid search to find optimal trading parameters based on backtesting
"""
import os
import sys
import json
import logging
import argparse
import itertools
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any
import multiprocessing
from colorama import init, Fore, Style
import matplotlib.pyplot as plt

# Initialize colorama
init(autoreset=True)

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Import the backtester
from backtest_signals import SignalBacktester

class StrategyOptimizer:
    """Optimizes strategy parameters using grid search"""
    
    def __init__(self, config_path=None):
        """Initialize the optimizer"""
        self.logger = logging.getLogger("BROski.Optimizer")
        
        # Load configuration
        self.config_path = config_path or os.path.join(parent_dir, 'config.json')
        self.config = self._load_config()
        
        # Results storage
        self.results = []
        
        # Output directory
        self.output_dir = os.path.join(parent_dir, 'optimization_results')
        os.makedirs(self.output_dir, exist_ok=True)
    
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
    
    def get_parameter_grid(self, strategy_name: str) -> Dict[str, List[Any]]:
        """Get parameter grid for a specific strategy"""
        # Define default parameter grids for different strategies
        if strategy_name == "rsi_strategy":
            return {
                "rsi_period": [7, 14, 21],
                "overbought": [65, 70, 75, 80],
                "oversold": [20, 25, 30, 35]
            }
        elif strategy_name == "macd_strategy":
            return {
                "fast": [8, 12, 16],
                "slow": [21, 26, 30],
                "signal": [7, 9, 11]
            }
        elif strategy_name == "hyperfocus_strategy":
            return {
                "sensitivity": [0.8, 1.0, 1.2, 1.5],
                "detection_window": [15, 20, 25],
                "correlation_threshold": [0.6, 0.7, 0.8],
                "rsi_period": [9, 14, 21],
                "bollinger_bands_width": [1.5, 2.0, 2.5]
            }
        else:
            # Default fallback
            return {
                "param1": [1, 2, 3],
                "param2": [0.1, 0.2, 0.3]
            }
    
    def run_optimization(self, strategy_name: str, symbols: List[str], days: int = 30, 
                        timeframe: str = '1h', initial_capital: float = 10000,
                        metric: str = 'sharpe_ratio'):
        """Run parameter optimization for a strategy"""
        print(f"{Fore.CYAN}Starting parameter optimization for {strategy_name}")
        print(f"{Fore.YELLOW}This may take some time depending on the parameter grid size...")
        
        # Get parameter grid
        param_grid = self.get_parameter_grid(strategy_name)
        print(f"{Fore.GREEN}Parameter grid loaded with {len(param_grid)} parameters")
        
        # Generate all parameter combinations
        param_keys = list(param_grid.keys())
        param_values = list(param_grid.values())
        combinations = list(itertools.product(*param_values))
        
        print(f"{Fore.GREEN}Testing {len(combinations)} parameter combinations")
        print(f"{Fore.CYAN}{'=' * 70}")
        
        # Store results
        self.results = []
        
        # Get number of CPUs for parallel processing
        cpus = max(1, multiprocessing.cpu_count() - 1)  # Keep 1 CPU free
        
        # Prepare arguments for parallel processing
        args_list = []
        for i, combo in enumerate(combinations):
            params = dict(zip(param_keys, combo))
            for symbol in symbols:
                args_list.append((strategy_name, symbol, days, timeframe, initial_capital, params, i))
        
        # Run backtests in parallel
        with multiprocessing.Pool(processes=cpus) as pool:
            results = pool.starmap(self._run_backtest_with_params, args_list)
        
        # Combine results
        self.results.extend([r for r in results if r is not None])
        
        # Sort results by the optimization metric
        self.results.sort(key=lambda x: x.get(metric, 0), reverse=True)
        
        # Display top results
        self._display_top_results(metric)
        
        # Save results to CSV
        self._save_results_to_csv()
        
        # Plot top parameter performance
        self._plot_parameter_performance(metric)
        
        return self.results
    
    def _run_backtest_with_params(self, strategy_name, symbol, days, timeframe, 
                                 initial_capital, params, combo_idx) -> Dict:
        """Run a single backtest with specific parameters"""
        try:
            # Update strategy parameters in config
            config_copy = self.config.copy()
            if 'strategies' not in config_copy:
                config_copy['strategies'] = {}
            
            if strategy_name not in config_copy['strategies']:
                config_copy['strategies'][strategy_name] = {}
            
            # Apply parameters
            for key, value in params.items():
                config_copy['strategies'][strategy_name][key] = value
            
            # Set active strategy
            config_copy['strategies']['active_strategy'] = strategy_name
            
            # Generate temporary config file
            temp_config_path = os.path.join(parent_dir, f'temp_config_{combo_idx}.json')
            with open(temp_config_path, 'w') as f:
                json.dump(config_copy, f)
            
            # Create backtester with temporary config
            backtester = SignalBacktester(temp_config_path)
            
            # Run backtest
            result = backtester.run_backtest(symbol, days, timeframe, initial_capital)
            
            # Clean up temp file
            try:
                os.remove(temp_config_path)
            except:
                pass
            
            # Add parameters and symbol to results
            result['parameters'] = params
            result['symbol'] = symbol
            result['strategy'] = strategy_name
            
            # Print progress
            param_str = ', '.join([f"{k}={v}" for k, v in params.items()])
            perf = result.get('return_pct', 0)
            color = Fore.GREEN if perf > 0 else Fore.RED
            print(f"{symbol} with {param_str}: {color}{perf:.2f}% return")
            
            return result
        except Exception as e:
            print(f"{Fore.RED}Error in backtest: {str(e)}")
            return None
    
    def _display_top_results(self, metric: str, top_n: int = 5):
        """Display top optimization results"""
        if not self.results:
            print(f"{Fore.RED}No results to display")
            return
        
        print(f"\n{Fore.CYAN}{'=' * 70}")
        print(f"{Fore.CYAN}{Style.BRIGHT} TOP {top_n} PARAMETER COMBINATIONS")
        print(f"{Fore.CYAN}{'=' * 70}")
        
        for i, result in enumerate(self.results[:top_n]):
            params = result.get('parameters', {})
            symbol = result.get('symbol', 'Unknown')
            
            # Display key metrics
            print(f"\n{Fore.WHITE}Rank {i+1}: {Fore.YELLOW}{symbol}")
            print(f"{Fore.CYAN}Parameters:")
            for key, value in params.items():
                print(f"{Fore.WHITE}  {key}: {Fore.CYAN}{value}")
            
            # Display performance metrics
            print(f"{Fore.CYAN}Performance:")
            metrics = {
                'Return': f"{result.get('return_pct', 0):.2f}%",
                'Profit Factor': f"{result.get('profit_factor', 0):.2f}",
                'Win Rate': f"{result.get('win_rate', 0):.2f}%",
                'Trades': str(result.get('trades', 0)),
                'Sharpe': f"{result.get('sharpe_ratio', 0):.2f}",
                'Max DD': f"{result.get('max_drawdown_pct', 0):.2f}%"
            }
            
            for key, value in metrics.items():
                if key == 'Return' and float(value.rstrip('%')) > 0:
                    print(f"{Fore.WHITE}  {key}: {Fore.GREEN}{value}")
                elif key == 'Return':
                    print(f"{Fore.WHITE}  {key}: {Fore.RED}{value}")
                else:
                    print(f"{Fore.WHITE}  {key}: {Fore.CYAN}{value}")  # Fixed: Added missing parenthesis
    
    def _save_results_to_csv(self):
        """Save optimization results to CSV"""
        if not self.results:
            return
        
        # Create DataFrame from results
        data = []
        
        for result in self.results:
            row = {
                'Symbol': result.get('symbol', ''),
                'Strategy': result.get('strategy', ''),
                'Return_pct': result.get('return_pct', 0),
                'Profit_Factor': result.get('profit_factor', 0),
                'Win_Rate': result.get('win_rate', 0),
                'Trades': result.get('trades', 0),
                'Sharpe_Ratio': result.get('sharpe_ratio', 0),
                'Max_Drawdown_pct': result.get('max_drawdown_pct', 0),
            }
            
            # Add parameters
            for key, value in result.get('parameters', {}).items():
                row[f'param_{key}'] = value
            
            data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        strategy = self.results[0]['strategy'] if self.results else 'unknown'
        filename = f"optimization_{strategy}_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        print(f"\n{Fore.GREEN}Results saved to {filepath}")
    
    def _plot_parameter_performance(self, metric: str):
        """Plot parameter impact on performance"""
        if not self.results or len(self.results) < 5:
            return
        
        # Get parameters from first result
        params = self.results[0].get('parameters', {})
        
        if not params:
            return
        
        # Create figure
        fig, axes = plt.subplots(len(params), 1, figsize=(10, 4 * len(params)))
        if len(params) == 1:
            axes = [axes]  # Make it iterable
        
        # For each parameter, plot its impact on performance
        for i, (param_name, _) in enumerate(params.items()):
            # Group results by this parameter
            param_values = {}
            
            for result in self.results:
                param_value = result['parameters'].get(param_name)
                
                if param_value not in param_values:
                    param_values[param_value] = []
                
                param_values[param_value].append(result.get(metric, 0))
            
            # Calculate average performance for each parameter value
            avg_performance = {}
            for value, performances in param_values.items():
                avg_performance[value] = sum(performances) / len(performances)
            
            # Sort by parameter value
            sorted_values = sorted(avg_performance.items())
            x_values = [str(v[0]) for v in sorted_values]
            y_values = [v[1] for v in sorted_values]
            
            # Plot
            bar_color = 'green' if max(y_values) > 0 else 'red'
            axes[i].bar(x_values, y_values, color=bar_color, alpha=0.6)
            axes[i].set_title(f"Impact of {param_name} on {metric}")
            axes[i].set_xlabel(param_name)
            axes[i].set_ylabel(metric)
            axes[i].grid(axis='y', alpha=0.3)
        
        # Save figure
        plt.tight_layout()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        strategy = self.results[0]['strategy'] if self.results else 'unknown'
        filename = f"param_impact_{strategy}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath)
        
        print(f"{Fore.GREEN}Parameter impact chart saved to {filepath}")

def main():
    """Main function to run the optimizer"""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='BROski Bot - Strategy Parameter Optimizer')
    
    parser.add_argument('--strategy', type=str, required=True, 
                        help='Strategy to optimize (e.g., "rsi_strategy", "macd_strategy", "hyperfocus_strategy")')
    parser.add_argument('--symbols', type=str, default='BTC/USDT',
                        help='Comma-separated list of symbols to test')
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days to backtest')
    parser.add_argument('--timeframe', type=str, default='1h',
                        choices=['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
                        help='Timeframe for backtesting')
    parser.add_argument('--capital', type=float, default=10000,
                        help='Initial capital for backtesting')
    parser.add_argument('--metric', type=str, default='sharpe_ratio',
                        choices=['return_pct', 'profit_factor', 'win_rate', 'sharpe_ratio'],
                        help='Metric to optimize for')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create optimizer
    optimizer = StrategyOptimizer()
    
    # Parse symbols
    symbols = args.symbols.split(',')
    
    # Run optimization
    optimizer.run_optimization(
        strategy_name=args.strategy,
        symbols=symbols,
        days=args.days,
        timeframe=args.timeframe,
        initial_capital=args.capital,
        metric=args.metric
    )
    
    print(f"\n{Fore.GREEN}Optimization completed successfully!")

if __name__ == "__main__":
    main()

# Add to _generate_alerts_from_data method in backtest_signals.py
# Create more frequent test alerts
def _generate_alerts_from_data(self, symbol, candle, i):
    if i % 10 == 0:  # Every 10 candles
        self.alerts_manager.add_alert_from_dict({
            'type': 'PriceAlert',
            'name': f'{symbol} Test Alert',
            'symbol': symbol,
            'price': candle['close'] * 0.999,  # Just below current price
            'condition': 'below'
        })
        
