#!/bin/bash

echo "Starting BROski Bot 3.0 Easy Setup..."

# Check for Python installation
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH."
    echo "Please install Python 3.8 or higher from your package manager"
    echo "or from https://www.python.org/downloads/"
    exit 1
fi

# Generate file listing
echo "Generating file listing..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows environment - try PowerShell first
    if command -v powershell.exe &> /dev/null; then
        echo "Using PowerShell to generate file listing..."
        # Use current directory (.) for both source and output
        powershell.exe -Command "Get-ChildItem -Path . -Recurse | Select-Object FullName | Out-File -FilePath './filelist.txt'"
        if [ ! -f "./filelist.txt" ] || [ ! -s "./filelist.txt" ]; then
            echo "PowerShell command failed, falling back to dir command..."
            dir /s /b > filelist.txt
        fi
    else
        # Fallback to dir command if PowerShell isn't available
        echo "PowerShell not available, using dir command..."
        dir /s /b > filelist.txt
    fi
else
    # Unix/Linux environment
    find . -type f | sort > filelist.txt
fi
echo "File listing saved to filelist.txt"

# Run the setup script
python3 easy_setup.py

# Check if script succeeded
if [ $? -ne 0 ]; then
    echo "Setup encountered some issues. Please check the messages above."
else
    echo "Setup completed successfully!"
fi

echo "Press Enter to continue..."
read
