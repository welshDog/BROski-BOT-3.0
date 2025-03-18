# BROski Bot 3.0 - Ultra Hub

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

BROski Bot 3.0 is an advanced cryptocurrency trading system with an Iron Man themed UI for seamless trading management.

<p align="center">
  <img src="assets/broski_logo.png" alt="BROski Bot Logo" width="200">
</p>

## Features

- **Ultra Hub**: Central command center for all trading operations
- **Multi-Exchange Support**: Compatible with multiple cryptocurrency exchanges
- **Real-Time Monitoring**: Live trade and market data visualization
- **AI-Enhanced Strategies**: Advanced algorithmic trading strategies
- **Hyperfocus Mode**: Distraction-free trading interface for critical market moments
- **Notification System**: Custom alerts for trade events and system status
- **Visual Strategy Builder**: Create and test trading strategies without coding
- **Backtesting**: Test strategies against historical data

## Getting Started

### Prerequisites

- Python 3.8+
- Required packages (see `docs/requirements.txt`)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/broski-bot.git
   cd broski-bot
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install required packages:
   ```
   pip install -r docs/requirements.txt
   ```

4. Create a logo (first time only):
   ```
   python utils/create_logo.py
   ```

5. Launch the Ultra Hub:
   ```
   python broski_ultra_hub.py
   ```

## Usage

### Ultra Hub

The Ultra Hub provides access to all BROski Bot components:

- **Launch Tab**: Start various components (dashboards, bots, utilities)
- **Configuration Tab**: Configure trading settings and API keys
- **Monitoring Tab**: View system status, activity logs, and performance metrics
- **Notifications Tab**: Set up desktop, email, and mobile notifications
- **Strategy Builder Tab**: Create custom trading strategies visually
- **Help Tab**: Access documentation and information about the system

### Hyperfocus Mode

For intense trading sessions, use Hyperfocus Mode which provides:

- Distraction-free interface
- Real-time price monitoring
- Quick buy/sell actions
- Key metrics display

## Project Structure

See [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for detailed information about the project organization.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Built with Python and Tkinter
- Inspired by Iron Man's JARVIS interface

# BROski Bot 3.0

Advanced cryptocurrency trading bot with HyperFocus multi-timeframe analysis, backtesting, and correlation-based risk management.

![BROski Bot](ui/broski_icon.png)

## Crypto Trading Bot - For Educational Purposes

BROski Bot is a modular cryptocurrency trading bot designed to automate trading on various exchanges, with primary support for MEXC. This software is for **educational purposes only** and comes with significant financial risk.

## ⚠️ DISCLAIMER

**CRYPTOCURRENCY TRADING INVOLVES SIGNIFICANT RISK AND IS NOT SUITABLE FOR ALL INVESTORS.**

Trading cryptocurrencies carries a high level of risk. The possibility exists that you could sustain a loss of some or all of your initial investment. BROski Bot is provided for educational purposes only and is not financial advice. [Read our full risk disclaimer](docs/RISK_DISCLAIMER.md).

## 🚀 Features

- **HyperFocus Trading Strategy** - Advanced multi-timeframe analysis with market regime detection
- **Professional Dashboard** - Real-time monitoring with interactive charts and metrics
- **Portfolio Management** - Correlation analysis to avoid overexposure to similar assets
- **Comprehensive Backtesting** - Statistical validation and Monte Carlo simulation
- **Multi-Exchange Support** - Trade across different exchanges and capture arbitrage opportunities
- **Risk Management** - Smart position sizing and drawdown protection
- **Unified Launcher** - Single interface to access all bot components

## 📊 Project Metrics

- **Total Files:** 533
- **Python Files:** 291
- **Documentation Files:** 133
- **Configuration Files:** 20
- **Scripts:** 28
- **Web UI Files:** 13

*Last updated: 2025-03-12 12:17:10*

- **Total Files:** 528
- **Python Files:** 290
- **Documentation Files:** 131
- **Configuration Files:** 18
- **Scripts:** 28
- **Web UI Files:** 13

*Last updated: 2025-03-12 08:57:49*

- **Total Files:** 515
- **Python Files:** 282
- **Documentation Files:** 129
- **Configuration Files:** 18
- **Scripts:** 28
- **Web UI Files:** 12

*Last updated: 2025-03-12 03:06:11*

## 📋 Requirements

- Python 3.8 or higher
- MEXC Exchange API Keys
- 2GB+ RAM recommended
- Internet connection

## ⚙️ Quick Installation

1. **Clone the repository or download the zip file**

2. **Create a virtual environment** (recommended)
   ```
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

4. **Install dependencies**
   ```
   pip install -r docs/requirements.txt
   ```

5. **Run the system check**
   ```
   python utils/check_system.py
   ```

## 🔧 Configuration

1. Edit the `config.json` file with your:
   - API keys
   - Trading preferences
   - Risk parameters
   
2. Or use the quick start wizard:
   ```
   python quick_start.py
   ```

## ▶️ Usage

### Start the Unified Launcher

1. Launch the unified launcher:
   ```bash
   python unified_launcher.py
   ```
2. Access these main features:
   - **Control Center** - Main bot configuration interface
   - **Dashboard** - Visual trade monitoring
   - **Trading Bot** - Start/stop the trading engine
   - **Monitoring Tools** - View logs and status
   - **Utilities** - Maintenance and emergency functions

## 📋 Documentation

- [ADVANCED BACKTESTING](docs/ADVANCED_BACKTESTING.md) - ADVANCED BACKTESTING guide
- [BACKTRADER GUIDE](docs/BACKTRADER_GUIDE.md) - BACKTRADER GUIDE guide
- [COLAB ML TRAINING](docs/COLAB_ML_TRAINING.md) - COLAB ML TRAINING guide
- [CONFIGURATION](docs/CONFIGURATION.md) - CONFIGURATION guide
- [DEV ONBOARDING](docs/DEV_ONBOARDING.md) - DEV ONBOARDING guide
- [EMERGENCY PROCEDURES](docs/EMERGENCY_PROCEDURES.md) - EMERGENCY PROCEDURES guide
- [ENVIRONMENT SETUP](docs/ENVIRONMENT_SETUP.md) - ENVIRONMENT SETUP guide
- [FAQ](docs/FAQ.md) - FAQ guide
- [FIRST TIME SETUP](docs/FIRST_TIME_SETUP.md) - FIRST TIME SETUP guide
- [GETTING STARTED](docs/GETTING_STARTED.md) - GETTING STARTED guide
- [HYPERFOCUS STRATEGY](docs/strategies/HYPERFOCUS_STRATEGY.md) - HYPERFOCUS STRATEGY guide
- [INSTALLATION](docs/INSTALLATION.md) - INSTALLATION guide
- [INTEGRATION PLAN](docs/INTEGRATION_PLAN.md) - INTEGRATION PLAN guide
- [LAUNCHER GUIDE](docs/LAUNCHER_GUIDE.md) - LAUNCHER GUIDE guide
- [LOCAL DEVELOPMENT](docs/LOCAL_DEVELOPMENT.md) - LOCAL DEVELOPMENT guide
- [MACD STRATEGY](docs/strategies/MACD_STRATEGY.md) - MACD STRATEGY guide
- [MAIN FILES](docs/MAIN_FILES.md) - MAIN FILES guide
- [ML STRATEGY](docs/strategies/ML_STRATEGY.md) - ML STRATEGY guide
- [PAPER TRADING](docs/PAPER_TRADING.md) - PAPER TRADING guide
- [PROJECT STRUCTURE](docs/PROJECT_STRUCTURE.md) - PROJECT STRUCTURE guide
- [QUICK START](docs/QUICK_START.md) - QUICK START guide
- [RISK DISCLAIMER](docs/RISK_DISCLAIMER.md) - RISK DISCLAIMER guide
- [RISK MANAGEMENT](docs/RISK_MANAGEMENT.md) - RISK MANAGEMENT guide
- [RSI STRATEGY](docs/strategies/RSI_STRATEGY.md) - RSI STRATEGY guide
- [SECURITY GUIDE](docs/SECURITY_GUIDE.md) - SECURITY GUIDE guide
- [TESTING CHECKLIST](docs/TESTING_CHECKLIST.md) - TESTING CHECKLIST guide
- [TOOL ARCHITECTURE](docs/TOOL_ARCHITECTURE.md) - TOOL ARCHITECTURE guide
- [TOOLS EXPLAINED](docs/TOOLS_EXPLAINED.md) - TOOLS EXPLAINED guide
- [TRADING STRATEGIES](docs/TRADING_STRATEGIES.md) - TRADING STRATEGIES guide
- [TRADING STYLES ASSESSMENT](docs/TRADING_STYLES_ASSESSMENT.md) - TRADING STYLES ASSESSMENT guide
- [TROUBLESHOOTING](docs/TROUBLESHOOTING.md) - TROUBLESHOOTING guide
- [USER MANUAL](docs/USER_MANUAL.md) - USER MANUAL guide
- [VERSION HISTORY](docs/VERSION_HISTORY.md) - VERSION HISTORY guide
- [WEB DASHBOARD](docs/WEB_DASHBOARD.md) - WEB DASHBOARD guide

##  📊 Trading Strategies

BROski Bot comes with the following built-in strategies:

- **RSI (Relative Strength Index)** - Identifies overbought/oversold conditions
- **MACD (Moving Average Convergence/Divergence)** - Follows trend momentum

Strategy parameters are configurable in the `config.json` file.

## 🛠️ Configuration

All configuration is done in the `config.json` file:

## 🔒 Security

Your API keys are stored locally and are never transmitted to any external servers. Always enable IP restrictions on your exchange API keys for maximum security.

## ⚠️ Risk Warning

Trading cryptocurrencies carries significant risk. Only trade with funds you can afford to lose. BROski is a tool to assist your trading but does not guarantee profits.

## 📝 License

BROski is provided for educational and personal use. For commercial use, please contact the developers.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Architecture Overview

BROski Bot 3.0 is built on a modular architecture that separates concerns and promotes reusability:
