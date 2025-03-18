from setuptools import setup, find_packages

setup(
    name="broski_bot",
    version="3.0.0",
    description="BROski Bot 3.0 - Advanced Trading Bot with Dashboard",
    author="Lyndz",
    author_email="user@example.com",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.27.0",
        "pandas>=1.5.0",
        "numpy>=1.22.0",
        "plotly>=5.10.0",
        "requests>=2.28.0",
        "aiohttp>=3.8.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ]
    },
    python_requires=">=3.8",
)
