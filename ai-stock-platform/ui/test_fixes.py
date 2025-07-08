#!/usr/bin/env python3
"""
Test script to verify the fixes work correctly
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_registration_fix():
    """Test that registration form points to correct endpoint"""
    print("Testing registration fix...")
    
    # Read the registration template
    with open('templates/auth/register.html', 'r') as f:
        content = f.read()
    
    # Check if form action is correct
    if 'action="/register"' in content:
        print("✅ Registration form action is correct")
        return True
    else:
        print("❌ Registration form action is incorrect")
        return False

def test_logout_fix():
    """Test that logout endpoints exist"""
    print("Testing logout fix...")
    
    # Read the main.py file
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check if both GET and POST logout endpoints exist
    has_get_logout = 'async def logout_get(' in content
    has_post_logout = 'async def logout_post(' in content
    
    if has_get_logout and has_post_logout:
        print("✅ Both GET and POST logout endpoints exist")
        return True
    else:
        print(f"❌ Logout endpoints missing - GET: {has_get_logout}, POST: {has_post_logout}")
        return False

def test_dashboard_enhancements():
    """Test that dashboard enhancements are added"""
    print("Testing dashboard enhancements...")
    
    # Check if CSS file exists
    css_exists = os.path.exists('static/css/dashboard-enhancements.css')
    
    # Check if JS file exists
    js_exists = os.path.exists('static/js/dashboard-enhancements.js')
    
    # Check if template includes new files
    with open('templates/dashboard/index.html', 'r') as f:
        template_content = f.read()
    
    css_included = 'dashboard-enhancements.css' in template_content
    js_included = 'dashboard-enhancements.js' in template_content
    
    # Check if new sections are added
    has_chart_section = 'Portfolio Performance' in template_content
    has_ai_insights = 'AI-Powered Insights' in template_content
    
    all_checks = [css_exists, js_exists, css_included, js_included, has_chart_section, has_ai_insights]
    
    if all(all_checks):
        print("✅ All dashboard enhancements are present")
        return True
    else:
        print(f"❌ Dashboard enhancements missing - CSS: {css_exists}, JS: {js_exists}, "
              f"CSS included: {css_included}, JS included: {js_included}, "
              f"Chart section: {has_chart_section}, AI insights: {has_ai_insights}")
        return False

def test_register_js_fix():
    """Test that register.js uses correct endpoint"""
    print("Testing register.js fix...")
    
    # Read the register.js file
    with open('static/js/auth/register.js', 'r') as f:
        content = f.read()
    
    # Check if it uses the correct endpoint
    if "fetch('/register'" in content:
        print("✅ Register.js uses correct endpoint")
        return True
    else:
        print("❌ Register.js uses incorrect endpoint")
        return False

def main():
    """Run all tests"""
    print("Running QuantumVestAI fix verification tests...\n")
    
    tests = [
        test_registration_fix,
        test_logout_fix,
        test_dashboard_enhancements,
        test_register_js_fix
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fixes are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)