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

        # Support both new-style and legacy environment variable names so that
        # deployments using either set will work correctly. The *.env.template*
        # file uses the legacy `TWITTER_CONSUMER_*` names while the code expects
        # `TWITTER_API_*`.  Here we check the API variables first and fall back
        # to the consumer versions if they are present.
        self.TWITTER_API_KEY = os.getenv('TWITTER_API_KEY') or os.getenv('TWITTER_CONSUMER_KEY')
        self.TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET') or os.getenv('TWITTER_CONSUMER_SECRET')
        self.TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
        self.TWITTER_ACCESS_TOKEN_SECRET = (
            os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            or os.getenv('TWITTER_ACCESS_SECRET')
        )
    
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
