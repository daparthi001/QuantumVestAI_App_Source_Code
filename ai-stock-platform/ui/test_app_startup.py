#!/usr/bin/env python3
"""
Startup test for QuantumVestAI UI to validate template filters
"""

import os
import sys

sys.path.append('.')

def test_app_startup():
    """Test application startup with template filters"""
    print("Testing QuantumVestAI UI Application Startup...")
    
    try:
        # Test minimal FastAPI app creation
        from datetime import datetime
        from pathlib import Path

        from fastapi import FastAPI
        from fastapi.templating import Jinja2Templates

        # Create app similar to main.py
        BASE_DIR = Path('.').resolve()
        app = FastAPI(title="QuantumVestAI UI Test")
        
        # Setup templates
        templates = Jinja2Templates(directory=str(BASE_DIR))
        app.state.templates = templates
        
        print("✓ FastAPI app created")
        print("✓ Templates configured")
        
        # Test template filter registration (main.py style)
        try:
            from utils.template_filters import (get_template_filter_status,
                                                register_filters,
                                                validate_template_filters)
            
            filter_success = register_filters(app)
            print(f"✓ Template filter registration: {filter_success}")
            
            if filter_success:
                validation_success = validate_template_filters(app)
                print(f"✓ Template filter validation: {validation_success}")
                
                status = get_template_filter_status()
                print(f"✓ Template filter status: {status['total_filters']} filters ready")
                
                # Check critical filters specifically
                critical_filters = ['format_change_value', 'format_large_number', 'format_currency']
                all_critical_available = True
                
                for filter_name in critical_filters:
                    if filter_name in app.state.templates.env.filters:
                        print(f"✓ Critical filter {filter_name} available")
                    else:
                        print(f"✗ Critical filter {filter_name} missing")
                        all_critical_available = False
                
                if all_critical_available:
                    print("✓ All critical template filters are available")
                else:
                    print("✗ Some critical template filters are missing")
                    return False
                
                # Test filter functionality
                print("\n--- Testing Filter Functionality ---")
                
                # Test format_change_value
                filter_func = app.state.templates.env.filters['format_change_value']
                test_result = filter_func(25.75)
                print(f"✓ format_change_value(25.75) = {test_result}")
                
                # Test format_large_number
                filter_func = app.state.templates.env.filters['format_large_number']
                test_result = filter_func(2500000)
                print(f"✓ format_large_number(2500000) = {test_result}")
                
                # Test format_currency
                filter_func = app.state.templates.env.filters['format_currency']
                test_result = filter_func(1234.56)
                print(f"✓ format_currency(1234.56) = {test_result}")
                
                print("\n🎉 Application startup test PASSED!")
                print("   The template filter errors should now be resolved.")
                return True
                
            else:
                print("✗ Template filter registration failed")
                return False
                
        except Exception as filter_error:
            print(f"✗ Template filter setup error: {filter_error}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"✗ Application startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_startup()
    if success:
        print("\n✅ SUCCESS: Template filter errors are fixed!")
        print("   The application should now start without 'No filter named format_change_value' errors.")
    else:
        print("\n❌ FAILURE: Template filter issues remain.")
    
    sys.exit(0 if success else 1)
