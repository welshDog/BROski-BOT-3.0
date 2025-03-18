"""
BROski Bot 3.0 - Main Application Entry Point

This script combines all refactored components into a complete trading bot solution.
"""
import argparse
import logging
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

from data.fetcher import ExchangeDataFetcher
from data.processor import DataProcessor
from data.storage import DataStorage
from strategies.hyperfocus_strategy import HyperFocusStrategy


def setup_logging(log_level=logging.INFO):
    """Set up logging configuration."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"broski_bot_{datetime.now().strftime('%Y%m%d')}.log")
        ]
    )


def load_config(config_path="config.json"):
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading config: {str(e)}")
        return {}


def run_trading_bot(config_path="config.json", backtest_mode=False):
    """
    Run the trading bot with the given configuration.
    
    Args:
        config_path: Path to configuration file
        backtest_mode: Whether to run in backtest mode
    """
    # Set up logging
    setup_logging()
    logger = logging.getLogger("BROskiBot")
    logger.info("Starting BROski Bot 3.0")
    
    # Load configuration
    config = load_config(config_path)
    if not config:
        logger.error("Failed to load configuration. Exiting.")
        return
    
    # Initialize components
    try:
        # Data components
        data_dir = config.get('data_dir', 'data_storage')
        storage = DataStorage(data_dir=data_dir)
        processor = DataProcessor()
        
        # Exchange connection
        if backtest_mode:
            logger.info("Running in backtest mode")
            exchange = None
        else:
            exchange_config = config.get('exchange', {})
            exchange_name = exchange_config.get('name', 'binance')
            api_key = exchange_config.get('api_key')
            api_secret = exchange_config.get('api_secret')
            
            logger.info(f"Connecting to exchange: {exchange_name}")
            exchange = ExchangeDataFetcher(
                exchange_name=exchange_name,
                api_key=api_key,
                api_secret=api_secret,
                test_mode=True  # Use test mode for safety
            )
        
        # Strategy configuration
        strategy_config = config.get('strategies', {}).get('hyperfocus_strategy', {})
        strategy = HyperFocusStrategy(config_path)
        
        # Symbol configuration
        symbols = config.get('symbols', ['BTC/USDT'])
        timeframes = config.get('timeframes', ['1h'])
        
        if backtest_mode:
            # Run backtest
            run_backtest(strategy, storage, processor, config, symbols, timeframes)
        else:
            # Run live trading
            run_live_trading(exchange, strategy, storage, processor, config, symbols, timeframes)
        
    except Exception as e:
        logger.exception(f"Error in trading bot: {str(e)}")


def run_backtest(strategy, storage, processor, config, symbols, timeframes):
    """Run backtesting mode."""
    logger = logging.getLogger("BROskiBot.Backtest")
    
    start_date_str = config.get('backtest', {}).get('start_date', '2023-01-01')
    end_date_str = config.get('backtest', {}).get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    start_date = datetime.fromisoformat(start_date_str)
    end_date = datetime.fromisoformat(end_date_str)
    
    initial_capital = config.get('backtest', {}).get('initial_capital', 10000)
    commission = config.get('backtest', {}).get('commission', 0.001)
    
    for symbol in symbols:
        for timeframe in timeframes:
            logger.info(f"Backtesting {symbol} on {timeframe} timeframe")
            
            # Load data from storage or generate sample data
            data = storage.load_market_data(symbol, timeframe, start_date, end_date)
            
            if data.empty:
                logger.warning(f"No data available for {symbol} ({timeframe}). Generating sample data.")
                data = strategy._generate_sample_data(symbol, (end_date - start_date).days, timeframe)
            
            # Run backtest
            results = strategy.backtest(data, symbol, initial_capital, commission)
            
            # Print results
            logger.info(f"Backtest results for {symbol} ({timeframe}):")
            logger.info(f"Final equity: ${results['final_equity']:.2f}")
            logger.info(f"Return: {results['return_pct']:.2f}%")
            logger.info(f"Number of trades: {results['trades']}")
            
            if 'win_rate' in results:
                logger.info(f"Win rate: {results['win_rate']:.2f}%")
            
            if 'max_drawdown' in results:
                logger.info(f"Max drawdown: {results['max_drawdown']:.2f}%")


def run_live_trading(exchange, strategy, storage, processor, config, symbols, timeframes):
    """Run live trading mode."""
    logger = logging.getLogger("BROskiBot.Live")
    logger.info("Running in live trading mode")
    
    # Configure trading parameters
    days_of_data = config.get('trading', {}).get('days_of_data', 30)
    check_interval = config.get('trading', {}).get('check_interval', 60)  # seconds
    
    # Get historical data for analysis
    for symbol in symbols:
        logger.info(f"Processing {symbol}")
        
        for timeframe in timeframes:
            logger.info(f"Getting historical data for {symbol} on {timeframe} timeframe")
            
            # Fetch historical data
            since = datetime.now() - timedelta(days=days_of_data)
            df = exchange.fetch_historical_data(
                symbol=symbol,
                timeframe=timeframe,
                start_date=since,
                end_date=datetime.now()
            )
            
            # Save data to storage
            if not df.empty:
                storage.save_market_data(df, symbol, timeframe)
                logger.info(f"Saved {len(df)} candles for {symbol} ({timeframe})")
                
                # Generate signals
                market_data = {
                    'symbol': symbol,
                    'ohlcv': [
                        [df.index[i].timestamp() * 1000] + 
                        [df.iloc[i][col] for col in ['open', 'high', 'low', 'close', 'volume']]
                        for i in range(len(df))
                    ]
                }
                
                signal = strategy.get_signal(market_data)
                logger.info(f"Signal for {symbol}: {signal}")
            else:
                logger.warning(f"No data fetched for {symbol} ({timeframe})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BROski Bot 3.0 Trading System")
    parser.add_argument('--config', type=str, default='config.json', help='Path to config file')
    parser.add_argument('--backtest', action='store_true', help='Run in backtest mode')
    
    args = parser.parse_args()
    run_trading_bot(config_path=args.config, backtest_mode=args.backtest)
