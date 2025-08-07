"""
Simple Configuration Module for Twitter Integration
This is a simplified version that works without additional dependencies
"""
import os
from typing import Optional


class TwitterConfig:
    """Simple Twitter configuration class that reads values from the environment"""

    def __init__(self) -> None:
        """No-op constructor for compatibility."""
        # The previous implementation stored the values at import time.  This
        # caused issues when environment variables were updated after the module
        # was loaded.  The new implementation exposes properties that read from
        # ``os.environ`` on each access so the latest values are always used.
        pass

    @property
    def TWITTER_BEARER_TOKEN(self) -> Optional[str]:
        return os.getenv('TWITTER_BEARER_TOKEN')

    @property
    def TWITTER_API_KEY(self) -> Optional[str]:
        return os.getenv('TWITTER_API_KEY') or os.getenv('TWITTER_CONSUMER_KEY')

    @property
    def TWITTER_API_SECRET(self) -> Optional[str]:
        return os.getenv('TWITTER_API_SECRET') or os.getenv('TWITTER_CONSUMER_SECRET')

    @property
    def TWITTER_ACCESS_TOKEN(self) -> Optional[str]:
        return os.getenv('TWITTER_ACCESS_TOKEN')

    @property
    def TWITTER_ACCESS_SECRET(self) -> Optional[str]:
        return os.getenv('TWITTER_ACCESS_SECRET') or os.getenv('TWITTER_ACCESS_SECRET')
    
    def has_credentials(self) -> bool:
        """Check if required Twitter credentials are configured
        
        Requires at minimum a bearer token OR both API key and secret
        Also respects the ENABLE_TWITTER_SENTIMENT setting to allow manual disable
        """
        # Check if Twitter sentiment is explicitly disabled
        enable_twitter = os.getenv('ENABLE_TWITTER_SENTIMENT', 'false').lower() == 'true'
        if not enable_twitter:
            return False
            
        has_bearer = bool(self.TWITTER_BEARER_TOKEN)
        has_api_keys = bool(self.TWITTER_API_KEY and self.TWITTER_API_SECRET)
        
        return has_bearer or has_api_keys

# Create global instance
twitter_config = TwitterConfig()
