"""
Test suite for logging configuration and login state persistence fixes
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
ai_stock_platform_path = project_root / "ai-stock-platform"
ui_path = ai_stock_platform_path / "ui"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(ai_stock_platform_path))
sys.path.insert(0, str(ui_path))


class TestLoggingConfiguration(unittest.TestCase):
    """Test independent logging configuration"""
    
    def test_independent_logging_config(self):
        """Test that logging configuration works independently of settings"""
        # This should not import anything from settings
        from core.logging_config import get_independent_logging_config, setup_independent_logging
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test configuration generation
            config = get_independent_logging_config(base_dir=temp_path, log_level="DEBUG")
            
            # Verify structure
            self.assertIn("version", config)
            self.assertIn("handlers", config)
            self.assertIn("loggers", config)
            self.assertIn("console", config["handlers"])
            self.assertIn("file", config["handlers"])
            
            # Verify log level
            self.assertEqual(config["handlers"]["console"]["level"], "DEBUG")
            
            # Test setup doesn't raise errors
            setup_independent_logging(base_dir=temp_path, log_level="INFO")
            
            # Verify logs directory was created
            self.assertTrue((temp_path / "logs").exists())
    
    def test_logger_creation(self):
        """Test that loggers can be created without circular dependencies"""
        from core.logging_config import get_logger
        
        logger = get_logger("test_module")
        
        # Should not be None and should have the correct name
        self.assertIsNotNone(logger)
        self.assertTrue(logger.name.startswith("quantumvestai."))
    
    def test_no_settings_dependency(self):
        """Test that logging config doesn't import from settings"""
        import core.logging_config
        
        # Check that the module doesn't import settings
        source_code = Path(core.logging_config.__file__).read_text()
        
        # Should not import from settings modules
        self.assertNotIn("from core.config.settings", source_code)
        self.assertNotIn("import settings", source_code)
        self.assertNotIn("from settings", source_code)


class TestAuthenticationPersistence(unittest.TestCase):
    """Test improved authentication and login state persistence"""
    
    def test_cookie_creation(self):
        """Test that persistent auth cookies are created properly"""
        from middleware.improved_auth_middleware import create_persistent_auth_cookies
        
        # Mock response object
        mock_response = Mock()
        mock_response.set_cookie = Mock()
        
        token = "test_token_123"
        user_info = {"username": "testuser", "role": "user", "full_name": "Test User"}
        
        # Test cookie creation
        create_persistent_auth_cookies(
            response=mock_response,
            token=token,
            remember=True,
            user_info=user_info,
            secure=False
        )
        
        # Verify set_cookie was called for each cookie type
        call_args_list = mock_response.set_cookie.call_args_list
        
        # Should have been called 3 times (access_token, qvai_token, user_info)
        self.assertEqual(len(call_args_list), 3)
        
        # Check cookie names
        cookie_names = [call[1]["key"] for call in call_args_list]
        expected_names = ["access_token", "qvai_token", "user_info"]
        for name in expected_names:
            self.assertIn(name, cookie_names)
    
    def test_cookie_clearing(self):
        """Test that auth cookies are cleared properly"""
        from middleware.improved_auth_middleware import clear_auth_cookies
        
        # Mock response object
        mock_response = Mock()
        mock_response.delete_cookie = Mock()
        
        # Test cookie clearing
        clear_auth_cookies(mock_response)
        
        # Verify delete_cookie was called for each cookie type
        call_args_list = mock_response.delete_cookie.call_args_list
        
        # Should have been called 3 times
        self.assertEqual(len(call_args_list), 3)
        
        # Check cookie names
        cookie_names = [call[1]["key"] for call in call_args_list]
        expected_names = ["access_token", "qvai_token", "user_info"]
        for name in expected_names:
            self.assertIn(name, cookie_names)
    
    def test_token_extraction(self):
        """Test token extraction from multiple sources"""
        from middleware.improved_auth_middleware import ImprovedAuthMiddleware
        
        middleware = ImprovedAuthMiddleware(app=None)
        
        # Mock request with different token sources
        mock_request = Mock()
        
        # Test 1: Authorization header
        mock_request.headers = {"authorization": "Bearer test_token_header"}
        mock_request.cookies = {}
        mock_request.query_params = {}
        
        token = middleware._extract_token_from_request(mock_request)
        self.assertEqual(token, "test_token_header")
        
        # Test 2: access_token cookie
        mock_request.headers = {}
        mock_request.cookies = {"access_token": "Bearer test_token_cookie"}
        mock_request.query_params = {}
        
        token = middleware._extract_token_from_request(mock_request)
        self.assertEqual(token, "test_token_cookie")
        
        # Test 3: qvai_token cookie
        mock_request.headers = {}
        mock_request.cookies = {"qvai_token": "test_token_qvai"}
        mock_request.query_params = {}
        
        token = middleware._extract_token_from_request(mock_request)
        self.assertEqual(token, "test_token_qvai")
        
        # Test 4: No token
        mock_request.headers = {}
        mock_request.cookies = {}
        mock_request.query_params = {}
        
        token = middleware._extract_token_from_request(mock_request)
        self.assertIsNone(token)
    
    def test_protected_routes(self):
        """Test that protected routes are identified correctly"""
        from middleware.improved_auth_middleware import ImprovedAuthMiddleware
        
        middleware = ImprovedAuthMiddleware(app=None)
        
        # Protected routes
        self.assertTrue(middleware._requires_authentication("/settings"))
        self.assertTrue(middleware._requires_authentication("/dashboard"))
        self.assertTrue(middleware._requires_authentication("/settings/profile"))
        
        # Public routes
        self.assertFalse(middleware._requires_authentication("/"))
        self.assertFalse(middleware._requires_authentication("/login"))
        self.assertFalse(middleware._requires_authentication("/auth/login"))
        self.assertFalse(middleware._requires_authentication("/static/css/main.css"))
        self.assertFalse(middleware._requires_authentication("/api/health"))


def run_tests():
    """Run all tests and return success status"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLoggingConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationPersistence))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)