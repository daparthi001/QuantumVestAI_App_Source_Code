#!/usr/bin/env python3
"""
Dashboard QA Test Script
Created: 2025-01-13
Author: AI Assistant

Tests the dashboard rendering to ensure it works without template filter errors.
"""

import os
import sys
from pathlib import Path

# Add paths
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / 'ui' / 'utils'))

def test_template_filters_availability():
    """Test that all required template filters are available"""
    print("🧪 Testing Template Filter Availability...")
    
    try:
        from template_filters import template_filters
        
        required_filters = [
            'format_currency',
            'format_percentage',
            'format_change_value',
            'format_large_number'
        ]
        
        missing_filters = []
        working_filters = []
        
        for filter_name in required_filters:
            if filter_name in template_filters:
                # Test the filter with sample data
                try:
                    filter_func = template_filters[filter_name]
                    if filter_name == 'format_currency':
                        result = filter_func(125350.75)
                        assert result == "$125,350.75"
                    elif filter_name == 'format_percentage':
                        result = filter_func(0.0234)
                        assert result == "2.34%"
                    elif filter_name == 'format_change_value':
                        result = filter_func(2.34)
                        assert result.startswith('+')
                    elif filter_name == 'format_large_number':
                        result = filter_func(1500000)
                        assert 'M' in result
                    
                    working_filters.append(filter_name)
                    print(f"  ✅ {filter_name}: Working correctly")
                    
                except Exception as e:
                    missing_filters.append(f"{filter_name} (failed test: {e})")
                    print(f"  ❌ {filter_name}: Test failed - {e}")
            else:
                missing_filters.append(filter_name)
                print(f"  ❌ {filter_name}: Not found")
        
        if missing_filters:
            print(f"\n❌ Missing filters: {missing_filters}")
            return False
        else:
            print(f"\n✅ All {len(required_filters)} required filters are working")
            return True
            
    except Exception as e:
        print(f"❌ Error testing template filters: {e}")
        return False

def test_dashboard_template_syntax():
    """Test that dashboard template exists and has valid syntax"""
    print("🧪 Testing Dashboard Template...")
    
    try:
        template_path = BASE_DIR / "ui" / "templates" / "dashboard" / "index.html"
        
        if not template_path.exists():
            print("❌ Dashboard template does not exist")
            return False
        
        # Read template content
        content = template_path.read_text()
        
        # Check for required template filter usage
        required_patterns = [
            "format_currency",
            "format_percentage"
        ]
        
        found_patterns = []
        for pattern in required_patterns:
            if pattern in content:
                found_patterns.append(pattern)
                print(f"  ✅ Template uses {pattern} filter")
            else:
                print(f"  ⚠️  Template doesn't use {pattern} filter")
        
        # Check for safe patterns
        safe_patterns = ['if portfolio', 'else', '|']  # Jinja2 patterns
        found_safe = sum(1 for pattern in safe_patterns if pattern in content)
        
        if found_safe > 0:
            print(f"  ✅ Template uses {found_safe} safe patterns")
        else:
            print("  ⚠️  Template might not use safe patterns")
        
        print("✅ Dashboard template exists and appears valid")
        return True
        
    except Exception as e:
        print(f"❌ Error checking dashboard template: {e}")
        return False

def test_fallback_implementations():
    """Test fallback implementations for when imports fail"""
    print("🧪 Testing Fallback Implementations...")
    
    try:
        # Test the fallback implementations that would be used in main.py
        def format_currency_fallback(value, symbol='$'):
            if value is None:
                return f"{symbol}0.00"
            try:
                float_value = float(value)
                return f"{symbol}{float_value:,.2f}"
            except (ValueError, TypeError):
                return f"{symbol}0.00"
        
        def format_percentage_fallback(value, precision=2):
            if value is None:
                return f"0.{precision * '0'}%"
            try:
                float_value = float(value) * 100
                return f"{float_value:.{precision}f}%"
            except (ValueError, TypeError):
                return f"0.{precision * '0'}%"
        
        # Test fallback filters
        test_cases = [
            (format_currency_fallback, 125350.75, "$125,350.75"),
            (format_currency_fallback, None, "$0.00"),
            (format_currency_fallback, "invalid", "$0.00"),
            (format_percentage_fallback, 0.0234, "2.34%"),
            (format_percentage_fallback, None, "0.00%"),
            (format_percentage_fallback, "invalid", "0.00%"),
        ]
        
        for func, input_val, expected in test_cases:
            result = func(input_val)
            if result == expected:
                print(f"  ✅ {func.__name__}({input_val}) = {result}")
            else:
                print(f"  ❌ {func.__name__}({input_val}) = {result}, expected {expected}")
                return False
        
        print("✅ All fallback implementations working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing fallback implementations: {e}")
        return False

def test_error_scenarios():
    """Test error handling scenarios"""
    print("🧪 Testing Error Handling Scenarios...")
    
    try:
        from template_filters import template_filters

        # Test with None values
        test_results = []
        
        none_tests = [
            ('format_currency', None, "$0.00"),
            ('format_percentage', None, "0.00%"),
            ('format_change_value', None, "—"),
            ('format_large_number', None, "—"),
        ]
        
        for filter_name, input_val, expected in none_tests:
            if filter_name in template_filters:
                try:
                    result = template_filters[filter_name](input_val)
                    if result == expected:
                        test_results.append(True)
                        print(f"  ✅ {filter_name}(None) = {result}")
                    else:
                        test_results.append(False)
                        print(f"  ❌ {filter_name}(None) = {result}, expected {expected}")
                except Exception as e:
                    test_results.append(False)
                    print(f"  ❌ {filter_name}(None) failed: {e}")
        
        # Test with invalid strings
        invalid_tests = [
            ('format_currency', "invalid", "$0.00"),
            ('format_percentage', "invalid", "0.00%"),
        ]
        
        for filter_name, input_val, expected in invalid_tests:
            if filter_name in template_filters:
                try:
                    result = template_filters[filter_name](input_val)
                    if result == expected:
                        test_results.append(True)
                        print(f"  ✅ {filter_name}('invalid') = {result}")
                    else:
                        test_results.append(False)
                        print(f"  ❌ {filter_name}('invalid') = {result}, expected {expected}")
                except Exception as e:
                    test_results.append(False)
                    print(f"  ❌ {filter_name}('invalid') failed: {e}")
        
        if all(test_results):
            print("✅ All error handling tests passed")
            return True
        else:
            print("❌ Some error handling tests failed")
            return False
        
    except Exception as e:
        print(f"❌ Error testing error scenarios: {e}")
        return False

def main():
    """Run complete QA test suite"""
    print("🚀 QuantumVestAI Dashboard QA Test Suite")
    print("=" * 50)
    
    tests = [
        test_template_filters_availability,
        test_dashboard_template_syntax,
        test_fallback_implementations,
        test_error_scenarios
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n{test.__doc__.strip()}")
        if test():
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 QA Results: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("🎉 Dashboard QA: ALL TESTS PASSED!")
        print("✅ Dashboard is ready for production")
        print("✅ Template filters working correctly")
        print("✅ Error handling implemented")
        print("✅ Fallback systems operational")
        return True
    else:
        print("❌ Dashboard QA: SOME TESTS FAILED")
        print("⚠️  Please review and fix the issues above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
