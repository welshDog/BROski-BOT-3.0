#!/usr/bin/env python
"""
BROski Bot - ML Integration Example
Demonstrates how to integrate ML components with the main BROski Bot
"""
import os
import sys
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pandas as pd
import numpy as np
from colorama import Fore, Style, init as colorama_init

# Import ML components
from utils.ml_tools import MLPricePredictor
from strategies.ml_enhanced_strategy import MLEnhancedStrategy
from ui.ml_dashboard_panel import MLDashboardPanel
from utils.integration_tester import MLStrategyTester

# Initialize colorama
colorama_init(autoreset=True)

class MLIntegrationDemo:
    """Demo application showing ML integration with BROski Bot"""
    
    def __init__(self):
        """Initialize the ML integration demo"""
        self.root = tk.Tk()
        self.root.title("BROski Bot - ML Integration Demo")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Set up styles
        self.setup_styles()
        
        # Create ML predictor
        self.ml_predictor = None
        self.ml_strategy = None
        self.test_data = None
        
        # Create UI
        self.create_ui()
        
        print(f"{Fore.GREEN}ML Integration Demo initialized{Style.RESET_ALL}")
    
    def setup_styles(self):
        """Set up ttk styles for UI components"""
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('MLPanel.TFrame', background='#f5f5f5', relief='ridge')
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Info.TLabel', font=('Helvetica', 10), background='#f0f0f0')
    
    def create_ui(self):
        """Create the demo UI"""
        # Main container
        main_container = ttk.Frame(self.root, padding=10)
        main_container.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(
            header_frame, 
            text="BROski Bot - Machine Learning Integration", 
            style='Header.TLabel'
        ).pack(side='left')
        
        # Control panel
        control_frame = ttk.LabelFrame(main_container, text="Controls")
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Buttons
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill='x', padx=5, pady=5)
        
        self.load_data_btn = ttk.Button(
            buttons_frame,
            text="1. Load Sample Data",
            command=self.load_sample_data
        )
        self.load_data_btn.pack(side='left', padx=5)
        
        self.train_ml_btn = ttk.Button(
            buttons_frame,
            text="2. Train ML Model",
            command=self.train_ml_model,
            state='disabled'
        )
        self.train_ml_btn.pack(side='left', padx=5)
        
        self.create_strategy_btn = ttk.Button(
            buttons_frame,
            text="3. Create Enhanced Strategy",
            command=self.create_enhanced_strategy,
            state='disabled'
        )
        self.create_strategy_btn.pack(side='left', padx=5)
        
        self.test_strategy_btn = ttk.Button(
            buttons_frame,
            text="4. Run Strategy Test",
            command=self.run_strategy_test,
            state='disabled'
        )
        self.test_strategy_btn.pack(side='left', padx=5)
        
        # Status info
        self.status_var = tk.StringVar(value="Ready to start")
        status_label = ttk.Label(
            control_frame,
            textvariable=self.status_var,
            style='Info.TLabel'
        )
        status_label.pack(fill='x', padx=5, pady=5)
        
        # Main content - split into two frames
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill='both', expand=True)
        
        # Left panel - Dashboard
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.ml_dashboard = MLDashboardPanel(left_frame)
        self.ml_dashboard.pack(fill='both', expand=True)
        
        # Right panel - Info/Results
        right_frame = ttk.LabelFrame(content_frame, text="Results")
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Results text area
        self.results_text = tk.Text(right_frame, wrap='word', height=20)
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(self.results_text, command=self.results_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.results_text['yscrollcommand'] = scrollbar.set
        
        self.log_message("Welcome to the BROski Bot ML Integration Demo")
        self.log_message("Follow the numbered steps to see how ML integration works")
    
    def load_sample_data(self):
        """Load sample cryptocurrency data"""
        self.log_message("Loading sample data...")
        
        try:
            # Generate sample data
            start_date = datetime(2022, 1, 1)
            dates = pd.date_range(start=start_date, periods=200, freq='D')
            
            # Create a realistic price series
            np.random.seed(42)  # For reproducibility
            price_changes = np.random.normal(0, 0.02, 200).cumsum()
            btc_prices = 20000 * (1 + price_changes)
            
            # Generate OHLCV data
            self.test_data = pd.DataFrame({
                'open': btc_prices * (1 + np.random.normal(0, 0.005, 200)),
                'high': btc_prices * (1 + np.abs(np.random.normal(0, 0.01, 200))),
                'low': btc_prices * (1 - np.abs(np.random.normal(0, 0.01, 200))),
                'close': btc_prices,
                'volume': np.random.normal(1000000, 200000, 200) * btc_prices / 20000,
                'symbol': 'BTC/USDT'
            }, index=dates)
            
            # Ensure high is actual high and low is actual low
            self.test_data['high'] = np.maximum(np.maximum(self.test_data['high'], self.test_data['open']), self.test_data['close'])
            self.test_data['low'] = np.minimum(np.minimum(self.test_data['low'], self.test_data['open']), self.test_data['close'])
            
            self.log_message(f"Successfully loaded sample data with {len(self.test_data)} days")
            self.log_message(f"Date range: {self.test_data.index[0].date()} to {self.test_data.index[-1].date()}")
            self.log_message(f"Price range: ${self.test_data['low'].min():.2f} - ${self.test_data['high'].max():.2f}")
            
            # Enable training button
            self.train_ml_btn['state'] = 'normal'
            self.status_var.set("Data loaded. Ready to train ML model.")
            
        except Exception as e:
            self.log_message(f"Error loading data: {str(e)}", is_error=True)
    
    def train_ml_model(self):
        """Train the ML price prediction model"""
        if self.test_data is None:
            self.log_message("No data available. Please load data first.", is_error=True)
            return
        
        self.log_message("Training ML price prediction model...")
        
        try:
            # Create and train ML predictor
            self.ml_predictor = MLPricePredictor(model_type='random_forest')
            metrics = self.ml_predictor.train(self.test_data, prediction_window=5)
            
            # Log training results
            self.log_message(f"ML model training complete!")
            self.log_message(f"MSE: {metrics['mse']:.6f}")
            self.log_message(f"R² Score: {metrics['r2']:.6f}")
            
            # Make a test prediction
            latest_data = self.test_data.tail(30)
            prediction = self.ml_predictor.predict(latest_data)
            self.log_message(f"Test prediction (5-day price change): {prediction*100:.2f}%")
            
            # Update ML dashboard
            self.ml_dashboard.ml_predictor = self.ml_predictor
            self.ml_dashboard.refresh_predictions()
            
            # Enable next step
            self.create_strategy_btn['state'] = 'normal'
            self.status_var.set("ML model trained. Ready to create enhanced strategy.")
            
        except Exception as e:
            self.log_message(f"Error training ML model: {str(e)}", is_error=True)
    
    def create_enhanced_strategy(self):
        """Create the ML-enhanced trading strategy"""
        if self.ml_predictor is None:
            self.log_message("No ML model available. Please train the model first.", is_error=True)
            return
        
        self.log_message("Creating ML-enhanced trading strategy...")
        
        try:
            # Create ML-enhanced strategy
            self.ml_strategy = MLEnhancedStrategy(
                base_strategy_name='rsi',
                prediction_weight=0.5,
                confidence_threshold=0.3
            )
            
            # Assign our trained model
            self.ml_strategy.ml_predictor = self.ml_predictor
            
            self.log_message("ML-enhanced strategy created successfully")
            self.log_message("- Base strategy: RSI")
            self.log_message("- ML prediction weight: 50%")
            self.log_message("- Confidence threshold: 30%")
            
            # Generate a test signal
            latest_data = self.test_data.tail(50)
            signal = self.ml_strategy.generate_signals(latest_data)
            
            self.log_message("\nTest trading signal generated:")
            self.log_message(f"- Signal: {signal['signal'].upper()}")
            self.log_message(f"- Price: ${signal['price']:.2f}")
            if 'ml_prediction_pct' in signal:
                self.log_message(f"- ML prediction: {signal['ml_prediction_pct']}%")
                self.log_message(f"- ML confidence: {signal['ml_confidence']}% ({signal['ml_confidence_level']})")
            
            # Enable next step
            self.test_strategy_btn['state'] = 'normal'
            self.status_var.set("Enhanced strategy created. Ready to run strategy test.")
            
        except Exception as e:
            self.log_message(f"Error creating enhanced strategy: {str(e)}", is_error=True)
    
    def run_strategy_test(self):
        """Run a test of the ML-enhanced strategy"""
        if self.ml_strategy is None:
            self.log_message("No strategy available. Please create the strategy first.", is_error=True)
            return
        
        self.log_message("\nRunning ML strategy comparison test...")
        
        try:
            # Initialize the strategy tester
            tester = MLStrategyTester(
                base_strategies=['rsi'],
                test_symbols=['BTC/USDT']
            )
            
            # Use our existing test data
            setattr(tester, '_fetch_historical_data', lambda symbol, days: self.test_data)
            
            # Run test with different ML weights
            weights = [0, 0.3, 0.5, 0.7, 1.0]
            self.log_message(f"Testing with ML weights: {weights}")
            
            # Replace tester's run_tests method to use our test data
            original_run_tests = tester.run_tests
            
            def run_tests_with_our_data(prediction_weights=None):
                results = []
                for weight in weights:
                    self.log_message(f"Testing with ML weight: {weight}")
                    strategy = MLEnhancedStrategy(
                        base_strategy_name='rsi',
                        prediction_weight=weight
                    )
                    
                    # Use our trained model
                    if weight > 0:
                        strategy.ml_predictor = self.ml_predictor
                    
                    # Split data for backtest
                    train_data = self.test_data.iloc[:140]
                    test_data = self.test_data.iloc[140:]
                    
                    # Run backtest
                    backtest_results = tester._run_backtest(strategy, test_data, 'BTC/USDT')
                    
                    # Add metadata
                    backtest_results.update({
                        'symbol': 'BTC/USDT',
                        'strategy': 'rsi',
                        'ml_weight': weight,
                        'is_ml_enhanced': weight > 0
                    })
                    
                    results.append(backtest_results)
                
                results_df = pd.DataFrame(results)
                tester._save_results(results_df)
                return results_df
            
            # Patch the run_tests method
            tester.run_tests = run_tests_with_our_data
            
            # Run the tests
            results = tester.run_tests(prediction_weights=weights)
            
            # Display results
            if results is not None:
                self.log_message("\nStrategy test results:")
                for index, row in results.iterrows():
                    ml_info = "ML-enhanced" if row['is_ml_enhanced'] else "Standard"
                    self.log_message(f"- {ml_info} RSI (weight: {row['ml_weight']}):")
                    self.log_message(f"  ROI: {row['roi']:.2f}%")
                    self.log_message(f"  Win rate: {row['win_rate']:.2f}%")
                    self.log_message(f"  vs Buy & Hold: {row['roi_vs_hold']:.2f}%")
                    self.log_message(f"  Number of trades: {row['num_trades']}")
                
                # Find best strategy
                best_row = results.loc[results['roi'].idxmax()]
                self.log_message(f"\nBest performing strategy:")
                self.log_message(f"- {'ML-enhanced' if best_row['is_ml_enhanced'] else 'Standard'} RSI with weight {best_row['ml_weight']}")
                self.log_message(f"- ROI: {best_row['roi']:.2f}%")
                
                self.status_var.set("Strategy test complete. See results.")
                
            else:
                self.log_message("No test results were generated.", is_error=True)
            
        except Exception as e:
            self.log_message(f"Error running strategy test: {str(e)}", is_error=True)
            import traceback
            self.log_message(traceback.format_exc(), is_error=True)
    
    def log_message(self, message, is_error=False):
        """Add message to the log text area"""
        self.results_text.configure(state='normal')
        
        if self.results_text.index('end-1c') != '1.0':
            self.results_text.insert('end', '\n')
            
        if is_error:
            self.results_text.insert('end', f"ERROR: {message}", 'error')
        else:
            self.results_text.insert('end', message)
            
        self.results_text.configure(state='disabled')
        self.results_text.see('end')
        
        # Configure tags for styling
        self.results_text.tag_configure('error', foreground='red')
    
    def get_current_data(self):
        """Return current data for ML dashboard"""
        if self.test_data is not None:
            return self.test_data.tail(30)
        return None
    
    def run(self):
        """Run the demo application"""
        self.root.mainloop()

# Run the demo if script is executed directly
if __name__ == "__main__":
    demo = MLIntegrationDemo()
    demo.run()
