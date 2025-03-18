#!/usr/bin/env python
"""
BROski Bot 3.0 - Ultra Hub
Unified control center with Iron Man UI and integrated components
"""
import os
import sys
import subprocess
import threading
import time
import json
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path

# Determine if we're in a virtual environment
IN_VENV = sys.prefix != sys.base_prefix

# Set up path handling
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(ROOT_DIR, "ui")
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

# Ensure directories exist
os.makedirs(UI_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# Colors (Iron Man theme)
COLORS = {
    "bg_dark": "#0d1117",
    "primary": "#0abdc6",  # Cyan blue
    "secondary": "#ea580c",  # Burnt orange
    "accent": "#ff5722",    # Bright orange
    "text_light": "#ffffff",
    "text_dark": "#cccccc",
}

class BroskiUltraHub:
    """Unified Control Hub for BROski Bot 3.0"""
    
    def __init__(self, root):
        """Initialize the Ultra Hub interface"""
        self.root = root
        self.root.title("BROski Ultra Hub - Mark VI")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        self.root.configure(bg=COLORS["bg_dark"])
        
        # Set the icon
        try:
            icon_path = os.path.join(ASSETS_DIR, "broski_logo.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass  # Icon not critical
            
        # Track running processes
        self.running_processes = {}
        
        # Load config
        self.config = self.load_config()
        
        # System status
        self.system_status = {
            "dashboard_running": False,
            "bot_running": False,
            "monitor_running": False,
            "last_trade": None,
            "api_connected": False
        }
        
        # Create UI
        self.create_ui()
        
        # Start status updater thread
        self.stop_event = threading.Event()
        self.status_thread = threading.Thread(target=self.update_status_loop)
        self.status_thread.daemon = True
        self.status_thread.start()
        
    def load_config(self):
        """Load configuration from file"""
        config_file = os.path.join(CONFIG_DIR, "config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                
        # Return default config if loading fails
        return {
            "version": "3.0.0",
            "exchange": {"name": "mexc", "sandbox_mode": False},
            "trading": {
                "base_symbol": "PI",
                "quote_symbol": "USDT",
                "trade_amount": 15.0,
                "auto_trade": False,
            },
            "strategies": {
                "active_strategy": "hyperfocus_strategy"
            },
            "advanced": {
                "websocket_enabled": True,
                "multi_timeframe_analysis": True
            }
        }
    
    def create_ui(self):
        """Create the main UI components"""
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=COLORS["bg_dark"])
        self.style.configure('TLabel', background=COLORS["bg_dark"], foreground=COLORS["text_light"])
        self.style.configure('TButton', 
                             background=COLORS["primary"], 
                             foreground=COLORS["bg_dark"],
                             borderwidth=0,
                             focusthickness=3,
                             focuscolor=COLORS["accent"])
        self.style.map('TButton', 
                      background=[('active', COLORS["accent"])],
                      foreground=[('active', COLORS["text_light"])])
                      
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with logo
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Try to load and display the logo
        try:
            logo_path = os.path.join(ASSETS_DIR, "broski_logo.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((80, 80), Image.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = ttk.Label(self.header_frame, image=logo_photo, background=COLORS["bg_dark"])
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack(side=tk.LEFT, padx=10)
            
            # Title next to logo
            title_frame = ttk.Frame(self.header_frame)
            title_frame.pack(side=tk.LEFT, padx=10)
            
            title_label = ttk.Label(title_frame, 
                                   text="BROski Ultra Hub", 
                                   font=("Helvetica", 24, "bold"),
                                   foreground=COLORS["primary"])
            title_label.pack(anchor=tk.W)
            
            subtitle_label = ttk.Label(title_frame,
                                      text="STARK INDUSTRIES TRADING TECHNOLOGY",
                                      font=("Helvetica", 10),
                                      foreground=COLORS["text_dark"])
            subtitle_label.pack(anchor=tk.W)
        except Exception as e:
            # Fallback to text-only header
            title_label = ttk.Label(self.header_frame, 
                                   text="BROski Ultra Hub", 
                                   font=("Helvetica", 24, "bold"),
                                   foreground=COLORS["primary"])
            title_label.pack(side=tk.LEFT, padx=10)
        
        # Status indicators in header
        self.status_frame = ttk.Frame(self.header_frame)
        self.status_frame.pack(side=tk.RIGHT, padx=10)
        
        # API status indicator
        self.api_status_var = tk.StringVar(value="API: Not Connected")
        api_status = ttk.Label(self.status_frame, textvariable=self.api_status_var)
        api_status.pack(anchor=tk.E)
        
        # Bot status indicator
        self.bot_status_var = tk.StringVar(value="Bot: Stopped")
        bot_status = ttk.Label(self.status_frame, textvariable=self.bot_status_var)
        bot_status.pack(anchor=tk.E)
        
        # Time indicator
        self.time_var = tk.StringVar()
        time_label = ttk.Label(self.status_frame, textvariable=self.time_var)
        time_label.pack(anchor=tk.E)
        
        # Main content - tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_launch_tab()
        self.create_config_tab()
        self.create_monitor_tab()
        self.create_help_tab()
        
        # Footer
        footer = ttk.Label(self.main_frame, 
                          text="BROski Bot 3.1.0 - Multi-Exchange Support · AI Enhanced",
                          foreground=COLORS["text_dark"])
        footer.pack(side=tk.BOTTOM, pady=10)
        
        # Update the time display
        self.update_time()
    
    def create_launch_tab(self):
        """Create the launch tab with component launchers"""
        launch_frame = ttk.Frame(self.notebook)
        self.notebook.add(launch_frame, text=" Launch Center ")
        
        # Grid layout for launch buttons
        launch_frame.columnconfigure(0, weight=1)
        launch_frame.columnconfigure(1, weight=1)
        
        # Section 1: Dashboards
        section_label = ttk.Label(launch_frame, text="DASHBOARDS", 
                                 font=("Helvetica", 12, "bold"),
                                 foreground=COLORS["primary"])
        section_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))
        
        # Dashboard buttons
        self.create_launch_button(launch_frame, 
                                 "Iron Man Dashboard", 
                                 "Launch the advanced Iron Man themed trading dashboard",
                                 lambda: self.launch_component("ironman_dashboard"),
                                 row=1, column=0)
        
        self.create_launch_button(launch_frame, 
                                 "Simple Dashboard", 
                                 "Launch a lightweight trading dashboard",
                                 lambda: self.launch_component("launch_simple_hub"),
                                 row=1, column=1)
        
        # Section 2: Trading Bots
        section_label = ttk.Label(launch_frame, text="TRADING BOTS", 
                                 font=("Helvetica", 12, "bold"),
                                 foreground=COLORS["primary"])
        section_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))
        
        # Bot buttons
        self.create_launch_button(launch_frame, 
                                 "Direct Trader", 
                                 "Launch the direct trading bot without UI",
                                 lambda: self.launch_component("direct_trader"),
                                 row=3, column=0)
        
        self.create_launch_button(launch_frame, 
                                 "Brain Hub", 
                                 "Launch the AI-enhanced trading brain",
                                 lambda: self.launch_component("launch_brain_hub"),
                                 row=3, column=1)
        
        # Section 3: Tools
        section_label = ttk.Label(launch_frame, text="TOOLS", 
                                 font=("Helvetica", 12, "bold"),
                                 foreground=COLORS["primary"])
        section_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))
        
        # Tool buttons
        self.create_launch_button(launch_frame, 
                                 "Bot Monitor", 
                                 "Launch the enhanced bot monitoring interface",
                                 lambda: self.launch_component("bot_monitor_enhanced"),
                                 row=5, column=0)
        
        self.create_launch_button(launch_frame, 
                                 "Run Backtest", 
                                 "Run strategy backtests with performance analysis",
                                 lambda: self.launch_component("run_backtest"),
                                 row=5, column=1)
        
        self.create_launch_button(launch_frame, 
                                 "Setup Wizard", 
                                 "Configure BROski Bot with the interactive wizard",
                                 self.run_setup_wizard,  # Use our internal method instead of launching external script
                                 row=6, column=0)
        
        self.create_launch_button(launch_frame, 
                                 "System Check", 
                                 "Run a diagnostic check on the BROski system",
                                 self.run_system_check,  # Use our internal method instead of launching external script
                                 row=6, column=1)
        
        # Kill all processes button
        kill_frame = ttk.Frame(launch_frame)
        kill_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=20, sticky="ew")
        
        kill_btn = ttk.Button(kill_frame, 
                             text="⚠️ EMERGENCY STOP - KILL ALL PROCESSES", 
                             command=self.kill_all_processes)
        kill_btn.pack(fill=tk.X, pady=10)
    
    def create_config_tab(self):
        """Create the configuration tab"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text=" Configuration ")
        
        # Quick config panel
        config_frame.columnconfigure(0, weight=1)
        config_frame.columnconfigure(1, weight=1)
        
        # Trading pair section
        section_label = ttk.Label(config_frame, text="TRADING SETTINGS", 
                                 font=("Helvetica", 12, "bold"),
                                 foreground=COLORS["primary"])
        section_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))
        
        # Trading pair
        pair_frame = ttk.Frame(config_frame)
        pair_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        pair_label = ttk.Label(pair_frame, text="Trading Pair:")
        pair_label.pack(side=tk.LEFT)
        
        self.base_var = tk.StringVar(value=self.config["trading"]["base_symbol"])
        base_entry = ttk.Entry(pair_frame, width=5, textvariable=self.base_var)
        base_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        separator = ttk.Label(pair_frame, text="/")
        separator.pack(side=tk.LEFT)
        
        self.quote_var = tk.StringVar(value=self.config["trading"]["quote_symbol"])
        quote_entry = ttk.Entry(pair_frame, width=5, textvariable=self.quote_var)
        quote_entry.pack(side=tk.LEFT)
        
        # Trade amount
        amount_frame = ttk.Frame(config_frame)
        amount_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        amount_label = ttk.Label(amount_frame, text="Trade Amount:")
        amount_label.pack(side=tk.LEFT)
        
        self.amount_var = tk.DoubleVar(value=self.config["trading"]["trade_amount"])
        amount_entry = ttk.Entry(amount_frame, width=8, textvariable=self.amount_var)
        amount_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Strategy section
        section_label = ttk.Label(config_frame, text="STRATEGY SETTINGS", 
                                 font=("Helvetica", 12, "bold"),
                                 foreground=COLORS["primary"])
        section_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))
        
        # Strategy selector
        strategy_frame = ttk.Frame(config_frame)
        strategy_frame.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        strategy_label = ttk.Label(strategy_frame, text="Active Strategy:")
        strategy_label.pack(side=tk.LEFT)
        
        self.strategy_var = tk.StringVar(value=self.config["strategies"]["active_strategy"])
        strategies = ["hyperfocus_strategy", "rsi_strategy", "macd_strategy", "ml_strategy"]
        strategy_dropdown = ttk.Combobox(strategy_frame, textvariable=self.strategy_var, values=strategies, width=20)
        strategy_dropdown.pack(side=tk.LEFT, padx=(10, 0))
        
        # Auto trade toggle
        autotrade_frame = ttk.Frame(config_frame)
        autotrade_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        autotrade_label = ttk.Label(autotrade_frame, text="Auto Trading:")
        autotrade_label.pack(side=tk.LEFT)
        
        self.autotrade_var = tk.BooleanVar(value=self.config["trading"]["auto_trade"])
        autotrade_check = ttk.Checkbutton(autotrade_frame, variable=self.autotrade_var)
        autotrade_check.pack(side=tk.LEFT, padx=(10, 0))
        
        # Save button
        save_btn = ttk.Button(config_frame, text="Save Configuration", 
                             command=self.save_config)
        save_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=20)
        
        # API Key management section
        section_label = ttk.Label(config_frame, text="API KEYS", 
                                 font=("Helvetica", 12, "bold"),
                                 foreground=COLORS["primary"])
        section_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))
        
        # Change this button to use the internal wizard instead of external script
        api_btn = ttk.Button(config_frame, text="Launch API Key Wizard", 
                            command=self.run_setup_wizard)  # Changed from lambda: self.launch_component("wizard")
        api_btn.grid(row=6, column=0, columnspan=2, padx=10, pady=5)
        
        # API Key status
        key_status_label = ttk.Label(config_frame, 
                                    text="Use the wizard to securely store your API keys",
                                    foreground=COLORS["text_dark"])
        key_status_label.grid(row=7, column=0, columnspan=2, padx=10, pady=5)
    
    def create_monitor_tab(self):
        """Create the monitoring tab"""
        monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitor_frame, text=" Monitoring ")
        
        # Monitoring display
        monitor_frame.columnconfigure(0, weight=1)
        
        # Status overview section
        section_label = ttk.Label(monitor_frame, text="SYSTEM STATUS", 
                                 font=("Helvetica", 12, "bold"),
                                 foreground=COLORS["primary"])
        section_label.grid(row=0, column=0, sticky="w", padx=10, pady=(20, 10))
        
        # Status indicators
        status_frame = ttk.Frame(monitor_frame)
        status_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Create indicators for different components
        self.component_status = {
            "api": {"label": "API Connection", "var": tk.StringVar(value="Disconnected")},
            "dashboard": {"label": "Dashboard", "var": tk.StringVar(value="Stopped")},
            "bot": {"label": "Trading Bot", "var": tk.StringVar(value="Inactive")},
            "websocket": {"label": "WebSocket", "var": tk.StringVar(value="Disconnected")},
        }
        
        # Create status display
        row = 0
        for key, data in self.component_status.items():
            frame = ttk.Frame(status_frame)
            frame.grid(row=row, column=0, sticky="ew", pady=5)
            
            label = ttk.Label(frame, text=f"{data['label']}:", width=15)
            label.pack(side=tk.LEFT)
            
            status = ttk.Label(frame, textvariable=data["var"], width=20)
            status.pack(side=tk.LEFT)
            
            row += 1
        
        # Recent activity section
        section_label = ttk.Label(monitor_frame, text="RECENT ACTIVITY", 
                                 font=("Helvetica", 12, "bold"),
                                 foreground=COLORS["primary"])
        section_label.grid(row=2, column=0, sticky="w", padx=10, pady=(20, 10))
        
        # Activity log (simulated)
        self.activity_text = tk.Text(monitor_frame, height=12, bg="#1a1a1a", fg="#cccccc",
                                    font=("Courier", 9))
        self.activity_text.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Add some sample activity
        self.activity_text.insert(tk.END, "[INFO] BROski Ultra Hub initialized\n")
        self.activity_text.insert(tk.END, "[INFO] Checking for configuration...\n")
        self.activity_text.insert(tk.END, "[INFO] System ready\n")
        
        # Make the text widget read-only
        self.activity_text.config(state=tk.DISABLED)
        
        # Refresh button
        refresh_btn = ttk.Button(monitor_frame, text="Refresh Status", 
                                command=self.refresh_status)
        refresh_btn.grid(row=4, column=0, padx=10, pady=20)
    
    def create_help_tab(self):
        """Create the help/about tab"""
        help_frame = ttk.Frame(self.notebook)
        self.notebook.add(help_frame, text=" Help & About ")
        
        # About section
        section_label = ttk.Label(help_frame, text="ABOUT BROSKI BOT", 
                                 font=("Helvetica", 12, "bold"),
                                 foreground=COLORS["primary"])
        section_label.grid(row=0, column=0, sticky="w", padx=10, pady=(20, 10))
        
        # About text
        about_text = """BROski Bot 3.0 is an advanced cryptocurrency trading system.

Key Features:
• Multi-exchange API support with secure key management
• Real-time data streaming via WebSockets
• Advanced trading strategies including AI/ML models
• Backtesting and performance analysis
• Iron Man themed UI with real-time monitoring

This Ultra Hub brings together all BROski components into a unified control center.
"""
        about_label = ttk.Label(help_frame, text=about_text, justify=tk.LEFT, wraplength=600)
        about_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        # Documentation section
        section_label = ttk.Label(help_frame, text="DOCUMENTATION", 
                                 font=("Helvetica", 12, "bold"),
                                 foreground=COLORS["primary"])
        section_label.grid(row=2, column=0, sticky="w", padx=10, pady=(20, 10))
        
        # Documentation buttons
        docs_frame = ttk.Frame(help_frame)
        docs_frame.grid(row=3, column=0, padx=10, pady=5)
        
        # Quick Start button
        quickstart_btn = ttk.Button(docs_frame, text="Quick Start Guide", 
                                   command=lambda: self.open_documentation("LAUNCHER_GUIDE.md"))
        quickstart_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Project Structure button
        structure_btn = ttk.Button(docs_frame, text="Project Structure", 
                                  command=lambda: self.open_documentation("PROJECT_STRUCTURE.md"))
        structure_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Version info
        version_label = ttk.Label(help_frame, 
                                 text="BROski Bot 3.1.0 - Developed by STARK INDUSTRIES",
                                 foreground=COLORS["text_dark"])
        version_label.grid(row=4, column=0, padx=10, pady=(50, 10))
    
    def create_launch_button(self, parent, title, description, command, row, column):
        """Create a standardized launch button with description"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        
        btn = ttk.Button(frame, text=title, command=command)
        btn.pack(fill=tk.X, pady=(0, 5))
        
        desc = ttk.Label(frame, text=description, wraplength=250,
                        foreground=COLORS["text_dark"])
        desc.pack(fill=tk.X)
        
        return frame
    
    def launch_component(self, component_name):
        """Launch a specific component"""
        component_paths = {
            "ironman_dashboard": os.path.join(UI_DIR, "ironman_dashboard.py"),
            "launch_simple_hub": os.path.join(ROOT_DIR, "launch_simple_hub.py"),
            "direct_trader": os.path.join(ROOT_DIR, "direct_trader.py"),
            "launch_brain_hub": os.path.join(ROOT_DIR, "launch_brain_hub.py"),
            "bot_monitor_enhanced": os.path.join(ROOT_DIR, "bot_monitor_enhanced.py"),
            "run_backtest": os.path.join(ROOT_DIR, "run_backtest.py"),
            "wizard": os.path.join(ROOT_DIR, "python", "wizard.py"),
            "check_system": os.path.join(ROOT_DIR, "check_system.py")
        }
        
        if component_name not in component_paths:
            messagebox.showerror("Error", f"Component {component_name} not found")
            return
            
        path = component_paths[component_name]
        
        # Check if file exists
        if not os.path.exists(path):
            messagebox.showerror("Error", f"File not found: {path}")
            return
        
        # Launch the component
        try:
            # Use sys.executable to ensure we use the same Python interpreter
            process = subprocess.Popen([sys.executable, path])
            
            # Store the process
            self.running_processes[component_name] = {
                "process": process,
                "started": datetime.now()
            }
            
            # Update status
            self.log_activity(f"Launched {component_name}")
            
            # Update specific status indicators
            if component_name == "ironman_dashboard":
                self.component_status["dashboard"]["var"].set("Running")
            elif component_name in ["direct_trader", "launch_brain_hub"]:
                self.component_status["bot"]["var"].set("Active")
                
        except Exception as e:
            messagebox.showerror("Launch Error", str(e))
    
    def kill_all_processes(self):
        """Kill all running processes"""
        if not self.running_processes:
            messagebox.showinfo("Info", "No processes running")
            return
            
        confirm = messagebox.askyesno("Confirm", 
                                     "Are you sure you want to kill all running processes?")
        if not confirm:
            return
            
        for name, data in list(self.running_processes.items()):
            try:
                data["process"].terminate()
                self.log_activity(f"Terminated {name}")
            except Exception as e:
                self.log_activity(f"Error terminating {name}: {e}")
        
        # Clear the processes list
        self.running_processes.clear()
        
        # Update status indicators
        for component in self.component_status.values():
            if component["label"] not in ["API Connection", "WebSocket"]:
                component["var"].set("Stopped")
    
    def save_config(self):
        """Save the configuration"""
        try:
            # Update config from UI values
            self.config["trading"]["base_symbol"] = self.base_var.get()
            self.config["trading"]["quote_symbol"] = self.quote_var.get()
            self.config["trading"]["trade_amount"] = self.amount_var.get()
            self.config["strategies"]["active_strategy"] = self.strategy_var.get()
            self.config["trading"]["auto_trade"] = self.autotrade_var.get()
            
            # Save to file
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(os.path.join(CONFIG_DIR, "config.json"), 'w') as f:
                json.dump(self.config, f, indent=2)
                
            messagebox.showinfo("Success", "Configuration saved successfully")
            self.log_activity("Configuration saved")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def open_documentation(self, doc_name):
        """Open a documentation file"""
        doc_path = os.path.join(ROOT_DIR, "docs", doc_name)
        
        if not os.path.exists(doc_path):
            messagebox.showerror("Error", f"Documentation file not found: {doc_path}")
            return
            
        # On Windows, use the default text editor
        if sys.platform == 'win32':
            os.startfile(doc_path)
        # On macOS, use open
        elif sys.platform == 'darwin':
            subprocess.call(['open', doc_path])
        # On Linux, use xdg-open
        else:
            subprocess.call(['xdg-open', doc_path])
    
    def refresh_status(self):
        """Manually refresh the status display"""
        # Check processes
        for name, data in list(self.running_processes.items()):
            if data["process"].poll() is not None:  # Process has terminated
                self.log_activity(f"{name} has stopped")
                del self.running_processes[name]
        
        # Update component status based on running processes
        self.component_status["dashboard"]["var"].set(
            "Running" if any(k in ["ironman_dashboard", "launch_simple_hub"] for k in self.running_processes) else "Stopped"
        )
        self.component_status["bot"]["var"].set(
            "Active" if any(k in ["direct_trader", "launch_brain_hub"] for k in self.running_processes) else "Inactive"
        )
    
    def update_status_loop(self):
        """Continuously update the status indicators"""
        while not self.stop_event.is_set():
            # Check for running processes and update component status
            self.refresh_status()
            
            # Check API connection by attempting to read config
            try:
                # Try to detect if API is connected (simple check of config file existence for now)
                if os.path.exists(os.path.join(CONFIG_DIR, "config.json")):
                    api_status = "Connected"
                else:
                    api_status = "Not Connected"
                self.component_status["api"]["var"].set(api_status)
                
                # Check for websocket connections
                ws_processes = [p for p in self.running_processes.keys() 
                               if p in ["ironman_dashboard", "launch_brain_hub"]]
                if ws_processes:
                    self.component_status["websocket"]["var"].set("Connected")
                else:
                    self.component_status["websocket"]["var"].set("Disconnected")
                
                # Update header status displays
                self.api_status_var.set(f"API: {api_status}")
                
                # Get bot status from component status
                bot_status = self.component_status["bot"]["var"].get()
                self.bot_status_var.set(f"Bot: {bot_status}")
                
            except Exception as e:
                self.log_activity(f"Error updating status: {e}")
                
            time.sleep(5)  # Update every 5 seconds
    
    def on_closing(self):
        """Handle window closing event"""
        if self.running_processes:
            confirm = messagebox.askyesno("Confirm Exit", 
                                         "There are processes still running.\nDo you want to exit anyway?")
            if not confirm:
                return
                
            # Ask if they want to kill all processes
            kill = messagebox.askyesno("Kill Processes", 
                                      "Do you want to kill all running processes before exit?")
            if kill:
                self.kill_all_processes()
        
        # Stop the update thread
        self.stop_event.set()
        if self.status_thread.is_alive():
            self.status_thread.join(timeout=1)
            
        # Clean up and exit
        self.root.destroy()
        sys.exit(0)
    
    def check_environment(self):
        """Check if the environment is properly set up"""
        self.log_activity("Checking environment...")
        
        # Check Python version
        python_version = sys.version.split()[0]
        self.log_activity(f"Python version: {python_version}")
        
        # Check if we're in a virtual environment
        if IN_VENV:
            self.log_activity("Running in virtual environment: Yes")
        else:
            self.log_activity("Running in virtual environment: No")
        
        # Check directory structure
        for dir_name, dir_path in [("Root", ROOT_DIR), ("UI", UI_DIR), ("Config", CONFIG_DIR), ("Assets", ASSETS_DIR)]:
            if os.path.exists(dir_path):
                self.log_activity(f"{dir_name} directory: Found")
            else:
                self.log_activity(f"{dir_name} directory: Not found")
        
        # Check for critical files
        critical_files = {
            "ironman_dashboard.py": os.path.join(UI_DIR, "ironman_dashboard.py"),
            "launch_simple_hub.py": os.path.join(ROOT_DIR, "launch_simple_hub.py"),
            "direct_trader.py": os.path.join(ROOT_DIR, "direct_trader.py"),
            "config.json": os.path.join(CONFIG_DIR, "config.json")
        }
        
        for name, path in critical_files.items():
            if os.path.exists(path):
                self.log_activity(f"File {name}: Found")
            else:
                self.log_activity(f"File {name}: Not found")
        
        self.log_activity("Environment check completed")

    # Add this method to the BroskiUltraHub class
    def update_time(self):
        """Update the time display"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_var.set(f"Time: {now}")
        # Schedule the next update after 1 second
        self.root.after(1000, self.update_time)

    # Add this method to the BroskiUltraHub class
    def log_activity(self, message):
        """Log activity to the activity text widget"""
        try:
            # Enable editing
            self.activity_text.config(state=tk.NORMAL)
            
            # Add timestamp and message
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.activity_text.insert(tk.END, f"[{timestamp}] {message}\n")
            
            # Disable editing again
            self.activity_text.config(state=tk.DISABLED)
            
            # Auto-scroll to the end
            self.activity_text.see(tk.END)
        except Exception as e:
            # If there's an error logging, print to console as fallback
            print(f"Error logging activity: {e}")
            print(f"Message was: {message}")

    def run_system_check(self):
        """Run a comprehensive system check and display the results"""
        self.log_activity("Starting comprehensive system check...")
        
        # Create a new window for results
        check_window = tk.Toplevel(self.root)
        check_window.title("BROski System Check")
        check_window.geometry("600x500")
        check_window.configure(bg=COLORS["bg_dark"])
        
        # Try to set icon
        try:
            icon_path = os.path.join(ASSETS_DIR, "broski_logo.ico")
            if os.path.exists(icon_path):
                check_window.iconbitmap(icon_path)
        except Exception:
            pass
        
        # Create scrollable text area for results
        results_frame = ttk.Frame(check_window)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        results_text = tk.Text(results_frame, bg="#1a1a1a", fg="#cccccc",
                             font=("Courier", 10), wrap=tk.WORD)
        results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(results_frame, command=results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        results_text.config(yscrollcommand=scrollbar.set)
        
        # Function to add a check result
        def add_check(title, status, details=None):
            status_color = "#0abdc6" if status == "PASSED" else "#ea580c"  # Cyan or orange
            results_text.insert(tk.END, f"\n{title}\n", "heading")
            results_text.insert(tk.END, f"Status: ", "normal")
            results_text.insert(tk.END, f"{status}\n", "status")
            if details:
                results_text.insert(tk.END, f"{details}\n", "details")
            results_text.tag_config("heading", font=("Courier", 10, "bold"))
            results_text.tag_config("normal", foreground="#cccccc")
            results_text.tag_config("status", foreground=status_color, font=("Courier", 10, "bold"))
            results_text.tag_config("details", foreground="#aaaaaa")
        
        # Add header
        results_text.insert(tk.END, "BROski Bot System Check Results\n", "title")
        results_text.insert(tk.END, "===============================\n", "title")
        results_text.insert(tk.END, f"Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n", "subtitle")
        results_text.tag_config("title", font=("Courier", 12, "bold"), foreground="#0abdc6")
        results_text.tag_config("subtitle", font=("Courier", 10), foreground="#cccccc")
        
        # Run system checks
        
        # 1. Python Version
        python_version = sys.version.split()[0]
        version_check = "PASSED" if float(python_version.split(".")[:2]) >= 3.6 else "WARNING"
        add_check(
            "Python Version Check", 
            version_check,
            f"Detected Python {python_version} (3.6+ recommended)"
        )
        
        # 2. Virtual Environment
        venv_check = "PASSED" if IN_VENV else "WARNING"
        add_check(
            "Virtual Environment", 
            venv_check,
            "Running in virtual environment" if IN_VENV else "Not running in virtual environment (recommended)"
        )
        
        # 3. Directory Structure
        directories = [
            ("Root", ROOT_DIR),
            ("UI", UI_DIR),
            ("Config", CONFIG_DIR),
            ("Assets", ASSETS_DIR),
            ("Python", os.path.join(ROOT_DIR, "python")),
            ("Utils", os.path.join(ROOT_DIR, "utils")),
            ("Docs", os.path.join(ROOT_DIR, "docs"))
        ]
        
        missing_dirs = []
        for name, path in directories:
            if not os.path.exists(path):
                missing_dirs.append(name)
                
        dir_check = "PASSED" if not missing_dirs else "WARNING"
        add_check(
            "Directory Structure", 
            dir_check,
            f"Missing directories: {', '.join(missing_dirs)}" if missing_dirs else "All required directories found"
        )
        
        # 4. Critical Files
        critical_files = {
            "ironman_dashboard.py": os.path.join(UI_DIR, "ironman_dashboard.py"),
            "config.json": os.path.join(CONFIG_DIR, "config.json"),
            "README.md": os.path.join(ROOT_DIR, "README.md"),
            "broski_ultra_hub.py": os.path.join(ROOT_DIR, "broski_ultra_hub.py")
        }
        
        missing_files = []
        for name, path in critical_files.items():
            if not os.path.exists(path):
                missing_files.append(name)
                
        file_check = "PASSED" if not missing_files else "WARNING"
        add_check(
            "Critical Files", 
            file_check,
            f"Missing files: {', '.join(missing_files)}" if missing_files else "All critical files found"
        )
        
        # 5. Config Validation
        try:
            # Basic config structure check
            config_issues = []
            if "exchange" not in self.config:
                config_issues.append("Missing 'exchange' section")
            if "trading" not in self.config:
                config_issues.append("Missing 'trading' section")
            if "strategies" not in self.config:
                config_issues.append("Missing 'strategies' section")
            
            config_check = "PASSED" if not config_issues else "WARNING"
            add_check(
                "Configuration Check", 
                config_check,
                f"Config issues: {', '.join(config_issues)}" if config_issues else "Configuration structure valid"
            )
        except Exception as e:
            add_check("Configuration Check", "WARNING", f"Error checking config: {str(e)}")
        
        # 6. Required Packages
        recommended_packages = ["PIL", "json", "tkinter", "datetime", "threading"]
        missing_packages = []
        
        try:
            for package in recommended_packages:
                try:
                    __import__(package.lower())
                except ImportError:
                    missing_packages.append(package)
                    
            packages_check = "PASSED" if not missing_packages else "WARNING"
            add_check(
                "Required Packages", 
                packages_check,
                f"Missing packages: {', '.join(missing_packages)}" if missing_packages else "All recommended packages installed"
            )
        except Exception as e:
            add_check("Required Packages", "WARNING", f"Error checking packages: {str(e)}")
        
        # Make text read-only
        results_text.config(state=tk.DISABLED)
        
        # Add close button
        def copy_results():
            check_window.clipboard_clear()
            check_window.clipboard_append(results_text.get(1.0, tk.END))
            messagebox.showinfo("Copied", "Results copied to clipboard")
            
        button_frame = ttk.Frame(check_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        copy_btn = ttk.Button(button_frame, text="Copy Results", command=copy_results)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = ttk.Button(button_frame, text="Close", command=check_window.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Log that we ran the check
        self.log_activity("Comprehensive system check completed")

    def run_setup_wizard(self):
        """Run the setup wizard to configure the BROski Bot"""
        self.log_activity("Starting setup wizard...")
        
        # Create wizard window
        wizard_window = tk.Toplevel(self.root)
        wizard_window.title("BROski Setup Wizard")
        wizard_window.geometry("650x550")
        wizard_window.configure(bg=COLORS["bg_dark"])
        wizard_window.resizable(False, False)
        
        # Try to set icon
        try:
            icon_path = os.path.join(ASSETS_DIR, "broski_logo.ico")
            if os.path.exists(icon_path):
                wizard_window.iconbitmap(icon_path)
        except Exception:
            pass
        
        # Define wizard state variables
        current_step = tk.IntVar(value=1)
        total_steps = 4  # Welcome, Exchange, Trading, Strategy
        
        # Create header frame
        header_frame = ttk.Frame(wizard_window)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        header_title = ttk.Label(header_frame, 
                               text="BROski Bot Setup Wizard",
                               font=("Helvetica", 16, "bold"),
                               foreground=COLORS["primary"])
        header_title.pack(side=tk.LEFT)
        
        # Progress indicator
        progress_frame = ttk.Frame(wizard_window)
        progress_frame.pack(fill=tk.X, padx=20)
        
        progress_text = ttk.Label(progress_frame, 
                                 textvariable=tk.StringVar(value=f"Step {current_step.get()} of {total_steps}"))
        progress_text.pack(side=tk.LEFT)
        
        # Main content area
        content_frame = ttk.Frame(wizard_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Bottom navigation buttons
        nav_frame = ttk.Frame(wizard_window)
        nav_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Initialize step frames
        step_frames = []
        for i in range(total_steps):
            frame = ttk.Frame(content_frame)
            if i == 0:  # First step is visible initially
                frame.pack(fill=tk.BOTH, expand=True)
            step_frames.append(frame)
        
        # Function to navigate between steps
        def go_to_step(step_num):
            # Hide all frames
            for frame in step_frames:
                frame.pack_forget()
            
            # Show current frame
            if 1 <= step_num <= total_steps:
                step_frames[step_num-1].pack(fill=tk.BOTH, expand=True)
                current_step.set(step_num)
                progress_text.config(text=f"Step {step_num} of {total_steps}")
                
                # Update button states
                back_btn.config(state="disabled" if step_num == 1 else "normal")
                
                if step_num == total_steps:
                    next_btn.config(text="Finish")
                else:
                    next_btn.config(text="Next >")
        
        # Handle next button click
        def next_clicked():
            current = current_step.get()
            if current < total_steps:
                go_to_step(current + 1)
            else:
                # Final step - save and close
                save_wizard_settings()
                wizard_window.destroy()
        
        # Handle back button click
        def back_clicked():
            current = current_step.get()
            if current > 1:
                go_to_step(current - 1)
        
        # Navigation buttons
        back_btn = ttk.Button(nav_frame, text="< Back", command=back_clicked)
        back_btn.pack(side=tk.LEFT)
        
        cancel_btn = ttk.Button(nav_frame, text="Cancel", command=wizard_window.destroy)
        cancel_btn.pack(side=tk.RIGHT)
        
        next_btn = ttk.Button(nav_frame, text="Next >", command=next_clicked)
        next_btn.pack(side=tk.RIGHT, padx=10)
        
        # ---- Step 1: Welcome ----
        welcome_frame = step_frames[0]
        
        welcome_title = ttk.Label(welcome_frame, 
                                 text="Welcome to BROski Bot 3.0",
                                 font=("Helvetica", 14, "bold"),
                                 foreground=COLORS["primary"])
        welcome_title.pack(pady=20)
        
        welcome_text = """
        This wizard will guide you through setting up your BROski Bot.
        
        We'll cover:
        • Exchange API configuration
        • Trading settings
        • Strategy selection
        • Notification preferences
        
        You can change these settings later through the Configuration tab.
        
        Click 'Next' to begin.
        """
        
        welcome_msg = ttk.Label(welcome_frame, text=welcome_text, wraplength=550, justify=tk.LEFT)
        welcome_msg.pack(pady=20, anchor=tk.W)
        
        # ---- Step 2: Exchange Settings ----
        exchange_frame = step_frames[1]
        
        exchange_title = ttk.Label(exchange_frame,
                                  text="Exchange Configuration",
                                  font=("Helvetica", 14, "bold"),
                                  foreground=COLORS["primary"])
        exchange_title.pack(pady=20, anchor=tk.W)
        
        # Exchange selector
        exchange_select_frame = ttk.Frame(exchange_frame)
        exchange_select_frame.pack(fill=tk.X, pady=10, anchor=tk.W)
        
        exchange_label = ttk.Label(exchange_select_frame, text="Exchange:")
        exchange_label.pack(side=tk.LEFT)
        
        exchange_var = tk.StringVar(value=self.config.get("exchange", {}).get("name", "mexc"))
        exchanges = ["mexc", "binance", "kucoin", "huobi"]
        exchange_dropdown = ttk.Combobox(exchange_select_frame, textvariable=exchange_var, values=exchanges)
        exchange_dropdown.pack(side=tk.LEFT, padx=(10, 0))
        
        # Sandbox mode
        sandbox_frame = ttk.Frame(exchange_frame)
        sandbox_frame.pack(fill=tk.X, pady=10, anchor=tk.W)
        
        sandbox_var = tk.BooleanVar(value=self.config.get("exchange", {}).get("sandbox_mode", False))
        sandbox_check = ttk.Checkbutton(sandbox_frame, text="Use Sandbox Mode (Test Environment)", variable=sandbox_var)
        sandbox_check.pack(side=tk.LEFT)
        
        # API Key info
        api_info_frame = ttk.Frame(exchange_frame)
        api_info_frame.pack(fill=tk.X, pady=20, anchor=tk.W)
        
        api_info_text = """
        Note: API keys are stored securely and can be configured in the following ways:
        
        1. Using environment variables (most secure):
           export MEXC_API_KEY=your_key
           export MEXC_API_SECRET=your_secret
           
        2. Using the API Key section in the Configuration tab after setup.
        
        For security reasons, this wizard doesn't collect API keys directly.
        """
        
        api_info_label = ttk.Label(api_info_frame, text=api_info_text, wraplength=550, justify=tk.LEFT)
        api_info_label.pack()
        
        # ---- Step 3: Trading Settings ----
        trading_frame = step_frames[2]
        
        trading_title = ttk.Label(trading_frame,
                                 text="Trading Configuration",
                                 font=("Helvetica", 14, "bold"),
                                 foreground=COLORS["primary"])
        trading_title.pack(pady=20, anchor=tk.W)
        
        # Trading pair
        pair_frame = ttk.Frame(trading_frame)
        pair_frame.pack(fill=tk.X, pady=10, anchor=tk.W)
        
        pair_label = ttk.Label(pair_frame, text="Trading Pair:")
        pair_label.pack(side=tk.LEFT)
        
        wizard_base_var = tk.StringVar(value=self.config["trading"]["base_symbol"])
        base_entry = ttk.Entry(pair_frame, width=5, textvariable=wizard_base_var)
        base_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        separator = ttk.Label(pair_frame, text="/")
        separator.pack(side=tk.LEFT)
        
        wizard_quote_var = tk.StringVar(value=self.config["trading"]["quote_symbol"])
        quote_entry = ttk.Entry(pair_frame, width=5, textvariable=wizard_quote_var)
        quote_entry.pack(side=tk.LEFT)
        
        # Trade amount
        amount_frame = ttk.Frame(trading_frame)
        amount_frame.pack(fill=tk.X, pady=10, anchor=tk.W)
        
        amount_label = ttk.Label(amount_frame, text="Trade Amount:")
        amount_label.pack(side=tk.LEFT)
        
        wizard_amount_var = tk.StringVar(value=str(self.config["trading"]["trade_amount"]))
        amount_entry = ttk.Entry(amount_frame, width=10, textvariable=wizard_amount_var)
        amount_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Auto trading
        auto_frame = ttk.Frame(trading_frame)
        auto_frame.pack(fill=tk.X, pady=10, anchor=tk.W)
        
        wizard_auto_var = tk.BooleanVar(value=self.config["trading"]["auto_trade"])
        auto_check = ttk.Checkbutton(auto_frame, 
                                    text="Enable Auto Trading (bot will execute trades automatically)", 
                                    variable=wizard_auto_var)
        auto_check.pack(side=tk.LEFT)
        
        # Warning for auto trading
        if not self.config["trading"]["auto_trade"]:
            warning_frame = ttk.Frame(trading_frame)
            warning_frame.pack(fill=tk.X, pady=10)
            
            warning_text = """
            ⚠️ Auto trading is disabled by default for safety.
            
            When enabled, the bot can place trades using real funds without confirmation.
            Consider starting with signal-only mode to evaluate performance first.
            """
            
            warning_label = ttk.Label(warning_frame, text=warning_text, 
                                     wraplength=550, justify=tk.LEFT, 
                                     foreground=COLORS["secondary"])
            warning_label.pack()
        
        # ---- Step 4: Strategy Settings ----
        strategy_frame = step_frames[3]
        
        strategy_title = ttk.Label(strategy_frame,
                                  text="Trading Strategy",
                                  font=("Helvetica", 14, "bold"),
                                  foreground=COLORS["primary"])
        strategy_title.pack(pady=20, anchor=tk.W)
        
        # Strategy selector
        strat_select_frame = ttk.Frame(strategy_frame)
        strat_select_frame.pack(fill=tk.X, pady=10, anchor=tk.W)
        
        strat_label = ttk.Label(strat_select_frame, text="Active Strategy:")
        strat_label.pack(side=tk.LEFT)
        
        wizard_strategy_var = tk.StringVar(value=self.config["strategies"]["active_strategy"])
        strategies = ["hyperfocus_strategy", "rsi_strategy", "macd_strategy", "ml_strategy"]
        strat_dropdown = ttk.Combobox(strat_select_frame, textvariable=wizard_strategy_var, values=strategies)
        strat_dropdown.pack(side=tk.LEFT, padx=(10, 0))
        
        # Strategy description
        desc_frame = ttk.Frame(strategy_frame)
        desc_frame.pack(fill=tk.X, pady=20)
        
        strategy_descriptions = {
            "hyperfocus_strategy": """
            HyperFocus Strategy: Advanced multi-timeframe analysis that adapts to market conditions.
            • Uses correlation between timeframes
            • Dynamically adjusts to volatility
            • Best for trending and ranging markets
            • Recommended for most users
            """,
            
            "rsi_strategy": """
            RSI Strategy: Uses Relative Strength Index to identify overbought/oversold conditions.
            • Simple and reliable
            • Better for ranging markets
            • Good starting strategy for beginners
            • Configurable periods and thresholds
            """,
            
            "macd_strategy": """
            MACD Strategy: Moving Average Convergence/Divergence momentum trading.
            • Follows market trends
            • Good for medium to long timeframes
            • Signals trend changes
            • Lower trade frequency
            """,
            
            "ml_strategy": """
            Machine Learning Strategy: AI-enhanced prediction model.
            • Uses historical data patterns
            • Adapts to changing market conditions
            • Requires additional setup
            • Advanced users only
            """
        }
        
        desc_text = tk.Text(desc_frame, height=10, bg="#1a1a1a", fg="#cccccc", wrap=tk.WORD)
        desc_text.pack(fill=tk.X)
        desc_text.insert("1.0", strategy_descriptions[wizard_strategy_var.get()])
        desc_text.config(state=tk.DISABLED)
        
        # Update description when strategy changes
        def update_description(*args):
            selected = wizard_strategy_var.get()
            desc_text.config(state=tk.NORMAL)
            desc_text.delete("1.0", tk.END)
            desc_text.insert("1.0", strategy_descriptions.get(selected, "No description available"))
            desc_text.config(state=tk.DISABLED)
        
        wizard_strategy_var.trace("w", update_description)
        
        # Function to save all wizard settings
        def save_wizard_settings():
            try:
                # Update config with wizard values
                self.config["exchange"] = {
                    "name": exchange_var.get(),
                    "sandbox_mode": sandbox_var.get()
                }
                
                self.config["trading"] = {
                    "base_symbol": wizard_base_var.get(),
                    "quote_symbol": wizard_quote_var.get(),
                    "trade_amount": float(wizard_amount_var.get()),
                    "auto_trade": wizard_auto_var.get()
                }
                
                self.config["strategies"]["active_strategy"] = wizard_strategy_var.get()
                
                # Update UI in main window
                self.base_var.set(wizard_base_var.get())
                self.quote_var.set(wizard_quote_var.get())
                self.amount_var.set(float(wizard_amount_var.get()))
                self.strategy_var.set(wizard_strategy_var.get())
                self.autotrade_var.set(wizard_auto_var.get())
                
                # Save to file
                os.makedirs(CONFIG_DIR, exist_ok=True)
                with open(os.path.join(CONFIG_DIR, "config.json"), 'w') as f:
                    json.dump(self.config, f, indent=2)
                    
                messagebox.showinfo("Setup Complete", "BROski Bot has been configured successfully!")
                self.log_activity("Setup wizard completed successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")
                self.log_activity(f"Error in setup wizard: {e}")
        
        # Start at step 1
        go_to_step(1)
        
        # Make the wizard modal
        wizard_window.transient(self.root)
        wizard_window.grab_set()
        self.root.wait_window(wizard_window)

# Add this at the end of the file to start the application
def main():
    """Start the BROski Ultra Hub application"""
    root = tk.Tk()
    app = BroskiUltraHub(root)
    # Set the closing handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    # Run the initial environment check
    app.check_environment()
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
