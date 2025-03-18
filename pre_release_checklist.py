#!/usr/bin/env python
"""
Pre-release validation script for BROski Bot 3.0
Run this before deploying to production
"""
import os
import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PreReleaseCheck:
    """Performs pre-release validation checks"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
    
    def run_all_checks(self):
        """Run all pre-release checks"""
        logger.info("RUNNING PRE-RELEASE VALIDATION")
        
        # 1. Configuration check
        self.check_configuration()
        
        # 2. ML model validation
        self.validate_ml_models()
        
        # 3. Backtest evaluation
        self.evaluate_backtest_results()
        
        # 4. Risk parameters check
        self.check_risk_parameters()
        
        # 5. API connectivity test
        self.test_api_connectivity()
        
        # Report results
        logger.info(f"CHECK SUMMARY: {self.checks_passed} passed, {self.checks_failed} failed, {self.warnings} warnings")
        
        if self.checks_failed > 0:
            logger.error("❌ CRITICAL ISSUES FOUND - BOT IS NOT READY FOR PRODUCTION")
            return False
        elif self.warnings > 0:
            logger.warning("⚠️ BOT IS READY WITH CAUTIONS - Review warnings before proceeding")
            return True
        else:
            logger.info("✅ ALL CHECKS PASSED - BOT IS READY FOR PRODUCTION")
            return True
    
    def check_configuration(self):
        """Ensure configuration files are properly set up"""
        try:
            if not os.path.exists("config.json"):
                logger.error("❌ config.json not found")
                self.checks_failed += 1
                return
                
            with open("config.json", 'r') as f:
                config = json.load(f)
                
            # Check API keys are not default values
            if config.get("exchange", {}).get("api_key", "") in ["", "YOUR_API_KEY_HERE"]:
                logger.error("❌ API keys not configured")
                self.checks_failed += 1
            else:
                logger.info("✅ API configuration found")
                self.checks_passed += 1
                
            # Check trading parameters
            if "trading" not in config:
                logger.error("❌ Trading parameters missing from config")
                self.checks_failed += 1
            else:
                logger.info("✅ Trading parameters configured")
                self.checks_passed += 1
        
        except Exception as e:
            logger.error(f"❌ Configuration check failed: {str(e)}")
            self.checks_failed += 1
    
    def validate_ml_models(self):
        """Check ML model performance metrics"""
        # This would validate saved models or run test predictions
        try:
            # Example validation - replace with actual model testing code
            models_path = os.path.join("data", "models")
            if not os.path.exists(models_path) or len(os.listdir(models_path)) == 0:
                logger.warning("⚠️ No ML models found - models will be trained on first run")
                self.warnings += 1
            else:
                logger.info("✅ ML models available")
                self.checks_passed += 1
                
            # Recommend running model accuracy test
            logger.info("ℹ️ RECOMMENDATION: Run ML validation tests before live trading")
            
        except Exception as e:
            logger.error(f"❌ ML model validation failed: {str(e)}")
            self.checks_failed += 1
    
    def evaluate_backtest_results(self):
        """Review backtest performance metrics"""
        try:
            # This would load and analyze backtest results
            backtest_path = os.path.join("data", "backtests")
            if not os.path.exists(backtest_path) or len(os.listdir(backtest_path)) == 0:
                logger.warning("⚠️ No backtest results found - run backtesting before live trading")
                self.warnings += 1
            else:
                logger.info("✅ Backtest data available")
                self.checks_passed += 1
                
            logger.info("ℹ️ RECOMMENDATION: Run at least 30 days of backtesting with different market conditions")
            
        except Exception as e:
            logger.error(f"❌ Backtest evaluation failed: {str(e)}")
            self.checks_failed += 1
    
    def check_risk_parameters(self):
        """Validate risk management settings"""
        try:
            with open("config.json", 'r') as f:
                config = json.load(f)
            
            trading = config.get("trading", {})
            
            # Check position size limits
            max_position = trading.get("max_position_size", 0)
            if max_position <= 0 or max_position > 100:
                logger.warning("⚠️ Unusual max position size detected")
                self.warnings += 1
            else:
                logger.info("✅ Position sizing looks reasonable")
                self.checks_passed += 1
                
            # Check stop loss settings
            if "stop_loss" not in trading:
                logger.warning("⚠️ No stop loss configured - high risk")
                self.warnings += 1
            else:
                logger.info("✅ Stop loss configured")
                self.checks_passed += 1
                
        except Exception as e:
            logger.error(f"❌ Risk parameters check failed: {str(e)}")
            self.checks_failed += 1
    
    def test_api_connectivity(self):
        """Test exchange API connectivity"""
        try:
            # This would test API connections with exchange
            # Using a placeholder since actual API testing would require keys
            logger.info("ℹ️ API connectivity testing requires credentials")
            logger.info("ℹ️ RECOMMENDATION: Test API connection with minimal permissions first")
            
            # Check if ccxt is available
            try:
                import ccxt
                logger.info("✅ CCXT library available for exchange connectivity")
                self.checks_passed += 1
            except ImportError:
                logger.error("❌ CCXT library not installed - required for exchange connectivity")
                self.checks_failed += 1
                
        except Exception as e:
            logger.error(f"❌ API connectivity test failed: {str(e)}")
            self.checks_failed += 1

if __name__ == "__main__":
    checker = PreReleaseCheck()
    is_ready = checker.run_all_checks()
    sys.exit(0 if is_ready else 1)
