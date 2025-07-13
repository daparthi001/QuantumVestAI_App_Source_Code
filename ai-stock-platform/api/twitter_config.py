"""
Simple Configuration Module for Twitter Integration
This is a simplified version that works without additional dependencies
"""
import os
from typing import Optional


class TwitterConfig:
    """Simple Twitter configuration class"""
    
    def __init__(self):
        self.TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
        self.TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
        self.TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
        self.TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
        self.TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    def has_credentials(self) -> bool:
        """Check if any Twitter credentials are configured"""
        return any([
            self.TWITTER_BEARER_TOKEN,
            self.TWITTER_API_KEY,
            self.TWITTER_API_SECRET,
            self.TWITTER_ACCESS_TOKEN,
            self.TWITTER_ACCESS_TOKEN_SECRET
        ])

# Create global instance
twitter_config = TwitterConfig()
