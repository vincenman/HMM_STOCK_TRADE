"""
Performance optimization utilities for production deployment.
"""
import streamlit as st
import pandas as pd
import time
from functools import wraps
from typing import Callable, Any
import hashlib

from utils.logger import setup_logger

logger = setup_logger(__name__)


def cache_data_with_ttl(ttl: int = 3600):
    """
    Decorator for caching data with time-to-live.

    Args:
        ttl: Time to live in seconds (default 1 hour)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use Streamlit's cache_data decorator
            cached_func = st.cache_data(ttl=ttl)(func)
            return cached_func(*args, **kwargs)
        return wrapper
    return decorator


def cache_resource():
    """Decorator for caching expensive resources (models, connections)."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use Streamlit's cache_resource decorator
            cached_func = st.cache_resource()(func)
            return cached_func(*args, **kwargs)
        return wrapper
    return decorator


def measure_time(operation_name: str = "Operation"):
    """
    Decorator to measure execution time.

    Args:
        operation_name: Name of the operation for logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"{operation_name} took {elapsed:.2f} seconds")
            return result
        return wrapper
    return decorator


class DataCache:
    """
    Simple data cache for frequently accessed data.
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize data cache.

        Args:
            max_size: Maximum number of cached items
        """
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}

    def get(self, key: str) -> Any:
        """Get item from cache."""
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """Set item in cache."""
        if len(self.cache) >= self.max_size:
            # Remove least accessed item
            min_key = min(self.access_count, key=self.access_count.get)
            del self.cache[min_key]
            del self.access_count[min_key]

        self.cache[key] = value
        self.access_count[key] = 0

    def clear(self):
        """Clear cache."""
        self.cache.clear()
        self.access_count.clear()


def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame memory usage.

    Args:
        df: Input DataFrame

    Returns:
        Optimized DataFrame
    """
    # Downcast numeric types
    for col in df.select_dtypes(include=['float']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')

    for col in df.select_dtypes(include=['int']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')

    return df


def get_cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


# Global data cache instance
global_cache = DataCache(max_size=50)


def clear_all_caches():
    """Clear all Streamlit caches and global cache."""
    st.cache_data.clear()
    st.cache_resource.clear()
    global_cache.clear()
    logger.info("All caches cleared")
