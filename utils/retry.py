"""
Robust retry mechanism with exponential backoff and jitter
"""
import time
import random
import logging
from functools import wraps
from typing import Callable, Optional, Tuple, Type

logger = logging.getLogger(__name__)

def retry(
    exceptions: Tuple[Type[Exception]] = (Exception,),
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: float = 0.1
):
    """
    Decorator for retrying a function with exponential backoff and jitter
    
    Args:
        exceptions: Exception types to catch
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Multiplier for exponential backoff
        jitter: Random jitter factor (0-1)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Max retries exceeded for {func.__name__}: {str(e)}")
                        raise
                    
                    # Calculate delay with jitter
                    jitter_amount = delay * jitter * random.uniform(-1, 1)
                    actual_delay = min(max_delay, delay + jitter_amount)
                    
                    logger.warning(
                        f"Attempt #{retries} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {actual_delay:.2f}s..."
                    )
                    
                    time.sleep(actual_delay)
                    delay *= backoff_factor
                    
        return wrapper
    return decorator