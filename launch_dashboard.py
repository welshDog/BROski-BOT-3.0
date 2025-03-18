#!/usr/bin/env python
"""
BROski Bot 3.0 Dashboard Launcher

This script launches the BROski Bot 3.0 dashboard, providing a unified entry point
for accessing the various analytics and configuration dashboards.
"""
import os
import sys
import argparse
from pathlib import Path
import subprocess
import webbrowser
from time import sleep
import logging

# Configure logging for performance monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('dashboard_performance.log'),
        logging.StreamHandler()
    ]
)

# Import performance tracking
from utils.profiler import ExecutionTimer, performance_tracker


def ensure_dependencies():
    """Ensure all required dependencies are installed."""
    try:
        import streamlit
        import pandas
        import numpy
        import plotly
        import ccxt
        print("All dependencies are installed.")
        return True
    except ImportError as e:
        print(f"Missing dependency: {str(e)}")
        print("Installing required dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return False


def launch_dashboard(dashboard_type="strategy", port=8501, enable_profiling=False):
    """
    Launch the specified dashboard.
    
    Args:
        dashboard_type: Type of dashboard to launch (regime, strategy, etc.)
        port: Port to run the dashboard on
        enable_profiling: Whether to enable performance profiling
    
    Returns:
        Process object for the dashboard
    """
    # Set up paths
    base_dir = Path(__file__).parent
    dashboard_map = {
        "strategy": "ui/pages/strategy_dashboard.py",
        "regime": "ui/pages/regime_dashboard.py",
        "main": "ui/pages/dashboard.py"
    }
    
    if dashboard_type not in dashboard_map:
        print(f"Unknown dashboard type: {dashboard_type}")
        print(f"Available types: {', '.join(dashboard_map.keys())}")
        return None
    
    dashboard_path = base_dir / dashboard_map[dashboard_type]
    
    if not dashboard_path.exists():
        print(f"Dashboard file not found: {dashboard_path}")
        return None
    
    # Performance timer
    with ExecutionTimer(f"Launching {dashboard_type} dashboard"):
        # Set environment variables for profiling
        env = os.environ.copy()
        if enable_profiling:
            env["BROSKI_ENABLE_PROFILING"] = "1"
        
        # Launch dashboard with Streamlit
        cmd = [
            sys.executable, 
            "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", str(port)
        ]
        
        print(f"Launching {dashboard_type} dashboard on port {port}...")
        process = subprocess.Popen(cmd, env=env)
        
        # Open browser after a short delay
        sleep(2)
        webbrowser.open(f"http://localhost:{port}")
    
    return process


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch BROski Bot 3.0 Dashboard")
    parser.add_argument(
        "--type", "-t",
        default="strategy",
        choices=["strategy", "regime", "main"],
        help="Type of dashboard to launch"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8501,
        help="Port to run the dashboard on"
    )
    parser.add_argument(
        "--profile", "-prof",
        action="store_true",
        help="Enable performance profiling"
    )
    
    args = parser.parse_args()
    
    # Start performance tracking
    if args.profile:
        print("Performance profiling enabled")
        performance_tracker.record_metric(
            name="dashboard_launch", 
            value=0,
            metadata={"type": args.type}
        )
    
    if ensure_dependencies():
        try:
            dashboard_process = launch_dashboard(args.type, args.port, args.profile)
            
            # Keep running until user interrupts
            print("Press Ctrl+C to stop the dashboard")
            dashboard_process.wait()
        except KeyboardInterrupt:
            print("Stopping dashboard...")
            dashboard_process.terminate()
            print("Dashboard stopped.")
            
            # Save performance metrics if profiling was enabled
            if args.profile:
                performance_tracker.save_metrics(f"dashboard_performance_{args.type}.csv")
                print(f"Performance metrics saved to dashboard_performance_{args.type}.csv")
