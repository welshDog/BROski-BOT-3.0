#!/usr/bin/env python
"""
BROski Bot 3.0 - System Check Utility
Standalone system diagnostic tool
"""
import os
import sys
import platform
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Set up path handling
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(ROOT_DIR, "ui")
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

# Colors (Iron Man theme)
COLORS = {
    "bg_dark": "#0d1117",
    "primary": "#0abdc6",  # Cyan blue
    "secondary": "#ea580c",  # Burnt orange
    "accent": "#ff5722",    # Bright orange
    "text_light": "#ffffff",
    "text_dark": "#cccccc",
}

def main():
    """Run standalone system check"""
    root = tk.Tk()
    root.title("BROski System Check")
    root.geometry("600x500")
    root.configure(bg=COLORS["bg_dark"])
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background=COLORS["bg_dark"])
    style.configure('TLabel', background=COLORS["bg_dark"], foreground=COLORS["text_light"])
    style.configure('TButton', 
                   background=COLORS["primary"], 
                   foreground=COLORS["bg_dark"],
                   borderwidth=0)
    
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    results = tk.Text(frame, bg="#1a1a1a", fg="#cccccc", font=("Courier", 10))
    results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    scrollbar = ttk.Scrollbar(frame, command=results.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    results.config(yscrollcommand=scrollbar.set)
    
    # Add check results
    results.insert(tk.END, "BROski Bot System Check\n", "header")
    results.insert(tk.END, "====================\n\n", "header")
    results.tag_config("header", foreground=COLORS["primary"], font=("Courier", 12, "bold"))
    
    # Add system info
    results.insert(tk.END, "System Information\n", "section")
    results.insert(tk.END, "-----------------\n", "section")
    results.tag_config("section", foreground=COLORS["accent"], font=("Courier", 10, "bold"))
    
    results.insert(tk.END, f"Date/Time: {datetime.now()}\n")
    results.insert(tk.END, f"Python Version: {sys.version}\n")
    results.insert(tk.END, f"Platform: {platform.platform()}\n")
    results.insert(tk.END, f"Architecture: {platform.machine()}\n\n")
    
    # Directory check
    results.insert(tk.END, "Directory Check\n", "section")
    results.insert(tk.END, "--------------\n", "section")
    
    for name, path in [
        ("Root", ROOT_DIR), 
        ("UI", UI_DIR), 
        ("Config", CONFIG_DIR), 
        ("Assets", ASSETS_DIR)
    ]:
        status = "FOUND" if os.path.exists(path) else "MISSING"
        color = COLORS["primary"] if status == "FOUND" else COLORS["secondary"]
        results.insert(tk.END, f"{name} Directory: ")
        results.insert(tk.END, f"{status}\n", f"status_{status}")
        results.tag_config(f"status_{status}", foreground=color, font=("Courier", 10, "bold"))
    
    results.insert(tk.END, "\n")
    
    # Package check
    results.insert(tk.END, "Required Packages\n", "section")
    results.insert(tk.END, "----------------\n", "section")
    
    for package in ["tkinter", "PIL", "numpy", "pandas", "plyer"]:
        try:
            __import__(package)
            status = "INSTALLED"
            color = COLORS["primary"]
        except ImportError:
            status = "MISSING"
            color = COLORS["secondary"]
        
        results.insert(tk.END, f"{package}: ")
        results.insert(tk.END, f"{status}\n", f"pkg_{status}")
        results.tag_config(f"pkg_{status}", foreground=color, font=("Courier", 10, "bold"))
    
    # Make text read-only
    results.config(state=tk.DISABLED)
    
    # Add a close button
    btn_frame = ttk.Frame(root)
    btn_frame.pack(fill=tk.X, pady=10)
    
    close_btn = ttk.Button(btn_frame, text="Close", command=root.destroy)
    close_btn.pack(side=tk.RIGHT, padx=10)
    
    copy_btn = ttk.Button(btn_frame, text="Copy Results", command=lambda: copy_to_clipboard(root, results.get(1.0, tk.END)))
    copy_btn.pack(side=tk.RIGHT, padx=10)
    
    root.mainloop()

def copy_to_clipboard(root, text):
    """Copy text to clipboard"""
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Copied", "Results copied to clipboard")

if __name__ == "__main__":
    main()
