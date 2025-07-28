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
        """Check if any Twitter credentials are configured"""
        return any([
            self.TWITTER_BEARER_TOKEN,
            self.TWITTER_API_KEY,
            self.TWITTER_API_SECRET,
            self.TWITTER_ACCESS_TOKEN,
            self.TWITTER_ACCESS_SECRET,
        ])

# Create global instance
twitter_config = TwitterConfig()
