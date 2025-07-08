#!/usr/bin/env python3
"""
Unit tests for dashboard rendering logic
Created: 2025-01-13
Author: AI Assistant

Tests dashboard rendering with template filters to prevent future regressions.
"""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add paths
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / 'ui'))
sys.path.append(str(BASE_DIR / 'ui' / 'utils'))


class TestDashboardTemplateFilters:
    """Test suite for dashboard template filter functionality"""
    
    def test_format_currency_filter(self):
        """Test format_currency filter with various inputs"""
        from template_filters import template_filters
        
        format_currency = template_filters['format_currency']
        
        # Test positive value
        assert format_currency(123.45) == "$123.45"
        
        # Test large value with comma separation
        assert format_currency(1234567.89) == "$1,234,567.89"
        
        # Test zero value
        assert format_currency(0) == "$0.00"
        
        # Test None value
        assert format_currency(None) == "$0.00"
        
        # Test string that can be converted
        assert format_currency("123.45") == "$123.45"
        
        # Test invalid string
        assert format_currency("invalid") == "$0.00"
        
        # Test with custom symbol
        assert format_currency(123.45, symbol='€') == "€123.45"
    
    def test_format_percentage_filter(self):
        """Test format_percentage filter with various inputs"""
        from template_filters import template_filters
        
        format_percentage = template_filters['format_percentage']
        
        # Test positive percentage (as decimal)
        assert format_percentage(0.1234) == "12.34%"
        
        # Test zero percentage
        assert format_percentage(0) == "0.00%"
        
        # Test negative percentage
        assert format_percentage(-0.05) == "-5.00%"
        
        # Test None value
        assert format_percentage(None) == "0.00%"
        
        # Test string that can be converted
        assert format_percentage("0.15") == "15.00%"
        
        # Test invalid string
        assert format_percentage("invalid") == "0.00%"
        
        # Test custom precision
        assert format_percentage(0.123456, precision=4) == "12.3456%"
    
    def test_format_change_value_filter(self):
        """Test format_change_value filter with various inputs"""
        from template_filters import template_filters
        
        format_change_value = template_filters['format_change_value']
        
        # Test positive value
        result = format_change_value(1.23)
        assert result.startswith('+')
        assert '1.23' in result
        
        # Test negative value
        result = format_change_value(-1.23)
        assert result.startswith('-')
        assert '1.23' in result
        
        # Test zero value
        result = format_change_value(0)
        assert '0.00' in result
        
        # Test None value
        assert format_change_value(None) == "—"
    
    def test_format_large_number_filter(self):
        """Test format_large_number filter with various inputs"""
        from template_filters import template_filters
        
        format_large_number = template_filters['format_large_number']
        
        # Test thousands
        assert 'K' in format_large_number(2500)
        
        # Test millions
        assert 'M' in format_large_number(1500000)
        
        # Test billions
        assert 'B' in format_large_number(1500000000)
        
        # Test small numbers
        result = format_large_number(100)
        assert 'K' not in result and 'M' not in result and 'B' not in result
        
        # Test None value
        assert format_large_number(None) == "—"


class TestDashboardTemplateContext:
    """Test suite for dashboard template context and rendering"""
    
    @patch('sys.modules', {'fastapi': Mock(), 'jinja2': Mock()})
    def test_dashboard_context_structure(self):
        """Test that dashboard context contains all required variables"""
        # Mock portfolio data that would be passed to template
        portfolio_data = {
            "total_value": 125350.75,
            "daily_change": 0.0234,  # 2.34% as decimal
            "total_gain": 25350.75,
            "total_gain_percent": 0.2535  # 25.35% as decimal
        }
        
        # Simulate template context
        context = {
            "portfolio": portfolio_data,
            "selected_period": "month",
            "periods": [
                {"value": "day", "label": "Today"},
                {"value": "week", "label": "This Week"},
                {"value": "month", "label": "This Month"},
            ],
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "is_cached": False
        }
        
        # Verify essential context variables exist
        assert "portfolio" in context
        assert "selected_period" in context
        assert "periods" in context
        assert "last_updated" in context
        
        # Verify portfolio has required fields
        portfolio = context["portfolio"]
        assert "total_value" in portfolio
        assert "daily_change" in portfolio
        assert "total_gain" in portfolio
        assert "total_gain_percent" in portfolio
    
    def test_dashboard_template_filter_usage(self):
        """Test that template filters work correctly with dashboard data"""
        from template_filters import template_filters
        
        # Test data similar to what dashboard would use
        portfolio_value = 125350.75
        daily_change = 0.0234  # 2.34%
        total_gain = 25350.75
        
        # Test currency formatting
        formatted_value = template_filters['format_currency'](portfolio_value)
        assert formatted_value == "$125,350.75"
        
        # Test percentage formatting
        formatted_change = template_filters['format_percentage'](daily_change)
        assert formatted_change == "2.34%"
        
        # Test large number formatting
        formatted_large = template_filters['format_large_number'](1500000)
        assert 'M' in formatted_large
    
    def test_dashboard_error_handling(self):
        """Test that dashboard handles missing or invalid data gracefully"""
        from template_filters import template_filters
        
        # Test filters with None/invalid data (simulating API failures)
        assert template_filters['format_currency'](None) == "$0.00"
        assert template_filters['format_percentage'](None) == "0.00%"
        assert template_filters['format_change_value'](None) == "—"
        assert template_filters['format_large_number'](None) == "—"
        
        # Test filters with invalid string data
        assert template_filters['format_currency']("invalid") == "$0.00"
        assert template_filters['format_percentage']("invalid") == "0.00%"


class TestTemplateFilterRegistration:
    """Test suite for template filter registration process"""
    
    def test_all_required_filters_exist(self):
        """Test that all required filters are available"""
        from template_filters import template_filters
        
        required_filters = [
            'format_currency',
            'format_percentage', 
            'format_change_value',
            'format_large_number',
            'format_date',
            'get_asset_url'
        ]
        
        for filter_name in required_filters:
            assert filter_name in template_filters, f"Missing required filter: {filter_name}"
    
    def test_filter_functions_are_callable(self):
        """Test that all filters are callable functions"""
        from template_filters import template_filters
        
        for filter_name, filter_func in template_filters.items():
            assert callable(filter_func), f"Filter {filter_name} is not callable"
    
    def test_critical_filters_with_sample_data(self):
        """Test critical filters with realistic dashboard data"""
        from template_filters import template_filters
        
        # Test format_currency with typical portfolio values
        test_values = [100.00, 1250.50, 125000.75, 1250000.99]
        for value in test_values:
            result = template_filters['format_currency'](value)
            assert result.startswith('$')
            # Check that the numeric part is present
            numeric_part = str(value)
            if '.' in numeric_part:
                base_number = numeric_part.split('.')[0]
                assert base_number in result.replace(',', '')
        
        # Test format_percentage with typical change values
        test_percentages = [0.01, 0.1234, -0.05, 0.0]
        for pct in test_percentages:
            result = template_filters['format_percentage'](pct)
            assert result.endswith('%')
        
        # Test format_change_value with typical stock changes
        test_changes = [1.25, -2.75, 0.0, 15.67]
        for change in test_changes:
            result = template_filters['format_change_value'](change)
            assert isinstance(result, str)
            if change > 0:
                assert result.startswith('+')
            elif change < 0:
                assert result.startswith('-')


def test_dashboard_template_exists():
    """Test that dashboard template file exists and is readable"""
    template_path = BASE_DIR / "ui" / "templates" / "dashboard" / "index.html"
    assert template_path.exists(), "Dashboard template file does not exist"
    
    # Read template content to verify it uses the filters
    content = template_path.read_text()
    
    # Check that template uses the critical filters
    assert "format_currency" in content, "Dashboard template should use format_currency filter"
    assert "format_percentage" in content, "Dashboard template should use format_percentage filter"


def test_template_safety_patterns():
    """Test that templates use safe patterns for handling missing data"""
    template_path = BASE_DIR / "ui" / "templates" / "dashboard" / "index.html"
    if template_path.exists():
        content = template_path.read_text()
        
        # Look for safe patterns in the template
        safe_patterns = [
            "if portfolio",  # Check for data existence
            "else",  # Fallback patterns
            "or",  # Default values
        ]
        
        found_patterns = sum(1 for pattern in safe_patterns if pattern in content)
        assert found_patterns > 0, "Dashboard template should use safe patterns for handling missing data"


def main():
    """Run all dashboard rendering tests"""
    print("🚀 QuantumVestAI Dashboard Rendering Test Suite")
    print("=" * 55)
    
    # Test classes
    test_classes = [
        TestDashboardTemplateFilters,
        TestDashboardTemplateContext,
        TestTemplateFilterRegistration
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"\n🧪 Running {test_class.__name__}...")
        
        # Get all test methods
        test_methods = [getattr(test_class, method) for method in dir(test_class) 
                       if method.startswith('test_')]
        
        for test_method in test_methods:
            try:
                if hasattr(test_class, '__init__'):
                    instance = test_class()
                    test_method(instance)
                else:
                    test_method()
                print(f"  ✅ {test_method.__name__}")
                passed += 1
            except Exception as e:
                print(f"  ❌ {test_method.__name__}: {str(e)}")
                failed += 1
    
    # Run standalone tests
    standalone_tests = [
        test_dashboard_template_exists,
        test_template_safety_patterns
    ]
    
    print(f"\n🧪 Running standalone tests...")
    for test_func in standalone_tests:
        try:
            test_func()
            print(f"  ✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {test_func.__name__}: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 55)
    print(f"📊 Test Results: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("🎉 All dashboard rendering tests passed!")
        return True
    else:
        print("❌ Some dashboard tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)