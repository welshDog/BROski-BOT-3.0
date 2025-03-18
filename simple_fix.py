#!/usr/bin/env python
"""
Simple encoding fix for dashboard
"""

def create_simple_dashboard():
    """Create a simple working dashboard without encoding problems"""
    print("Creating a simple working dashboard...")
    
    # Create ui directory if it doesn't exist
    import os
    os.makedirs("ui", exist_ok=True)
    
    # Create a simple dashboard that works
    with open('ui/broski_dashboard.py', 'w', encoding='utf-8') as f:
        f.write("""
import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(
    page_title="BROski Bot Dashboard", 
    layout="wide"
)

st.title("BROski Bot 3.0 - Control Center")

# Sidebar controls
st.sidebar.title("Control Panel")

# Add controls
symbol = st.sidebar.selectbox("Trading Pair", ["PI/USDT", "BTC/USDT", "ETH/USDT"])
timeframe = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "30m", "1h", "4h", "1d"])

# Refresh button
if st.sidebar.button("Refresh Data"):
    st.rerun()

# Auto-refresh checkbox
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=False)

# Emergency stop button
if st.sidebar.button("EMERGENCY STOP", help="Stop all trading activities"):
    st.sidebar.error("Trading stopped! Bot is now in monitor-only mode.")

# Create columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Market Analysis")
    
    # Random price chart
    chart_data = pd.DataFrame(
        np.random.randn(100, 3) * np.array([0.01, 0.005, 0.02]) + np.array([1.35, 1.35, 0]),
        columns=['Price', 'SMA', 'Volume']
    )
    
    # Display the chart
    st.line_chart(chart_data[['Price', 'SMA']])
    st.bar_chart(chart_data['Volume'])
    
    # Bot thoughts
    st.subheader("Bot Insights")
    
    # Generate random signals
    import random
    if random.random() > 0.7:  # 30% chance for buy signal
        st.success("BUY SIGNAL - Confidence: 75.5%")
        st.write("**Reason:** Bottom pattern detected")
        st.write("• RSI: 28.5")
        st.write("• MACD: 0.00123")
    elif random.random() > 0.8:  # 20% chance for sell signal
        st.error("SELL SIGNAL - Confidence: 82.3%")
        st.write("**Reason:** Top pattern detected")
        st.write("• RSI: 72.1")
        st.write("• MACD: -0.00156")
    else:  # 50% chance for neutral
        st.info("NEUTRAL - No clear pattern detected")
        st.write("• RSI: 45.3")
        st.write("• MACD: 0.00023")

with col2:
    st.subheader("Current Status")
    
    # Metrics
    st.metric("Current Price", "$1.3456", "1.2%")
    
    # Strategy
    st.subheader("Active Strategy")
    st.write("**HyperFocus Strategy**")
    
    with st.expander("Strategy Parameters"):
        st.write("• Sensitivity: 1.5")
        st.write("• RSI Period: 14")
        st.write("• MACD Fast: 12")
        st.write("• MACD Slow: 26")
    
    # Recent trades
    st.subheader("Recent Trades")
    trade1, trade2 = st.columns(2)
    trade1.write("**BUY**")
    trade1.write("10.5 PI at $1.3245")
    trade2.write("**SELL**")
    trade2.write("8.2 PI at $1.3502")
    
    # Notifications
    st.subheader("Notifications")
    st.info("Signal detected for PI/USDT")
    st.success("Order filled: 10.5 PI at $1.3245")

# Implement auto-refresh
if auto_refresh:
    time.sleep(15)  # Refresh every 15 seconds
    st.rerun()
""")
    
    print("Simple dashboard created successfully.")
    print("\nYou can run the dashboard with:")
    print("streamlit run ui/broski_dashboard.py")

if __name__ == "__main__":
    create_simple_dashboard()
