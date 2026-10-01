import time
import random
import logging
from typing import Callable, Any, Type, Tuple, Optional

logger = logging.getLogger(__name__)


def retry_with_backoff(
    func: Callable[..., Any],
    max_retries: int = 3,
    initial_delay: float = 0.5,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    *args: Any,
    **kwargs: Any
) -> Any:
    """
    Executes func with exponential backoff and optional jitter.
    Retries only specified retryable_exceptions.
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except retryable_exceptions as e:
            last_exception = e
            if attempt == max_retries:
                logger.error(f"Function '{func.__name__}' failed after {max_retries} attempts: {e}")
                raise e

            sleep_time = delay * (random.uniform(0.8, 1.2) if jitter else 1.0)
            logger.warning(
                f"Attempt {attempt}/{max_retries} for '{func.__name__}' failed ({e}). "
                f"Retrying in {sleep_time:.2f}s..."
            )
            time.sleep(sleep_time)
            delay *= backoff_factor

    if last_exception:
        raise last_exception
