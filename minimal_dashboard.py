#!/usr/bin/env python
# Minimal BROski dashboard for debugging
"""
BROski Bot 3.0 - MinimalDashboard
DESCRIPTION NEEDED
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import traceback

# Configure basic logging to console for debugging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_exception(e):
    """Log an exception with traceback"""
    logger.error(f"Exception occurred: {str(e)}")
    logger.error(traceback.format_exc())

class MinimalDashboard(tk.Tk):
    def __init__(self):
        logger.info("Initializing MinimalDashboard")
        super().__init__()
        
        # Configure window
        self.title("BROski Bot - Minimal Debug Version")
        self.geometry("800x600")
        
        # Simple colors
        self.colors = {
            'bg_dark': '#0f1923',
            'text': '#e0e0e0',
            'accent': '#00b8d4',
        }
        
        # Configure basic styles
        self.configure(bg=self.colors['bg_dark'])
        
        # Create simple UI
        self.create_minimal_ui()
        
        logger.info("MinimalDashboard initialization complete")
    
    def create_minimal_ui(self):
        """Create a very simple UI for testing"""
        logger.info("Creating minimal UI")
        
        # Main frame
        main_frame = tk.Frame(self, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Simple title
        title = tk.Label(main_frame, 
                        text="BROski Bot - Debug Mode", 
                        font=("Arial", 20, "bold"),
                        fg=self.colors['accent'],
                        bg=self.colors['bg_dark'])
        title.pack(pady=20)
        
        # Status message
        status_msg = tk.Label(main_frame,
                            text="If you can see this window without it closing, the base UI works.",
                            fg=self.colors['text'],
                            bg=self.colors['bg_dark'],
                            wraplength=600)
        status_msg.pack(pady=20)
        
        # Test button
        test_button = tk.Button(main_frame, 
                              text="Test Button - Click Me",
                              command=self.test_button_click)
        test_button.pack(pady=10)
        
        # Exit button
        exit_button = tk.Button(main_frame,
                              text="Exit",
                              command=self.destroy)
        exit_button.pack(pady=10)
        
        logger.info("Minimal UI created successfully")
    
    def test_button_click(self):
        """Test event handler"""
        messagebox.showinfo("Test", "Button clicked successfully!")

def main():
    """Main function with try/except for debugging"""
    try:
        logger.info("Starting minimal dashboard")
        app = MinimalDashboard()
        logger.info("Entering mainloop")
        app.mainloop()
        logger.info("Mainloop exited normally")
    except Exception as e:
        log_exception(e)
        print(f"Error starting minimal dashboard: {e}")
        print("See log output above for details.")
        
        # Show error in GUI if possible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", f"Dashboard error: {str(e)}\n\nCheck console for details.")
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    main()
