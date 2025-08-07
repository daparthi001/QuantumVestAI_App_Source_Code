#!/usr/bin/env python3
"""
Validation script to ensure no mock/demo data patterns remain in the codebase.
Only live data from Alpha Vantage and RapidAPI should be used.
"""

import os
import sys
from pathlib import Path

def find_mock_patterns():
    """Find any remaining mock/demo data patterns."""
    root_dir = Path("ai-stock-platform")
    
    # Patterns to search for (excluding comments)
    mock_patterns = [
        'DEMO_',
        'mock_data',
        'demo_data', 
        'fallback.*mock',
        'mock.*fallback',
        'use_mock.*=.*True',
        'use_mock.*=.*true'
    ]
    
    issues = []
    
    for pattern in mock_patterns:
        print(f"Searching for pattern: {pattern}")
        result = os.system(f"grep -r -n '{pattern}' {root_dir} --include='*.py' | grep -v test | grep -v '#.*{pattern}'")
        if result == 0:  # Found matches
            issues.append(pattern)
    
    return issues

def check_api_settings():
    """Check that API settings enforce live data usage."""
    settings_file = Path("ai-stock-platform/api/core/config/settings.py")
    
    if not settings_file.exists():
        return ["Settings file not found"]
    
    issues = []
    content = settings_file.read_text()
    
    # Check that ENABLE_REAL_DATA defaults to True
    if 'ENABLE_REAL_DATA: bool = Field(default=False' in content:
        issues.append("ENABLE_REAL_DATA should default to True")
    
    # Check that Alpha Vantage key is required (no default)
    if 'ALPHA_VANTAGE_API_KEY.*default=' in content and 'default=None' not in content:
        issues.append("ALPHA_VANTAGE_API_KEY should not have a default value")
    
    # Check that RapidAPI key is configured
    if 'RAPIDAPI_KEY' not in content:
        issues.append("RAPIDAPI_KEY should be configured in settings")
    
    return issues

def main():
    """Main validation function."""
    print("=" * 60)
    print("VALIDATING: No Mock Data - Only Live Data from APIs")
    print("=" * 60)
    
    # Check for mock patterns
    print("\n1. Checking for mock/demo data patterns...")
    mock_issues = find_mock_patterns()
    
    # Check API settings
    print("\n2. Checking API settings...")
    settings_issues = check_api_settings()
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    if not mock_issues and not settings_issues:
        print("✅ SUCCESS: No mock data patterns found!")
        print("✅ All services configured to use live data from Alpha Vantage and RapidAPI")
        return True
    else:
        print("❌ ISSUES FOUND:")
        if mock_issues:
            print(f"  - Mock data patterns: {mock_issues}")
        if settings_issues:
            print(f"  - Settings issues: {settings_issues}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)