#!/usr/bin/env python
"""
BROski Bot 3.0 - Unified ML Trading Dashboard
Combines ML predictions, backtrading results and strategy visualization
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename, askdirectory
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import datetime
from colorama import Fore, Style, init as colorama_init

# Import BROski modules
from utils.ml_tools import MLPricePredictor
from utils.backtrader_patch import apply_patches
from utils.backtest_runner import BacktestRunner
from strategies.backtrader_ml_strategy import BROskiMLStrategy, BROskiRSIStrategy
from ui.ml_dashboard_panel import MLDashboardPanel

# Initialize colorama
colorama_init(autoreset=True)

class MLTradingDashboard(tk.Tk):
    """Unified dashboard for ML-powered trading"""
    
    def __init__(self):
        super().__init__()
        
        # Configure the window
        self.title("BROski Bot 3.0 - ML Trading Dashboard")
        self.geometry("1200x800")
        self.configure(bg='#f0f0f0')
        
        # Apply theme
        self.setup_styles()
        
        # Initialize variables
        self.ml_predictor = None
        self.backtest_runner = None
        self.historical_data = None
        self.backtesting_thread = None
        self.current_model_path = None
        self.current_data_path = None
        
        # Create UI
        self.create_menu()
        self.create_main_interface()
        
        # Apply Backtrader patches
        apply_patches()
        
        print(f"{Fore.GREEN}ML Trading Dashboard initialized{Style.RESET_ALL}")
        self.status_message("Ready. Start by loading data or a trained model.")
    
    def setup_styles(self):
        """Configure ttk styles for consistent appearance"""
        style = ttk.Style()
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TFrame', background='#f5f5f5')
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Status.TLabel', font=('Helvetica', 10), foreground='#555555')
        style.configure('Info.TLabel', font=('Helvetica', 10))
        style.configure('Section.TLabelframe', background='#f5f5f5')
        style.configure('Graph.TFrame', background='#ffffff', relief='ridge')
    
    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load Data", command=self.load_data)
        file_menu.add_command(label="Save Data", command=self.save_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # ML menu
        ml_menu = tk.Menu(menubar, tearoff=0)
        ml_menu.add_command(label="Load Model", command=self.load_model)
        ml_menu.add_command(label="Train Model", command=self.train_model)
        ml_menu.add_command(label="Save Model", command=self.save_model)
        menubar.add_cascade(label="ML Model", menu=ml_menu)
        
        # Backtest menu
        backtest_menu = tk.Menu(menubar, tearoff=0)
        backtest_menu.add_command(label="Run Basic Backtest", command=self.run_standard_backtest)
        backtest_menu.add_command(label="Run ML Backtest", command=self.run_ml_backtest)
        backtest_menu.add_command(label="Generate Report", command=self.generate_backtest_report)
        menubar.add_cascade(label="Backtest", menu=backtest_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menubar)
    
    def create_main_interface(self):
        """Create the main interface with tabs"""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Dashboard Overview
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text="Dashboard")
        self.create_dashboard_tab()
        
        # Tab 2: ML Training & Prediction
        self.tab_ml = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ml, text="ML Training")
        self.create_ml_tab()
        
        # Tab 3: Backtesting
        self.tab_backtest = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_backtest, text="Backtesting")
        self.create_backtest_tab()
        
        # Tab 4: Live Trading
        self.tab_live = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_live, text="Live Trading")
        self.create_live_trading_tab()
        
        # Status bar at the bottom
        self.status_bar = ttk.Label(self, text="Ready", style='Status.TLabel')
        self.status_bar.pack(fill='x', padx=10, pady=5)
    
    def create_dashboard_tab(self):
        """Create the dashboard overview tab"""
        # Top section: Summary stats
        stats_frame = ttk.LabelFrame(self.tab_dashboard, text="Performance Summary", style='Section.TLabelframe')
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        # Grid of key metrics
        metrics_frame = ttk.Frame(stats_frame)
        metrics_frame.pack(fill='x', padx=10, pady=10)
        
        metrics = [
            ("ML Model Status:", "Not Loaded", "ml_status"),
            ("Predicted Change:", "N/A", "pred_change"),
            ("Backtest ROI:", "N/A", "backtest_roi"),
            ("Win Rate:", "N/A", "win_rate"),
            ("Sharpe Ratio:", "N/A", "sharpe"),
            ("Max Drawdown:", "N/A", "drawdown")
        ]
        
        self.metric_vars = {}
        
        for i, (label_text, default_value, var_name) in enumerate(metrics):
            row = i // 3
            col = i % 3
            
            label_frame = ttk.Frame(metrics_frame)
            label_frame.grid(row=row, column=col, padx=20, pady=5, sticky='w')
            
            ttk.Label(label_frame, text=label_text, style='Info.TLabel').pack(anchor='w')
            
            # Create StringVar and store reference
            value_var = tk.StringVar(value=default_value)
            self.metric_vars[var_name] = value_var
            
            ttk.Label(label_frame, textvariable=value_var, font=('Helvetica', 12, 'bold')).pack(anchor='w')
        
        # Center section: Charts
        charts_frame = ttk.Frame(self.tab_dashboard, style='Graph.TFrame')
        charts_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create figure for charts
        self.dashboard_figure = plt.Figure(figsize=(10, 6), dpi=100)
        
        # Create tabs within the chart area
        charts_notebook = ttk.Notebook(charts_frame)
        charts_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add chart tabs
        price_tab = ttk.Frame(charts_notebook)
        charts_notebook.add(price_tab, text="Price & Predictions")
        
        returns_tab = ttk.Frame(charts_notebook)
        charts_notebook.add(returns_tab, text="Strategy Returns")
        
        comparison_tab = ttk.Frame(charts_notebook)
        charts_notebook.add(comparison_tab, text="Strategy Comparison")
        
        # Set up the charts
        self.price_chart_canvas = FigureCanvasTkAgg(self.dashboard_figure, price_tab)
        self.price_chart_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Draw empty charts initially
        self.setup_empty_charts()
        
        # Bottom section: Recent activity log
        log_frame = ttk.LabelFrame(self.tab_dashboard, text="Activity Log", style='Section.TLabelframe')
        log_frame.pack(fill='x', padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=6, width=10, wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add scrollbar to log
        log_scrollbar = ttk.Scrollbar(self.log_text, orient='vertical', command=self.log_text.yview)
        log_scrollbar.pack(side='right', fill='y')
        self.log_text['yscrollcommand'] = log_scrollbar.set
    
    def create_ml_tab(self):
        """Create the ML training tab"""
        # Left panel - Controls
        controls_frame = ttk.Frame(self.tab_ml)
        controls_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        # Data section
        data_frame = ttk.LabelFrame(controls_frame, text="Data", style='Section.TLabelframe')
        data_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            data_frame, 
            text="Load Historical Data", 
            command=self.load_data
        ).pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            data_frame, 
            text="Generate Sample Data", 
            command=self.generate_sample_data
        ).pack(fill='x', padx=5, pady=5)
        
        ttk.Label(data_frame, text="Symbol:").pack(anchor='w', padx=5, pady=2)
        
        self.symbol_var = tk.StringVar(value="BTC/USDT")
        symbol_entry = ttk.Entry(data_frame, textvariable=self.symbol_var)
        symbol_entry.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(data_frame, text="Data Range (Days):").pack(anchor='w', padx=5, pady=2)
        
        self.days_var = tk.IntVar(value=180)
        days_entry = ttk.Entry(data_frame, textvariable=self.days_var)
        days_entry.pack(fill='x', padx=5, pady=5)
        
        # Model section
        model_frame = ttk.LabelFrame(controls_frame, text="ML Model", style='Section.TLabelframe')
        model_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(model_frame, text="Model Type:").pack(anchor='w', padx=5, pady=2)
        
        self.model_type_var = tk.StringVar(value="random_forest")
        model_type_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_type_var,
            values=["random_forest", "gradient_boosting", "linear_regression"]
        )
        model_type_combo.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(model_frame, text="Prediction Window (days):").pack(anchor='w', padx=5, pady=2)
        
        self.prediction_window_var = tk.IntVar(value=5)
        prediction_window_entry = ttk.Entry(model_frame, textvariable=self.prediction_window_var)
        prediction_window_entry.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            model_frame, 
            text="Train Model", 
            command=self.train_model
        ).pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            model_frame, 
            text="Load Existing Model", 
            command=self.load_model
        ).pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            model_frame, 
            text="Save Model", 
            command=self.save_model
        ).pack(fill='x', padx=5, pady=5)
        
        # Right panel - ML dashboard panel
        right_frame = ttk.Frame(self.tab_ml)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.ml_dashboard_panel = MLDashboardPanel(right_frame)
        self.ml_dashboard_panel.pack(fill='both', expand=True)
    
    def create_backtest_tab(self):
        """Create the backtesting tab"""
        # Top section: Controls
        controls_frame = ttk.LabelFrame(self.tab_backtest, text="Backtest Configuration", style='Section.TLabelframe')
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        # Create left and right control sections
        left_controls = ttk.Frame(controls_frame)
        left_controls.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        right_controls = ttk.Frame(controls_frame)
        right_controls.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Left controls
        ttk.Label(left_controls, text="Time Period:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.backtest_days_var = tk.IntVar(value=180)
        ttk.Entry(left_controls, textvariable=self.backtest_days_var).grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        
        ttk.Label(left_controls, text="Trading Pair:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.backtest_pair_var = tk.StringVar(value="BTC/USDT")
        ttk.Entry(left_controls, textvariable=self.backtest_pair_var).grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        
        ttk.Label(left_controls, text="Base Strategy:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.backtest_strategy_var = tk.StringVar(value="RSI")
        ttk.Combobox(
            left_controls, 
            textvariable=self.backtest_strategy_var,
            values=["RSI", "MACD", "Bollinger"]
        ).grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        
        # Right controls
        ttk.Label(right_controls, text="Initial Capital:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.backtest_capital_var = tk.DoubleVar(value=10000)
        ttk.Entry(right_controls, textvariable=self.backtest_capital_var).grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        
        ttk.Label(right_controls, text="ML Weight (%):").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.backtest_ml_weight_var = tk.DoubleVar(value=50.0)
        ttk.Scale(
            right_controls,
            variable=self.backtest_ml_weight_var,
            from_=0,
            to=100,
            orient='horizontal'
        ).grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        
        ttk.Label(right_controls, text="Compare Weights:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.backtest_compare_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_controls, variable=self.backtest_compare_var).grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        # Buttons row
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            buttons_frame,
            text="Run Standard Backtest",
            command=self.run_standard_backtest
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Run ML Backtest",
            command=self.run_ml_backtest
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Generate Report",
            command=self.generate_backtest_report
        ).pack(side='left', padx=5)
        
        # Bottom section: Results visualization
        results_frame = ttk.LabelFrame(self.tab_backtest, text="Backtest Results", style='Section.TLabelframe')
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create a notebook for backtest visualizations
        self.backtest_notebook = ttk.Notebook(results_frame)
        self.backtest_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Equity curve tab
        equity_tab = ttk.Frame(self.backtest_notebook)
        self.backtest_notebook.add(equity_tab, text="Equity Curve")
        
        self.equity_figure = plt.Figure(figsize=(10, 6), dpi=100)
        self.equity_subplot = self.equity_figure.add_subplot(111)
        self.equity_canvas = FigureCanvasTkAgg(self.equity_figure, equity_tab)
        self.equity_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Comparison tab
        comparison_tab = ttk.Frame(self.backtest_notebook)
        self.backtest_notebook.add(comparison_tab, text="Strategy Comparison")
        
        self.comparison_figure = plt.Figure(figsize=(10, 6), dpi=100)
        self.comparison_canvas = FigureCanvasTkAgg(self.comparison_figure, comparison_tab)
        self.comparison_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Setup empty backtest charts
        self.setup_empty_backtest_charts()
        
        # Status info
        self.backtest_status_var = tk.StringVar(value="Ready to run backtest")
        ttk.Label(self.tab_backtest, textvariable=self.backtest_status_var, style='Status.TLabel').pack(fill='x', padx=10, pady=5)
    
    def create_live_trading_tab(self):
        """Create the live trading tab"""
        # TODO: Implement live trading interface
        warning_label = ttk.Label(
            self.tab_live,
            text="Live Trading is Premium Functionality\n\nThis feature will be available in the full version.",
            font=('Helvetica', 14, 'bold'),
            foreground='gray'
        )
        warning_label.pack(expand=True)
    
    def setup_empty_charts(self):
        """Initialize empty charts for the dashboard"""
        # Clear the figure
        self.dashboard_figure.clear()
        
        # Create a subplot for the price chart
        ax = self.dashboard_figure.add_subplot(111)
        ax.set_title('Price Data & Predictions (No Data Loaded)')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.grid(True, alpha=0.3)
        
        # Add a message when no data is available
        ax.text(
            0.5, 0.5,
            'Load data to see price chart and predictions',
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes,
            fontsize=14
        )
        
        self.dashboard_figure.tight_layout()
        self.price_chart_canvas.draw()
    
    def setup_empty_backtest_charts(self):
        """Initialize empty charts for backtesting"""
        # Equity curve
        self.equity_figure.clear()
        ax1 = self.equity_figure.add_subplot(111)
        ax1.set_title('Equity Curve (No Backtest Run)')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.grid(True, alpha=0.3)
        ax1.text(
            0.5, 0.5,
            'Run a backtest to see results',
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax1.transAxes,
            fontsize=14
        )
        self.equity_figure.tight_layout()
        self.equity_canvas.draw()
        
        # Comparison chart
        self.comparison_figure.clear()
        ax2 = self.comparison_figure.add_subplot(111)
        ax2.set_title('Strategy Comparison (No Backtest Run)')
        ax2.set_xlabel('Strategy')
        ax2.set_ylabel('Return (%)')
        ax2.grid(True, alpha=0.3)
        ax2.text(
            0.5, 0.5,
            'Run multiple backtests to see comparison',
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax2.transAxes,
            fontsize=14
        )
        self.comparison_figure.tight_layout()
        self.comparison_canvas.draw()
    
    def load_data(self):
        """Load historical price data from a file"""
        try:
            filename = askopenfilename(
                title="Load Historical Data",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            
            if not filename:  # User canceled
                return
                
            self.current_data_path = filename
            self.historical_data = pd.read_csv(filename, parse_dates=['date'])
            
            # Set date as index if it isn't already
            if 'date' in self.historical_data.columns:
                self.historical_data.set_index('date', inplace=True)
                
            self.status_message(f"Loaded {len(self.historical_data)} data points from {os.path.basename(filename)}")
            self.log_activity(f"Loaded historical data: {os.path.basename(filename)}")
            
            # Update dashboard charts
            self.update_price_chart()
            
            # Make ML tab aware of the data
            if hasattr(self.ml_dashboard_panel, 'refresh_predictions') and self.ml_predictor:
                self.ml_dashboard_panel.ml_predictor = self.ml_predictor
                self.ml_dashboard_panel.refresh_predictions()
                
            return True
            
        except Exception as e:
            messagebox.showerror("Data Loading Error", f"Error loading data: {str(e)}")
            self.status_message(f"Error loading data: {str(e)}", is_error=True)
            return False
    
    def generate_sample_data(self):
        """Generate sample price data for testing"""
        try:
            symbol = self.symbol_var.get() or "BTC/USDT"
            days = self.days_var.get() or 180
            
            self.status_message(f"Generating {days} days of sample data for {symbol}...")
            
            # Generate dates
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=days)
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Generate prices with a random walk
            np.random.seed(42)  # For reproducibility
            
            # Determine base price based on symbol
            base_price = 100
            if "BTC" in symbol:
                base_price = 20000
            elif "ETH" in symbol:
                base_price = 1000
                
            # Create random price movements
            price_changes = np.random.normal(0, 0.02, len(dates)).cumsum()
            prices = base_price * (1 + price_changes)
            
            # Create DataFrame with OHLCV data
            self.historical_data = pd.DataFrame({
                'open': prices * (1 + np.random.normal(0, 0.005, len(dates))),
                'high': prices * (1 + np.abs(np.random.normal(0, 0.01, len(dates)))),
                'low': prices * (1 - np.abs(np.random.normal(0, 0.01, len(dates)))),
                'close': prices,
                'volume': np.random.normal(1000000, 200000, len(dates)) * prices / base_price,
                'symbol': symbol
            }, index=dates)
            
            # Ensure high is higher than other prices, low is lower
            self.historical_data['high'] = np.maximum(
                np.maximum(self.historical_data['high'], self.historical_data['open']), 
                self.historical_data['close']
            )
            self.historical_data['low'] = np.minimum(
                np.minimum(self.historical_data['low'], self.historical_data['open']), 
                self.historical_data['close']
            )
            
            self.status_message(f"Generated {len(self.historical_data)} days of sample data for {symbol}")
            self.log_activity(f"Generated sample data for {symbol}")
            
            # Update dashboard charts
            self.update_price_chart()
            
            return True
            
        except Exception as e:
            messagebox.showerror("Data Generation Error", f"Error generating sample data: {str(e)}")
            self.status_message(f"Error generating sample data: {str(e)}", is_error=True)
            return False
    
    def update_price_chart(self):
        """Update the price chart with current data"""
        if self.historical_data is None or len(self.historical_data) == 0:
            self.setup_empty_charts()
            return
            
        # Clear the figure
        self.dashboard_figure.clear()
        
        # Create subplot for price chart
        ax = self.dashboard_figure.add_subplot(111)
        
        # Plot price
        ax.plot(
            self.historical_data.index,
            self.historical_data['close'],
            label='Close Price',
            color='blue',
            alpha=0.7
        )
        
        # Add ML predictions if available
        if self.ml_predictor is not None:
            try:
                # Get predictions for the last portion of data
                window_size = min(30, len(self.historical_data))
                recent_data = self.historical_data.tail(window_size)
                
                # Make prediction for each point with forecasting
                predictions = []
                prediction_dates = []
                
                for i in range(max(0, len(self.historical_data) - window_size), len(self.historical_data)):
                    data_slice = self.historical_data.iloc[:i]
                    if len(data_slice) > 20:  # Minimum data needed
                        pred = self.ml_predictor.predict(data_slice)
                        last_price = self.historical_data.iloc[i-1]['close']
            except Exception as e:
                print(f"Error in ML prediction: {e}")
        
        self.dashboard_figure.tight_layout()
        self.price_chart_canvas.draw()
    
    def run_standard_backtest(self):
        """Run a standard backtest using the selected strategy"""
        if self.historical_data is None or len(self.historical_data) == 0:
            messagebox.showwarning("No Data", "Please load historical data before running a backtest.")
            return
        
        try:
            self.status_message("Running standard backtest...")
            self.backtest_status_var.set("Running standard backtest...")
            
            # Extract backtest parameters
            days = self.backtest_days_var.get()
            symbol = self.backtest_pair_var.get()
            strategy = self.backtest_strategy_var.get()
            initial_capital = self.backtest_capital_var.get()
            
            # Prepare data for backtest
            end_date = self.historical_data.index[-1]
            start_date = end_date - datetime.timedelta(days=days)
            backtest_data = self.historical_data.loc[start_date:end_date]
            
            # Run backtest in a separate thread
            self.backtesting_thread = threading.Thread(
                target=self._run_backtest_thread,
                args=(backtest_data, symbol, strategy, initial_capital, False)
            )
            self.backtesting_thread.start()
            
        except Exception as e:
            messagebox.showerror("Backtest Error", f"Error running standard backtest: {str(e)}")
            self.status_message(f"Error running standard backtest: {str(e)}", is_error=True)
            self.backtest_status_var.set("Error running standard backtest")
    
    def run_ml_backtest(self):
        """Run a backtest using the ML model"""
        if self.historical_data is None or len(self.historical_data) == 0:
            messagebox.showwarning("No Data", "Please load historical data before running a backtest.")
            return
        
        if self.ml_predictor is None:
            messagebox.showwarning("No Model", "Please load or train an ML model before running an ML backtest.")
            return
        
        try:
            self.status_message("Running ML backtest...")
            self.backtest_status_var.set("Running ML backtest...")
            
            # Extract backtest parameters
            days = self.backtest_days_var.get()
            symbol = self.backtest_pair_var.get()
            strategy = self.backtest_strategy_var.get()
            initial_capital = self.backtest_capital_var.get()
            ml_weight = self.backtest_ml_weight_var.get() / 100.0
            
            # Prepare data for backtest
            end_date = self.historical_data.index[-1]
            start_date = end_date - datetime.timedelta(days=days)
            backtest_data = self.historical_data.loc[start_date:end_date]
            
            # Run backtest in a separate thread
            self.backtesting_thread = threading.Thread(
                target=self._run_backtest_thread,
                args=(backtest_data, symbol, strategy, initial_capital, True, ml_weight)
            )
            self.backtesting_thread.start()
            
        except Exception as e:
            messagebox.showerror("Backtest Error", f"Error running ML backtest: {str(e)}")
            self.status_message(f"Error running ML backtest: {str(e)}", is_error=True)
            self.backtest_status_var.set("Error running ML backtest")
    
    def _run_backtest_thread(self, data, symbol, strategy, initial_capital, use_ml, ml_weight=0.5):
        """Threaded function to run the backtest"""
        try:
            # Initialize backtest runner
            self.backtest_runner = BacktestRunner(
                data=data,
                symbol=symbol,
                strategy=strategy,
                initial_capital=initial_capital,
                use_ml=use_ml,
                ml_weight=ml_weight,
                ml_predictor=self.ml_predictor
            )
            
            # Run backtest
            results = self.backtest_runner.run_backtest()
            
            # Update UI with results
            self.after(0, self._update_backtest_results, results)
            
        except Exception as e:
            self.after(0, self._handle_backtest_error, str(e))
    
    def _update_backtest_results(self, results):
        """Update the UI with backtest results"""
        try:
            # Update equity curve
            self.equity_figure.clear()
            ax1 = self.equity_figure.add_subplot(111)
            ax1.plot(results['equity_curve'].index, results['equity_curve']['portfolio_value'], label='Equity Curve')
            ax1.set_title('Equity Curve')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Portfolio Value ($)')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            self.equity_figure.tight_layout()
            self.equity_canvas.draw()
            
            # Update strategy comparison
            if self.backtest_compare_var.get():
                self.comparison_figure.clear()
                ax2 = self.comparison_figure.add_subplot(111)
                strategies = results['strategy_comparison'].index
                returns = results['strategy_comparison']['return']
                ax2.bar(strategies, returns, color=['blue', 'green', 'red'])
                ax2.set_title('Strategy Comparison')
                ax2.set_xlabel('Strategy')
                ax2.set_ylabel('Return (%)')
                ax2.grid(True, alpha=0.3)
                self.comparison_figure.tight_layout()
                self.comparison_canvas.draw()
            
            # Update status
            self.status_message("Backtest completed successfully")
            self.backtest_status_var.set("Backtest completed successfully")
            self.log_activity("Backtest completed successfully")
            
        except Exception as e:
            self._handle_backtest_error(str(e))
    
    def _handle_backtest_error(self, error_message):
        """Handle errors during backtest"""
        messagebox.showerror("Backtest Error", f"Error during backtest: {error_message}")
        self.status_message(f"Error during backtest: {error_message}", is_error=True)
        self.backtest_status_var.set("Error during backtest")
    
    def generate_backtest_report(self):
        """Generate a report of the backtest results"""
        if self.backtest_runner is None or self.backtest_runner.results is None:
            messagebox.showwarning("No Results", "Please run a backtest before generating a report.")
            return
        
        try:
            self.status_message("Generating backtest report...")
            report_path = self.backtest_runner.generate_report()
            self.status_message(f"Backtest report saved to {report_path}")
            self.log_activity(f"Backtest report saved to {report_path}")
            
        except Exception as e:
            messagebox.showerror("Report Error", f"Error generating backtest report: {str(e)}")
            self.status_message(f"Error generating backtest report: {str(e)}", is_error=True)
    
    def load_model(self):
        """Load a pre-trained ML model from a file"""
        try:
            filename = askopenfilename(
                title="Load ML Model",
                filetypes=[("Model Files", "*.pkl"), ("All Files", "*.*")]
            )
            
            if not filename:  # User canceled
                return
                
            self.current_model_path = filename
            self.ml_predictor = MLPricePredictor.load_model(filename)
            
            self.status_message(f"Loaded ML model from {os.path.basename(filename)}")
            self.log_activity(f"Loaded ML model: {os.path.basename(filename)}")
            
            # Update dashboard
            self.metric_vars['ml_status'].set("Loaded")
            
            # Make ML tab aware of the model
            if hasattr(self.ml_dashboard_panel, 'refresh_predictions'):
                self.ml_dashboard_panel.ml_predictor = self.ml_predictor
                self.ml_dashboard_panel.refresh_predictions()
                
            return True
            
        except Exception as e:
            messagebox.showerror("Model Loading Error", f"Error loading model: {str(e)}")
            self.status_message(f"Error loading model: {str(e)}", is_error=True)
            return False
    
    def train_model(self):
        """Train a new ML model using the loaded data"""
        if self.historical_data is None or len(self.historical_data) == 0:
            messagebox.showwarning("No Data", "Please load historical data before training a model.")
            return
        
        try:
            self.status_message("Training ML model...")
            
            # Extract training parameters
            model_type = self.model_type_var.get()
            prediction_window = self.prediction_window_var.get()
            
            # Initialize and train the model
            self.ml_predictor = MLPricePredictor(model_type=model_type, prediction_window=prediction_window)
            self.ml_predictor.train(self.historical_data)
            
            self.status_message("ML model trained successfully")
            self.log_activity("ML model trained successfully")
            
            # Update dashboard
            self.metric_vars['ml_status'].set("Trained")
            
            # Make ML tab aware of the model
            if hasattr(self.ml_dashboard_panel, 'refresh_predictions'):
                self.ml_dashboard_panel.ml_predictor = self.ml_predictor
                self.ml_dashboard_panel.refresh_predictions()
                
            return True
            
        except Exception as e:
            messagebox.showerror("Model Training Error", f"Error training model: {str(e)}")
            self.status_message(f"Error training model: {str(e)}", is_error=True)
            return False
    
    def save_model(self):
        """Save the trained ML model to a file"""
        if self.ml_predictor is None:
            messagebox.showwarning("No Model", "Please train or load an ML model before saving.")
            return
        
        try:
            filename = askdirectory(title="Save ML Model")
            
            if not filename:  # User canceled
                return
                
            self.ml_predictor.save_model(filename)
            
            self.status_message(f"Saved ML model to {filename}")
            self.log_activity(f"Saved ML model: {filename}")
            
            return True
            
        except Exception as e:
            messagebox.showerror("Model Saving Error", f"Error saving model: {str(e)}")
            self.status_message(f"Error saving model: {str(e)}", is_error=True)
            return False
    
    def status_message(self, message, is_error=False):
        """Update the status bar with a message"""
        self.status_bar.config(text=message, foreground='red' if is_error else 'black')
    
    def log_activity(self, message):
        """Log activity to the activity log"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
    
    def show_documentation(self):
        """Show the documentation for the application"""
        messagebox.showinfo("Documentation", "Documentation is available at: https://github.com/your-repo/BROski-Bot")
    
    def show_about(self):
        """Show the about dialog"""
        messagebox.showinfo("About", "BROski Bot 3.0 - ML Trading Dashboard\n\nDeveloped by Your Name")

if __name__ == "__main__":
    app = MLTradingDashboard()
    app.mainloop()
