"""
Setup script for static type checking with mypy.

This script helps set up and configure mypy for the BROski Bot codebase,
verifies the mypy installation, and provides a simple way to run type checking.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional, Tuple


def check_mypy_installed() -> bool:
    """Check if mypy is installed."""
    try:
        import mypy
        return True
    except ImportError:
        return False


def install_mypy() -> bool:
    """Install mypy package if not already installed."""
    print("Installing mypy...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mypy"])
        return True
    except subprocess.CalledProcessError:
        print("Failed to install mypy. Please install it manually with:")
        print("pip install mypy")
        return False


def create_mypy_config(config_path: Path) -> None:
    """Create a mypy configuration file if it doesn't exist."""
    if config_path.exists():
        print(f"Mypy config already exists at {config_path}")
        return
    
    config_content = """[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
disallow_incomplete_defs = False
check_untyped_defs = True
disallow_untyped_decorators = False
no_implicit_optional = True
strict_optional = True

# Per-module options:
[mypy.ui.*]
disallow_untyped_defs = True

[mypy.strategies.*]
disallow_untyped_defs = True

[mypy.utils.*]
check_untyped_defs = True
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"Created mypy config at {config_path}")


def run_mypy(paths: List[str], config_path: Path) -> bool:
    """Run mypy type checking on specified paths."""
    print(f"Running mypy on {', '.join(paths)}...")
    
    cmd = ["mypy", "--config-file", str(config_path)]
    cmd.extend(paths)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ No type errors found!")
            return True
        else:
            print("✗ Type errors found:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"Error running mypy: {e}")
        return False


def add_type_hints_example() -> None:
    """Display examples of how to add type hints to existing code."""
    print("\nExamples of adding type hints to your code:\n")
    
    print("Example 1: Function with parameters and return value")
    print("Before:")
    print("""def calculate_moving_average(data, window):
    return data.rolling(window=window).mean()""")
    
    print("\nAfter:")
    print("""from typing import Union
import pandas as pd

def calculate_moving_average(
    data: pd.DataFrame, 
    window: int
) -> pd.Series:
    return data.rolling(window=window).mean()""")
    
    print("\nExample 2: Class with methods")
    print("Before:")
    print("""class TradingStrategy:
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters or {}
        
    def generate_signals(self, data):
        # Implementation
        return signals""")
    
    print("\nAfter:")
    print("""from typing import Dict, Any, Optional
import pandas as pd

class TradingStrategy:
    name: str
    parameters: Dict[str, Any]
    
    def __init__(
        self, 
        name: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        self.name = name
        self.parameters = parameters or {}
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Implementation
        return signals""")


def main() -> None:
    """Main function to set up and run mypy."""
    parser = argparse.ArgumentParser(description="Set up and run mypy for type checking")
    parser.add_argument("--install", action="store_true", help="Install mypy if not already installed")
    parser.add_argument("--setup-only", action="store_true", help="Only set up mypy config without running checks")
    parser.add_argument("--paths", nargs="+", default=["ui", "strategies", "utils"], 
                       help="Paths to check (default: ui strategies utils)")
    args = parser.parse_args()
    
    # Check if mypy is installed
    if not check_mypy_installed():
        if args.install:
            if not install_mypy():
                return
        else:
            print("mypy is not installed. Run with --install to install it.")
            return
    
    # Create config file
    project_root = Path(__file__).parent
    config_path = project_root / "mypy.ini"
    create_mypy_config(config_path)
    
    if not args.setup_only:
        # Run mypy on specified paths
        paths = [str(project_root / path) for path in args.paths]
        success = run_mypy(paths, config_path)
        
        # Display help for adding type hints
        add_type_hints_example()
        
        if not success:
            sys.exit(1)
    else:
        print("Mypy setup completed. Run without --setup-only to perform type checking.")


if __name__ == "__main__":
    main()
