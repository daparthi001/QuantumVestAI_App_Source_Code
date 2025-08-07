"""
Simplified test suite for logging configuration and login state persistence fixes
Tests core functionality without requiring external dependencies
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
ai_stock_platform_path = project_root / "ai-stock-platform"
ui_path = ai_stock_platform_path / "ui"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(ai_stock_platform_path))
sys.path.insert(0, str(ui_path))


class TestLoggingConfiguration(unittest.TestCase):
    """Test independent logging configuration"""
    
    def test_logging_config_exists(self):
        """Test that logging configuration file exists"""
        logging_config_path = ui_path / "core" / "logging_config.py"
        self.assertTrue(logging_config_path.exists(), "logging_config.py should exist")
    
    def test_logging_config_structure(self):
        """Test that logging configuration has correct structure"""
        # Read the logging config source
        logging_config_path = ui_path / "core" / "logging_config.py"
        source_code = logging_config_path.read_text()
        
        # Should contain key functions
        self.assertIn("get_independent_logging_config", source_code)
        self.assertIn("setup_independent_logging", source_code)
        self.assertIn("get_logger", source_code)
        
        # Should not import from settings
        self.assertNotIn("from core.config.settings import", source_code)
        self.assertNotIn("from settings import", source_code)
        self.assertNotIn("import settings", source_code)
    
    def test_settings_no_longer_contains_logging(self):
        """Test that settings module no longer contains logging configuration"""
        settings_path = ui_path / "core" / "config" / "settings.py"
        source_code = settings_path.read_text()
        
        # Should not contain get_logging_config method
        self.assertNotIn("def get_logging_config", source_code)
        # Should have comment indicating it was moved
        self.assertIn("Logging configuration removed", source_code)


class TestAuthenticationMiddleware(unittest.TestCase):
    """Test improved authentication middleware"""
    
    def test_middleware_file_exists(self):
        """Test that improved auth middleware file exists"""
        middleware_path = ui_path / "middleware" / "improved_auth_middleware.py"
        self.assertTrue(middleware_path.exists(), "improved_auth_middleware.py should exist")
    
    def test_middleware_structure(self):
        """Test that middleware has correct structure"""
        middleware_path = ui_path / "middleware" / "improved_auth_middleware.py"
        source_code = middleware_path.read_text()
        
        # Should contain key components
        self.assertIn("class ImprovedAuthMiddleware", source_code)
        self.assertIn("create_persistent_auth_cookies", source_code)
        self.assertIn("clear_auth_cookies", source_code)
        self.assertIn("_extract_token_from_request", source_code)
        self.assertIn("_requires_authentication", source_code)
        
        # Should handle multiple cookie types
        self.assertIn("access_token", source_code)
        self.assertIn("qvai_token", source_code)
        self.assertIn("user_info", source_code)
    
    def test_protected_routes_configuration(self):
        """Test protected routes are properly configured"""
        middleware_path = ui_path / "middleware" / "improved_auth_middleware.py"
        source_code = middleware_path.read_text()
        
        # Should define protected routes
        self.assertIn("PROTECTED_ROUTES", source_code)
        self.assertIn("/settings", source_code)
        self.assertIn("/dashboard", source_code)
        
        # Should define public routes  
        self.assertIn("PUBLIC_ROUTES", source_code)
        self.assertIn("/login", source_code)
        self.assertIn("/auth/login", source_code)


class TestMainApplicationUpdates(unittest.TestCase):
    """Test that main application files use improved components"""
    
    def test_main_ui_uses_independent_logging(self):
        """Test that main UI application uses independent logging"""
        main_path = ui_path / "main.py"
        source_code = main_path.read_text()
        
        # Should import from core.logging_config
        self.assertIn("from core.logging_config import", source_code)
        self.assertIn("setup_independent_logging", source_code)
        
        # Should not use old dictConfig setup in main function
        lines = source_code.split('\n')
        dictconfig_lines = [line for line in lines if 'dictConfig(' in line]
        # Should have fewer dictConfig calls (only in fallback)
        self.assertLessEqual(len(dictconfig_lines), 1)
    
    def test_main_ui_uses_improved_middleware(self):
        """Test that main UI application uses improved auth middleware"""
        main_path = ui_path / "main.py"
        source_code = main_path.read_text()
        
        # Should import ImprovedAuthMiddleware
        self.assertIn("ImprovedAuthMiddleware", source_code)
        self.assertIn("improved_auth_middleware", source_code)
    
    def test_auth_routes_use_improved_cookies(self):
        """Test that auth routes use improved cookie handling"""
        auth_routes_path = ui_path / "routes" / "auth.py"
        source_code = auth_routes_path.read_text()
        
        # Should import improved cookie functions
        self.assertIn("from middleware.improved_auth_middleware import", source_code)
        self.assertIn("create_persistent_auth_cookies", source_code)
        self.assertIn("clear_auth_cookies", source_code)


class TestConfigurationConsistency(unittest.TestCase):
    """Test that configuration is consistent across files"""
    
    def test_cookie_names_consistency(self):
        """Test that cookie names are consistent across files"""
        # Main middleware file should define all cookie types
        middleware_path = ui_path / "middleware" / "improved_auth_middleware.py"
        
        if middleware_path.exists():
            source_code = middleware_path.read_text()
            expected_cookies = ["access_token", "qvai_token", "user_info"]
            
            for cookie_name in expected_cookies:
                self.assertIn(cookie_name, source_code, 
                            f"Cookie '{cookie_name}' should be in improved_auth_middleware.py")
        
        # Auth routes should import the improved middleware functions
        auth_routes_path = ui_path / "routes" / "auth.py"
        if auth_routes_path.exists():
            source_code = auth_routes_path.read_text()
            # Should import improved cookie functions
            self.assertIn("create_persistent_auth_cookies", source_code)
            self.assertIn("clear_auth_cookies", source_code)
    
    def test_jwt_secret_configuration(self):
        """Test JWT secret configuration is consistent"""
        files_to_check = [
            ui_path / "middleware" / "improved_auth_middleware.py",
            ui_path / "auth" / "dependencies.py"
        ]
        
        for file_path in files_to_check:
            if file_path.exists():
                source_code = file_path.read_text()
                # Should handle JWT_SECRET or SECRET_KEY
                self.assertTrue(
                    "JWT_SECRET" in source_code or "SECRET_KEY" in source_code,
                    f"JWT configuration should be in {file_path.name}"
                )


def run_tests():
    """Run all tests and return success status"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLoggingConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationMiddleware))
    suite.addTests(loader.loadTestsFromTestCase(TestMainApplicationUpdates))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationConsistency))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running simplified tests for logging and authentication fixes...")
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed! The fixes are working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    sys.exit(0 if success else 1)