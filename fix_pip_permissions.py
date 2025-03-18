#!/usr/bin/env python
"""
Fix pip permissions error when installing packages
"""
import os
import sys
import subprocess
import argparse

def install_requirements(use_admin=False, skip_cache=True, requirements_path=None):
    """Install requirements with various fixes for permission errors"""
    
    if requirements_path is None:
        # Default path to requirements file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        requirements_path = os.path.join(base_dir, 'docs', 'requirements.txt')
    
    if not os.path.exists(requirements_path):
        print(f"Error: Requirements file not found at {requirements_path}")
        return False
        
    # Construct pip command
    pip_cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade']
    
    # Add no-cache flag if requested
    if skip_cache:
        pip_cmd.append('--no-cache-dir')
        
    # Add requirements file
    pip_cmd.extend(['-r', requirements_path])
    
    try:
        print(f"Installing requirements from {requirements_path}")
        print(f"Command: {' '.join(pip_cmd)}")
        
        if use_admin and os.name == 'nt':  # Windows only
            # Use runas for admin privileges
            admin_cmd = ['runas', '/user:Administrator', ' '.join(pip_cmd)]
            print("Requesting administrator privileges...")
            subprocess.run(admin_cmd, shell=True, check=True)
        else:
            # Regular execution
            subprocess.run(pip_cmd, check=True)
            
        print("✅ Successfully installed requirements!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix pip permissions and install requirements")
    parser.add_argument('--admin', action='store_true', help='Run with admin privileges')
    parser.add_argument('--use-cache', action='store_true', help='Use pip cache (default: no cache)')
    parser.add_argument('--requirements', type=str, help='Path to requirements file')
    
    args = parser.parse_args()
    
    success = install_requirements(
        use_admin=args.admin, 
        skip_cache=not args.use_cache,
        requirements_path=args.requirements
    )
    
    sys.exit(0 if success else 1)
