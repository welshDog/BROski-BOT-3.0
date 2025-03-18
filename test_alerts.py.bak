#!/usr/bin/env python
"""
BROski Bot 3.0 - Alert System Tester
Creates sample alerts and simulates market data to trigger them
"""
import os
import sys
import time
import random
import logging
import math
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AlertsTest")

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Create data directories if needed
os.makedirs("data/alerts", exist_ok=True)

# Import alerts manager
from utils.alerts_manager import (
    AlertsManager, 
    PriceAlert, 
    PercentChangeAlert, 
    IndicatorAlert,
    PatternAlert,
    VolumeAlert
)

class TestNotificationManager:
    """Simple notification manager for testing"""
    def send_alert_notification(self, alert):
        logger.info(f"🔔 NOTIFICATION: Alert '{alert.name}' for {alert.symbol} triggered!")
        print(f"\n{'=' * 50}")
        print(f"🚨 ALERT TRIGGERED: {alert.name}")
        print(f"📊 Symbol: {alert.symbol}")
        print(f"⏱️ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if isinstance(alert, PriceAlert):
            print(f"💲 Price {alert.condition} ${alert.price:.4f}")
        elif isinstance(alert, IndicatorAlert):
            print(f"📈 {alert.indicator.upper()} {alert.condition} {alert.value}")
        print(f"{'=' * 50}\n")

def create_sample_alerts(alerts_mgr):
    """Create a variety of sample alerts"""
    # Price alerts
    btc_price_alert = PriceAlert("BTC Above 52000", "BTC/USDT", 52000, "above")
    alerts_mgr.add_alert(btc_price_alert)
    
    btc_price_alert2 = PriceAlert("BTC Below 48000", "BTC/USDT", 48000, "below")
    alerts_mgr.add_alert(btc_price_alert2)
    
    # RSI alerts
    rsi_alert = IndicatorAlert("BTC RSI Overbought", "BTC/USDT", "rsi", "above", 70)
    alerts_mgr.add_alert(rsi_alert)
    
    rsi_alert2 = IndicatorAlert("BTC RSI Oversold", "BTC/USDT", "rsi", "below", 30)
    alerts_mgr.add_alert(rsi_alert2)
    
    # Volume alert
    volume_alert = VolumeAlert("BTC Volume Spike", "BTC/USDT", 2.5, 12)
    alerts_mgr.add_alert(volume_alert)
    
    # Pattern alert
    pattern_alert = PatternAlert("Double Bottom", "BTC/USDT", "double_bottom", 75)
    alerts_mgr.add_alert(pattern_alert)
    
    # Percent change alert (5% in 30 minutes)
    percent_alert = PercentChangeAlert("BTC 5% Change", "BTC/USDT", 5.0, 30, "any")
    alerts_mgr.add_alert(percent_alert)
    
    logger.info(f"Created {len(alerts_mgr.get_alerts())} sample alerts")

def generate_market_data(cycle=0):
    """Generate simulated market data that will trigger alerts randomly"""
    # Base price oscillates between 47000 and 53000
    base_price = 50000 + 3000 * math.sin(cycle / 5)
    
    # Add some noise
    price = base_price + random.uniform(-500, 500)
    
    # RSI oscillates between 20 and 80
    rsi = 50 + 30 * math.sin(cycle / 8)
    
    # Create volume spikes occasionally
    if random.random() > 0.8:
        volume = 5000 * random.uniform(2, 4)  # Big spike
    else:
        volume = 5000 * random.uniform(0.8, 1.2)  # Normal volume
    
    # Price history - we'll just create some fake data points going back
    price_history = []
    for i in range(1, 13):
        # Price gradually changes over time
        historical_price = price - (i * 100 * random.uniform(0.8, 1.2))
        price_history.append({
            "timestamp": time.time() - (i * 3600),  # hourly data
            "price": historical_price
        })
    
    # Volume history
    volume_history = []
    for i in range(1, 25):
        # Normal volume for past data
        historical_volume = 5000 * random.uniform(0.8, 1.2)
        volume_history.append({
            "timestamp": time.time() - (i * 3600),
            "volume": historical_volume
        })
    
    # Pattern detection (randomly trigger occasionally)
    patterns = {}
    if random.random() > 0.9:
        pattern_type = random.choice(["double_bottom", "double_top", "head_shoulders"])
        confidence = random.uniform(60, 95)
        patterns[pattern_type] = {"detected": True, "confidence": confidence}
    
    # Create market data dictionary
    return {
        "symbol": "BTC/USDT",
        "price": price,
        "price_history": price_history,
        "volume": volume,
        "volume_history": volume_history,
        "indicators": {
            "rsi": rsi,
            "macd": 50 * math.sin(cycle / 10),
            "signal": 50 * math.sin((cycle / 10) + 1),
            "histogram": 50 * math.sin(cycle / 10) - 50 * math.sin((cycle / 10) + 1)
        },
        "patterns": patterns
    }

def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("BROski Bot - Alert System Tester")
    print("=" * 60)
    
    # Create alert manager with our test notification system
    notifier = TestNotificationManager()
    alerts_mgr = AlertsManager(notification_manager=notifier)
    
    # Check if we already have alerts
    existing_alerts = alerts_mgr.get_alerts()
    if not existing_alerts:
        print("\n📝 Creating sample alerts...")
        create_sample_alerts(alerts_mgr)
    else:
        print(f"\n✓ Using {len(existing_alerts)} existing alerts")
    
    print("\n▶️ Starting alert test simulation...")
    print("Press Ctrl+C to stop the test\n")
    
    try:
        for cycle in range(100):  # Run for 100 cycles
            # Generate simulated market data
            market_data = generate_market_data(cycle)
            
            # Print current price and RSI
            print(f"Cycle {cycle+1}: BTC/USDT Price: ${market_data['price']:.2f}, RSI: {market_data['indicators']['rsi']:.1f}")
            
            # Check alerts against the data
            triggered = alerts_mgr.check_alerts(market_data)
            if not triggered:
                print("No alerts triggered")
            
            # Sleep before next cycle
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Test stopped by user")
    
    print("\n✅ Alert testing complete!")

if __name__ == "__main__":
    main()
