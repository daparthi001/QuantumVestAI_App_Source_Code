from setuptools import setup, find_packages

setup(
    name="quantumvestai-ui",
    version="1.0.0",
    description="QuantumVestAI UI - Stock Analysis and Prediction Interface",
    author="QuantumVest Team",
    author_email="info@quantumvest.ai",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "jinja2>=3.0.0",
        "python-multipart>=0.0.5",
        "aiofiles>=0.7.0",
        "httpx>=0.19.0",
        "pydantic>=1.8.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib>=1.7.4",
        "yfinance>=0.1.70",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "pytest>=6.2.0",
        "requests>=2.26.0",
    ],
    entry_points={
        "console_scripts": [
            "quantumvestai=ui.main:app",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Investment",
        "Framework :: FastAPI",
    ],
    project_urls={
        "Documentation": "https://docs.quantumvest.ai",
        "Source": "https://github.com/quantumvest/quantumvestai-ui",
        "Issues": "https://github.com/quantumvest/quantumvestai-ui/issues",
    },
)