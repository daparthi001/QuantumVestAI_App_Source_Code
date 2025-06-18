#!/usr/bin/env python3
"""
QuantumVestAI File Listing Script (Python Version)
Created: 2025-06-18 01:42:05
Author: daparthi001
"""
import os
import subprocess
import datetime
import sys
from pathlib import Path

# ANSI color codes
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
RED = '\033[0;31m'
PURPLE = '\033[0;35m'
NC = '\033[0m'  # No Color

# Define base directories
API_DIR = "api"
UI_DIR = "ui"

def print_header():
    print(f"{GREEN}====================================================={NC}")
    print(f"{GREEN}      QuantumVestAI Project Files Listing{NC}")
    print(f"{GREEN}      Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{NC}")
    print(f"{GREEN}      User: daparthi001{NC}")
    print(f"{GREEN}====================================================={NC}")

def count_stats(directory):
    if not os.path.exists(directory):
        return 0, 0
    
    total_files = 0
    total_lines = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                total_files += 1
                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                    total_lines += sum(1 for _ in f)
    
    return total_files, total_lines

def list_directory(directory, indent="", max_depth=3, current_depth=1):
    if not os.path.exists(directory):
        return
    
    # List directories first
    dirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    dirs.sort()
    
    for dirname in dirs:
        print(f"{indent}{BLUE}📁 {dirname}/{NC}")
        
        if current_depth < max_depth:
            list_directory(
                os.path.join(directory, dirname),
                indent + "  ",
                max_depth,
                current_depth + 1
            )
    
    # Then list files
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files.sort()
    
    for filename in files:
        file_path = os.path.join(directory, filename)
        extension = filename.split('.')[-1] if '.' in filename else ""
        
        # Get file size
        file_size = os.path.getsize(file_path)
        if file_size < 1024:
            size_str = f"{file_size}B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size/1024:.1f}K"
        else:
            size_str = f"{file_size/(1024*1024):.1f}M"
        
        # Color based on file extension
        if extension == "py":
            print(f"{indent}{CYAN}📄 {filename}{NC} {PURPLE}({size_str}){NC}")
        elif extension in ["html", "jinja2"]:
            print(f"{indent}{GREEN}📄 {filename}{NC} {PURPLE}({size_str}){NC}")
        elif extension in ["css", "js"]:
            print(f"{indent}{YELLOW}📄 {filename}{NC} {PURPLE}({size_str}){NC}")
        elif extension in ["json", "yaml", "yml"]:
            print(f"{indent}{PURPLE}📄 {filename}{NC} {PURPLE}({size_str}){NC}")
        else:
            print(f"{indent}{NC}📄 {filename}{NC} {PURPLE}({size_str}){NC}")

def check_dependencies():
    print(f"\n{GREEN}============== Dependency Status =============={NC}")
    print(f"{YELLOW}Checking for required packages...{NC}")
    
    required_packages = ["aiohttp", "requests", "fastapi", "uvicorn", "jinja2"]
    
    for package in required_packages:
        try:
            # Try to import the package
            __import__(package)
            # Get version using pip
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package],
                capture_output=True,
                text=True
            )
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                    print(f"{GREEN}✓ {package} {YELLOW}(v{version}){NC} is installed")
                    break
        except ImportError:
            print(f"{RED}✗ {package} is NOT installed{NC}")

def main():
    print_header()
    
    # Process API directory
    print(f"\n{GREEN}============== API Directory =============={NC}")
    print(f"{YELLOW}Path:{NC} {API_DIR}\n")
    
    if os.path.exists(API_DIR):
        api_files, api_lines = count_stats(API_DIR)
        print(f"{YELLOW}Total Python Files:{NC} {api_files}")
        print(f"{YELLOW}Total Lines of Code:{NC} {api_lines}")
        
        print(f"\n{YELLOW}File Structure:{NC}")
        print(f"{BLUE}📁 api/{NC}")
        list_directory(API_DIR, "  ")
    else:
        print(f"{RED}API directory not found at {API_DIR}{NC}")
    
    # Process UI directory
    print(f"\n{GREEN}============== UI Directory =============={NC}")
    print(f"{YELLOW}Path:{NC} {UI_DIR}\n")
    
    if os.path.exists(UI_DIR):
        ui_files, ui_lines = count_stats(UI_DIR)
        print(f"{YELLOW}Total Python Files:{NC} {ui_files}")
        print(f"{YELLOW}Total Lines of Code:{NC} {ui_lines}")
        
        print(f"\n{YELLOW}File Structure:{NC}")
        print(f"{BLUE}📁 ui/{NC}")
        list_directory(UI_DIR, "  ")
    else:
        print(f"{RED}UI directory not found at {UI_DIR}{NC}")
    
    # Check dependencies
    check_dependencies()
    
    print(f"\n{GREEN}====================================================={NC}")
    print(f"{GREEN}      QuantumVestAI File Listing Complete{NC}")
    print(f"{GREEN}====================================================={NC}")

if __name__ == "__main__":
    main()
