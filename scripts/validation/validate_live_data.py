#!/usr/bin/env python3
"""
Live Data Validation Script

This script validates that the QuantumVestAI application is properly configured to use
only live market data and has no fallback to mock or demo data.

Usage:
    python validate_live_data.py

Author: AI Assistant
Date: August 4, 2025
"""

import os
import sys
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_file_for_mock_patterns(file_path, patterns):
    """Check a file for patterns indicating mock data usage."""
    if not os.path.exists(file_path):
        logger.warning(f"File not found: {file_path}")
        return []
    
    issues = []
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            content = file.read()
            line_number = 1
            for line in content.split('\n'):
                for pattern in patterns:
                    if pattern in line.lower() and not line.strip().startswith('#') and not line.strip().startswith('//'):
                        # Ignore comments about removing mock data or valid imports
                        if not any(ignore in line.lower() for ignore in ["no mock", "not use mock", "no fallback", "removed mock"]):
                            issues.append({
                                'file': file_path,
                                'line': line_number,
                                'content': line.strip(),
                                'pattern': pattern
                            })
                line_number += 1
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
    
    return issues

def check_settings_files():
    """Check settings files for proper configuration."""
    settings_issues = []
    
    # Check API settings
    api_settings = Path('/Users/gayatri/QuantumVestAI_App_Source_Code/ai-stock-platform/api/core/config/settings.py')
    if api_settings.exists():
        with open(api_settings, 'r', encoding='utf-8') as file:
            content = file.read()
            if 'ENABLE_REAL_DATA: bool = Field(default=False' in content:
                settings_issues.append({
                    'file': str(api_settings),
                    'issue': 'ENABLE_REAL_DATA is set to False by default',
                    'severity': 'High'
                })
    
    # Check K8s deployment files
    k8s_files = [
        '/Users/gayatri/QuantumVestAI_App_Source_Code/ci-cd/k8s/ui-deployment.yaml',
        '/Users/gayatri/QuantumVestAI_App_Source_Code/ci-cd/k8s/dev/04-api-deployment.yaml'
    ]
    
    for k8s_file in k8s_files:
        if os.path.exists(k8s_file):
            with open(k8s_file, 'r', encoding='utf-8') as file:
                content = file.read()
                if 'ENABLE_REAL_DATA' in content and '"false"' in content.lower():
                    settings_issues.append({
                        'file': k8s_file,
                        'issue': 'ENABLE_REAL_DATA is set to "false" in K8s deployment',
                        'severity': 'High'
                    })
    
    return settings_issues

def validate_live_data_usage():
    """Main validation function to check for mock/demo data usage."""
    root_dir = Path('/Users/gayatri/QuantumVestAI_App_Source_Code')
    
    # Define patterns that might indicate mock data
    mock_patterns = [
        'mock_data', 
        'demo_data', 
        'use_mock = true', 
        'use_mock=true',
        'fallback to mock', 
        'demo_stocks_db',
        'mock.', 
        '.mock(',
        'generate_mock'
    ]
    
    # Files and directories to skip
    skip_patterns = [
        'test_', 
        'tests/',
        '/tests/', 
        '.git/', 
        '__pycache__/',
        '.md',
        '.log',
        'validate_live_data.py'  # Skip this validation script
    ]
    
    all_issues = []
    settings_issues = check_settings_files()
    
    if settings_issues:
        all_issues.extend(settings_issues)
        logger.warning(f"Found {len(settings_issues)} issues in settings files")
    
    # Walk through the codebase
    for path in root_dir.glob('**/*'):
        # Skip directories and non-code files
        if path.is_dir() or not path.is_file():
            continue
            
        # Skip files matching skip patterns
        if any(skip in str(path) for skip in skip_patterns):
            continue
            
        # Only check code files
        if path.suffix.lower() not in ['.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.yaml', '.yml']:
            continue
            
        # Check file for mock patterns
        file_issues = check_file_for_mock_patterns(str(path), mock_patterns)
        if file_issues:
            all_issues.extend(file_issues)
            logger.warning(f"Found {len(file_issues)} potential issues in {path}")
    
    # Print summary
    if all_issues:
        logger.error(f"Found {len(all_issues)} potential issues with mock/demo data usage")
        print("\nDetailed Issues:")
        for i, issue in enumerate(all_issues, 1):
            if 'line' in issue:
                print(f"{i}. File: {issue['file']}, Line: {issue['line']}")
                print(f"   Pattern: {issue['pattern']}")
                print(f"   Content: {issue['content']}")
            else:
                print(f"{i}. File: {issue['file']}")
                print(f"   Issue: {issue['issue']}")
                print(f"   Severity: {issue['severity']}")
            print()
        
        print("\nRecommendations:")
        print("1. Update any remaining files to remove mock data generation")
        print("2. Ensure error handling is appropriate when live data cannot be fetched")
        print("3. Add validation tests to verify real data is being used")
        return False
    else:
        logger.info("Success! No mock/demo data usage found.")
        print("\nValidation complete. The application is properly configured to use only live market data.")
        return True

if __name__ == "__main__":
    success = validate_live_data_usage()
    sys.exit(0 if success else 1)
