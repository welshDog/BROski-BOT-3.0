#!/usr/bin/env python
"""
BROski Bot 3.0 - Simple Brain Hub Launcher
Quick utility to start the minimal Brain Hub dashboard
"""
import os
import sys
import subprocess
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def main():
    """Launch the simplified BROski Brain Hub"""
    print(f"{Fore.CYAN}=" * 70)
    print(f"{Fore.CYAN}BROski Bot - Simplified Brain Hub Launcher")
    print(f"{Fore.CYAN}=" * 70)
    
    dashboard_path = os.path.join("ui", "simple_brain_hub.py")
    
    # Create the file if it doesn't exist
    if not os.path.exists(dashboard_path):
        print(f"{Fore.YELLOW}Creating simplified Brain Hub file...")
        with open(dashboard_path, 'w') as f:
            f.write('''#!/usr/bin/env python
"""
BROski Bot 3.0 - Simplified Brain Hub
A minimal version of the Brain Hub that should work with basic dependencies
"""
import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="BROski Bot - Simplified Brain Hub",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("🧠 BROski Bot Simplified Brain Hub")
st.write("This is a simplified version of the Brain Hub to verify Streamlit is working correctly.")

# Basic sidebar
st.sidebar.title("Brain Controls")
symbol = st.sidebar.selectbox("Select Symbol", ["BTC/USDT", "ETH/USDT", "PI/USDT"])

# Tabs
tab1, tab2, tab3 = st.tabs(["Dashboard", "Performance", "Alerts"])

# Tab 1: Dashboard
with tab1:
    st.header(f"{symbol} Dashboard")
    
    # Simple metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Price", "$50,000", "1.2%")
    with col2:
        st.metric("Volume", "$1.2B", "-0.5%") 
    with col3:
        st.metric("RSI", "55", "5")
    
    # Simple data display
    st.subheader("Recent Data")
    df = pd.DataFrame({
        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S") for _ in range(5)],
        "Price": [50000 + i*100 for i in range(5)],
        "Volume": [1000000 + i*10000 for i in range(5)]
    })
    st.dataframe(df)
''')
        print(f"{Fore.GREEN}✅ Simplified Brain Hub file created!")
    
    print(f"{Fore.GREEN}Starting Simplified BROski Brain Hub...")
    print(f"{Fore.YELLOW}This will open in your default web browser.")
    print(f"{Fore.YELLOW}Press Ctrl+C in this terminal to stop the Brain Hub.")
    
    try:
        # Launch the dashboard using Streamlit with minimal arguments
        subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path], check=True)
        return True
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Brain Hub stopped.")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error launching Brain Hub: {str(e)}")
        print(f"{Fore.YELLOW}Detailed error information:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
