#!/usr/bin/env python
"""
BROski Bot 3.0 - Stark Interface Integration Helper
Helps integrate the Tony Stark-inspired UI with the existing BROski Bot system
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def ensure_ui_directories():
    """Create necessary UI directories if they don't exist"""
    project_root = Path(__file__).parent
    
    # Ensure UI directory exists
    ui_dir = project_root / "ui"
    ui_dir.mkdir(exist_ok=True)
    
    # Create assets directory for UI resources
    assets_dir = ui_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Create fonts directory if it doesn't exist
    fonts_dir = ui_dir / "fonts"
    fonts_dir.mkdir(exist_ok=True)
    
    return ui_dir, assets_dir, fonts_dir

def create_font_notice():
    """Create a notice about fonts instead of downloading them"""
    fonts_dir = Path(__file__).parent / "ui" / "fonts"
    fonts_dir.mkdir(exist_ok=True)
    
    notice_path = fonts_dir / "FONT_NOTICE.txt"
    
    notice_content = """STARK INTERFACE FONT NOTICE
    
The STARK Interface uses these Google Fonts:
1. Rajdhani - https://fonts.google.com/specimen/Rajdhani
2. Orbitron - https://fonts.google.com/specimen/Orbitron

These fonts are automatically loaded from Google's CDN in the HTML.
If you want to use them offline, download the fonts manually from the links above.

Place the TTF files in this directory for offline usage.
"""
    
    with open(notice_path, "w", encoding="utf-8") as f:
        f.write(notice_content)
    
    print(f"[OK] Created font notice at {notice_path}")

def create_feather_icons_helper():
    """Create a helper script to get Feather Icons locally if CDN fails"""
    ui_dir = Path(__file__).parent / "ui"
    
    helper_path = ui_dir / "feather_icons_helper.py"
    
    helper_code = """#!/usr/bin/env python
\"\"\"
BROski Bot 3.0 - Feather Icons Helper
Downloads Feather Icons locally as fallback for the Stark Interface
\"\"\"
import os
import sys
import requests
import json
import base64

def download_feather_icons():
    \"\"\"Download Feather Icons SVG files\"\"\"
    print("Downloading Feather Icons...")
    
    # Create icons directory
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    # Get icons from Feather CDN
    try:
        response = requests.get("https://unpkg.com/feather-icons/dist/feather-sprite.svg")
        if response.status_code == 200:
            # Save the sprite file
            with open(os.path.join(icons_dir, "feather-sprite.svg"), "wb") as f:
                f.write(response.content)
            print("[OK] Feather Icons downloaded successfully!")
            return True
        else:
            print("[ERROR] Failed to download Feather Icons")
            return False
    except Exception as e:
        print(f"[ERROR] Error downloading Feather Icons: {str(e)}")
        return False

def generate_fallback_script():
    \"\"\"Generate a JavaScript fallback for Feather Icons\"\"\"
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons")
    sprite_path = os.path.join(icons_dir, "feather-sprite.svg")
    
    if not os.path.exists(sprite_path):
        print("Sprite file not found. Download icons first.")
        return False
    
    # Read the sprite file
    with open(sprite_path, "r", encoding="utf-8") as f:
        sprite_content = f.read()
    
    # Create a simple JS file that injects the SVG sprite into the page
    fallback_js = f\"\"\"
    // Feather Icons Fallback
    if (typeof feather === 'undefined') {{
        console.log('Feather Icons not loaded from CDN, using fallback...');
        
        // Create and inject the sprite
        const sprite = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        sprite.innerHTML = `{sprite_content}`;
        sprite.style.display = 'none';
        document.body.appendChild(sprite);
        
        // Simple replacement for feather.replace()
        window.feather = {{
            replace: function() {{
                document.querySelectorAll('[data-feather]').forEach(function(el) {{
                    const iconName = el.getAttribute('data-feather');
                    const useEl = document.createElementNS('http://www.w3.org/2000/svg', 'use');
                    useEl.setAttributeNS('http://www.w3.org/1999/xlink', 'href', `#${{iconName}}`);
                    el.appendChild(useEl);
                }});
            }}
        }};
        
        // Initialize
        feather.replace();
    }}
    \"\"\"
    
    # Save the fallback JS
    with open(os.path.join(icons_dir, "feather-fallback.js"), "w", encoding="utf-8") as f:
        f.write(fallback_js)
    
    print("[OK] Feather Icons fallback script created!")
    return True

if __name__ == "__main__":
    if download_feather_icons():
        generate_fallback_script()
"""
    
    with open(helper_path, "w", encoding="utf-8") as f:
        f.write(helper_code)
    
    print(f"[OK] Created {helper_path}")

def update_dashboard_launcher():
    """Update the dashboard launcher to include Stark Interface"""
    project_root = Path(__file__).parent
    launcher_path = project_root / "launch_dashboard.py"
    
    launcher_code = """#!/usr/bin/env python
\"\"\"
BROski Bot 3.0 - Dashboard Launcher
Launches the desired dashboard interface
\"\"\"
import os
import sys
import subprocess
import webbrowser

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def launch_dashboard():
    \"\"\"Launch the BROski Dashboard\"\"\"
    print("BROski Bot 3.0 - Dashboard Launcher")
    print("=" * 50)
    
    # Dashboard options
    print("Select dashboard to launch:")
    print("1. STARK Interface (Iron Man-inspired UI)")
    print("2. Streamlit Dashboard")
    print("3. Simple Dashboard")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == '1':
        # Launch Stark Interface
        stark_path = os.path.join('ui', 'templates', 'dashboard_template.html')
        if os.path.exists(stark_path):
            print("Launching STARK Interface...")
            webbrowser.open('file://' + os.path.abspath(stark_path))
        else:
            print("STARK Interface not found. Try running utils/create_dashboard.py first.")
    
    elif choice == '2':
        # Launch Streamlit dashboard
        dashboard_path = os.path.join('ui', 'broski_dashboard.py')
        if os.path.exists(dashboard_path):
            print("Launching Streamlit dashboard...")
            subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path])
        else:
            print("Streamlit dashboard not found. Try running utils/create_dashboard.py first.")
    
    elif choice == '3':
        # Launch Simple dashboard
        simple_dashboard = os.path.join('ui', 'simple_dashboard.py')
        if os.path.exists(simple_dashboard):
            print("Launching Simple dashboard...")
            subprocess.run([sys.executable, simple_dashboard])
        else:
            print("Simple dashboard not found. Try running utils/create_dashboard.py first.")
    
    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    launch_dashboard()
"""
    
    # Back up existing launcher if it exists
    if launcher_path.exists():
        backup_path = launcher_path.with_suffix('.py.bak')
        shutil.copy(launcher_path, backup_path)
        print(f"[OK] Backed up launcher to {backup_path}")
    
    # Write new launcher
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write(launcher_code)
    
    print(f"[OK] Updated {launcher_path}")

def integrate_stark_interface():
    """Main function to integrate the Stark Interface with BROski Bot"""
    print("=" * 60)
    print("BROski Bot 3.0 - STARK Interface Integration Helper")
    print("=" * 60)
    
    # Ensure required directories exist
    ui_dir, assets_dir, fonts_dir = ensure_ui_directories()
    print("[OK] Created necessary directories")
    
    # Create font notice instead of downloading
    create_font_notice()
    
    # Create Feather icons helper
    create_feather_icons_helper()
    
    # Update dashboard launcher
    update_dashboard_launcher()
    
    print("\n[SUCCESS] STARK Interface integration steps complete!")
    print("\nNext steps:")
    print("1. Run the STARK Interface directly: open ui/templates/dashboard_template.html")
    print("2. Use the updated launcher: python launch_dashboard.py")
    print("3. Choose option 1 in the launcher for the STARK Interface")
    print("\nOptional improvements:")
    print("- Add live data to the STARK Interface by editing the JavaScript")
    print("- Customize the color scheme in the CSS :root section")
    print("- Add more cards or charts to display additional information")

if __name__ == "__main__":
    integrate_stark_interface()
