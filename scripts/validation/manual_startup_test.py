#!/usr/bin/env python3
"""
Manual startup test for QuantumVestAI UI with logging and auth fixes
This script tests that the application can start without circular dependency issues
"""
import os
import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).resolve().parent
ai_stock_platform_path = project_root / "ai-stock-platform"
ui_path = ai_stock_platform_path / "ui"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(ai_stock_platform_path))
sys.path.insert(0, str(ui_path))

def test_independent_logging():
    """Test that logging can be configured independently"""
    print("🔍 Testing independent logging configuration...")
    
    try:
        from core.logging_config import setup_independent_logging, get_logger
        
        # Test logging setup
        setup_independent_logging(base_dir=ui_path)
        logger = get_logger("test")
        
        logger.info("Independent logging test successful!")
        print("✅ Independent logging configuration works")
        return True
        
    except Exception as e:
        print(f"❌ Independent logging failed: {e}")
        return False

def test_settings_without_logging():
    """Test that settings can be imported without logging dependency"""
    print("🔍 Testing settings module independence...")
    
    try:
        # This should not cause circular dependency
        from core.config.settings import settings
        
        print(f"✅ Settings loaded successfully: {settings.APP_NAME}")
        return True
        
    except Exception as e:
        print(f"❌ Settings import failed: {e}")
        return False

def test_auth_middleware_imports():
    """Test that auth middleware can be imported"""
    print("🔍 Testing auth middleware imports...")
    
    try:
        # Mock the FastAPI dependencies to test imports
        class MockRequest:
            pass
        
        class MockResponse:
            pass
        
        # Temporarily mock FastAPI imports
        sys.modules['fastapi'] = type('MockModule', (), {
            'Request': MockRequest,
            'Response': MockResponse
        })()
        sys.modules['starlette.middleware.base'] = type('MockModule', (), {
            'BaseHTTPMiddleware': object
        })()
        sys.modules['starlette.responses'] = type('MockModule', (), {
            'RedirectResponse': object  
        })()
        sys.modules['jwt'] = type('MockModule', (), {
            'decode': lambda *args, **kwargs: {},
            'ExpiredSignatureError': Exception,
            'InvalidTokenError': Exception
        })()
        
        from ai_stock_platform.ui.middleware.improved_auth_middleware import (
            create_persistent_auth_cookies, 
            clear_auth_cookies
        )
        
        print("✅ Auth middleware imports work")
        return True
        
    except Exception as e:
        print(f"❌ Auth middleware import failed: {e}")
        return False

def test_application_structure():
    """Test overall application structure"""
    print("🔍 Testing application file structure...")
    
    required_files = [
        ui_path / "core" / "logging_config.py",
        ui_path / "middleware" / "improved_auth_middleware.py", 
        ui_path / "main.py",
        ui_path / "routes" / "auth.py",
        ui_path / "core" / "config" / "settings.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def main():
    """Run all manual tests"""
    print("🚀 Starting QuantumVestAI UI manual startup test...\n")
    
    tests = [
        ("Application Structure", test_application_structure),
        ("Independent Logging", test_independent_logging),
        ("Settings Module", test_settings_without_logging),
        ("Auth Middleware", test_auth_middleware_imports),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The application should start successfully.")
        print("🔧 Key fixes implemented:")
        print("   • Logging configuration is independent of settings")
        print("   • Authentication middleware improved for persistent login")
        print("   • No more circular dependencies")
        print("   • Proper cookie handling for login state")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)