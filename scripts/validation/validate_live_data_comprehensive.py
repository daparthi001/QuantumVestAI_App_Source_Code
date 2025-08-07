#!/usr/bin/env python3
"""
Comprehensive validation script to ensure no demo/mock data patterns remain in the codebase.
Only live data from Alpha Vantage and RapidAPI should be used.
"""

import os
import sys
import re
from pathlib import Path

def find_demo_patterns():
    """Find any remaining demo/mock data patterns."""
    root_dir = Path("ai-stock-platform")
    
    # Enhanced patterns to search for (excluding comments and tests)
    demo_patterns = [
        r'DEMO_\w+\s*=',  # Demo variable assignments
        r'demo_\w+\s*=',  # Demo variable assignments
        r'mock_\w+\s*=',  # Mock variable assignments
        r'(?<!\#.*)"demo"',  # Demo string literals (not in comments)
        r'(?<!\#.*)"mock"',  # Mock string literals (not in comments)
        r'demo.*data',  # Demo data references
        r'mock.*data',  # Mock data references
        r'fallback.*demo',  # Demo fallbacks
        r'fallback.*mock',  # Mock fallbacks
        r'use_mock.*=.*True',  # Mock usage flags
        r'hardcoded.*=',  # Hardcoded values
    ]
    
    issues = []
    
    # Search through Python files
    for py_file in root_dir.rglob("*.py"):
        # Skip test files
        if "test" in str(py_file).lower() or "tests" in str(py_file).lower():
            continue
            
        try:
            content = py_file.read_text()
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Skip empty lines and comments
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                
                for pattern in demo_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append({
                            'file': str(py_file),
                            'line': line_num,
                            'content': line.strip(),
                            'pattern': pattern
                        })
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return issues

def check_api_integration():
    """Check that all controllers use live API calls instead of demo data."""
    controllers_dir = Path("ai-stock-platform/ui/controllers")
    issues = []
    
    # Expected patterns for live API integration
    required_patterns = [
        r'httpx\.AsyncClient',  # HTTP client usage
        r'API_URL',  # API URL references
        r'\.get\(f["\'].*api.*["\']',  # API GET calls
        r'\.post\(f["\'].*api.*["\']',  # API POST calls
    ]
    
    if controllers_dir.exists():
        for controller_file in controllers_dir.glob("*.py"):
            try:
                content = controller_file.read_text()
                
                # Check if the controller has any data handling
                has_data_handling = any(keyword in content.lower() for keyword in 
                    ['forecast', 'dashboard', 'market', 'news', 'portfolio'])
                
                if has_data_handling:
                    # Check for live API integration patterns
                    has_api_integration = any(re.search(pattern, content) for pattern in required_patterns)
                    
                    if not has_api_integration:
                        issues.append({
                            'file': str(controller_file),
                            'issue': 'Controller handles data but does not use live API calls'
                        })
                        
            except Exception as e:
                print(f"Error checking {controller_file}: {e}")
    
    return issues

def check_environment_config():
    """Check that environment configuration enforces live data."""
    env_files = [
        ".env.template",
        ".env.data_sources",
        "ai-stock-platform/.env.template"
    ]
    
    issues = []
    
    for env_file in env_files:
        env_path = Path(env_file)
        if env_path.exists():
            try:
                content = env_path.read_text()
                
                # Check for demo/mock related settings
                if re.search(r'ENABLE_DEMO.*=.*true', content, re.IGNORECASE):
                    issues.append({
                        'file': str(env_path),
                        'issue': 'Environment file enables demo mode'
                    })
                
                # Check that real data is enabled by default
                if re.search(r'ENABLE_REAL_DATA.*=.*false', content, re.IGNORECASE):
                    issues.append({
                        'file': str(env_path),
                        'issue': 'Environment file disables real data by default'
                    })
                    
            except Exception as e:
                print(f"Error reading {env_file}: {e}")
    
    return issues

def main():
    """Main validation function."""
    print("=" * 80)
    print("COMPREHENSIVE VALIDATION: Live Data Implementation")
    print("=" * 80)
    
    all_issues = []
    
    # Check for demo patterns
    print("\n1. Checking for demo/mock data patterns...")
    demo_issues = find_demo_patterns()
    if demo_issues:
        print(f"   Found {len(demo_issues)} demo/mock patterns:")
        for issue in demo_issues[:10]:  # Show first 10
            print(f"     {issue['file']}:{issue['line']} - {issue['content'][:60]}...")
        all_issues.extend(demo_issues)
    else:
        print("   ✅ No demo/mock patterns found")
    
    # Check API integration
    print("\n2. Checking controller API integration...")
    api_issues = check_api_integration()
    if api_issues:
        print(f"   Found {len(api_issues)} API integration issues:")
        for issue in api_issues:
            print(f"     {issue['file']} - {issue['issue']}")
        all_issues.extend(api_issues)
    else:
        print("   ✅ All controllers use live API integration")
    
    # Check environment configuration
    print("\n3. Checking environment configuration...")
    env_issues = check_environment_config()
    if env_issues:
        print(f"   Found {len(env_issues)} environment issues:")
        for issue in env_issues:
            print(f"     {issue['file']} - {issue['issue']}")
        all_issues.extend(env_issues)
    else:
        print("   ✅ Environment configuration enforces live data")
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    if not all_issues:
        print("✅ SUCCESS: All data sources use live APIs!")
        print("✅ No demo/mock data patterns found")
        print("✅ All controllers integrate with live APIs")
        print("✅ Environment configuration enforces live data usage")
        return True
    else:
        print(f"❌ ISSUES FOUND: {len(all_issues)} problems to address")
        print("\nPLEASE FIX:")
        for i, issue in enumerate(all_issues[:20], 1):  # Show top 20 issues
            if 'file' in issue and 'line' in issue:
                print(f"{i:2}. {issue['file']}:{issue['line']} - {issue.get('content', issue.get('issue', ''))}")
            else:
                print(f"{i:2}. {issue['file']} - {issue['issue']}")
        
        if len(all_issues) > 20:
            print(f"... and {len(all_issues) - 20} more issues")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)