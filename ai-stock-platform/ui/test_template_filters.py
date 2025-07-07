#!/usr/bin/env python3
"""
Test script for template filters
Tests the template filter registration and validation functionality
"""

import sys
import os
sys.path.append('.')

def test_template_filters():
    """Test template filter functionality"""
    print("Testing QuantumVestAI Template Filters...")
    
    try:
        # Import template filters
        import utils.template_filters as tf_module
        print("✓ Template filters module imported")
        
        # Test individual filters
        print("\n--- Testing Individual Filters ---")
        
        # Test format_change_value (the problematic one)
        if 'format_change_value' in tf_module.template_filters:
            func = tf_module.template_filters['format_change_value']
            test_cases = [10.5, -5.25, 0, None]
            for value in test_cases:
                result = func(value)
                print(f"✓ format_change_value({value}) = {result}")
        else:
            print("✗ format_change_value filter missing")
            return False
        
        # Test format_large_number (the other problematic one)
        if 'format_large_number' in tf_module.template_filters:
            func = tf_module.template_filters['format_large_number']
            test_cases = [1500, 1500000, 1500000000, 1500000000000]
            for value in test_cases:
                result = func(value)
                print(f"✓ format_large_number({value}) = {result}")
        else:
            print("✗ format_large_number filter missing")
            return False
        
        # Test FastAPI integration
        print("\n--- Testing FastAPI Integration ---")
        
        from fastapi import FastAPI
        from fastapi.templating import Jinja2Templates
        
        app = FastAPI()
        templates = Jinja2Templates(directory='.')
        app.state.templates = templates
        
        # Test registration
        success = tf_module.register_filters(app)
        print(f"✓ Filter registration: {success}")
        
        if not success:
            print("✗ Filter registration failed")
            return False
        
        # Test validation
        validation = tf_module.validate_template_filters(app)
        print(f"✓ Filter validation: {validation}")
        
        if not validation:
            print("✗ Filter validation failed")
            return False
        
        # Test filter availability in Jinja2 environment
        critical_filters = ['format_change_value', 'format_large_number', 'format_currency', 'format_percentage']
        
        for filter_name in critical_filters:
            if filter_name in app.state.templates.env.filters:
                print(f"✓ {filter_name} available in Jinja2 environment")
            else:
                print(f"✗ {filter_name} missing from Jinja2 environment")
                return False
        
        print("\n🎉 All template filter tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_template_filters()
    sys.exit(0 if success else 1)