# BROski Bot 3.0 - Essential Files Guide

## Core Files

These are the main files you'll work with:

- **unified_launcher.py** - MAIN ENTRY POINT for starting the bot
- **config.json** - Your personal configuration (API keys and settings)
- **config.example.json** - Example configuration (for reference)
- **quick_start.py** - First-time setup wizard
- **README.md** - Main documentation

## Important Directories

- **core/** - Core trading engine components
- **strategies/** - Trading strategy implementations
- **utils/** - Utility scripts and helpers
- **ui/** - User interface components
- **docs/** - Documentation files
- **logs/** - Log files (auto-generated)
- **data/** - Data storage (auto-generated)
- **backups/** - Configuration backups (auto-generated)
- **archive/** - Archived/obsolete files (for reference only)

## How to Start

1. Run the quick start wizard:
   ```
   python quick_start.py
   ```

2. Or launch the main interface:
   ```
   python unified_launcher.py
   ```

3. Check system health:
   ```
   python utils/check_system.py
   ```

Remember to edit your `config.json` file to include your API keys and trading preferences.
