"""
BROski Bot 3.0 Dashboard Entry Point

This script launches the refactored dashboard with the new modular architecture.
"""
import os
import sys
import streamlit as st


def main():
    """Launch the dashboard by running the Streamlit app."""
    print("Starting BROski Bot 3.0 Dashboard...")
    os.system("streamlit run ui/dashboard.py")


if __name__ == "__main__":
    main()
