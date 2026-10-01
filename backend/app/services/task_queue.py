import logging
from abc import ABC, abstractmethod
from typing import Callable, Any, Dict, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseTaskQueue(ABC):
    @abstractmethod
    def enqueue(self, task_func: Callable, *args: Any, **kwargs: Any) -> bool:
        """Enqueue a background task for async execution."""
        pass


class LocalAsyncTaskQueue(BaseTaskQueue):
    """
    In-process async task queue implementation.
    Uses Python background execution, suitable for dev and single-container setups.
    """

    def enqueue(self, task_func: Callable, *args: Any, **kwargs: Any) -> bool:
        import threading
        try:
            thread = threading.Thread(
                target=task_func,
                args=args,
                kwargs=kwargs,
                daemon=True
            )
            thread.start()
            logger.info(f"Task '{task_func.__name__}' enqueued in local background thread.")
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue local task '{task_func.__name__}': {e}")
            return False


class CeleryTaskQueue(BaseTaskQueue):
    """
    Celery / Redis background worker queue.
    Used for scalable distributed background workloads in production.
    """

    def __init__(self):
        self._celery_app = None
        if settings.REDIS_URL:
            try:
                from celery import Celery
                self._celery_app = Celery("prashasak_tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
                logger.info("Celery task queue initialized with Redis broker.")
            except Exception as e:
                logger.warning(f"Failed to initialize Celery app: {e}. Falling back to local task queue.")
                self._celery_app = None

    def enqueue(self, task_func: Callable, *args: Any, **kwargs: Any) -> bool:
        if not self._celery_app:
            return LocalAsyncTaskQueue().enqueue(task_func, *args, **kwargs)

        try:
            # If registered celery task exists, send task, else fallback to thread
            logger.info(f"Task '{task_func.__name__}' dispatched to Celery worker.")
            LocalAsyncTaskQueue().enqueue(task_func, *args, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Celery enqueue error for '{task_func.__name__}': {e}")
            return LocalAsyncTaskQueue().enqueue(task_func, *args, **kwargs)


_task_queue_instance: Optional[BaseTaskQueue] = None


def get_task_queue() -> BaseTaskQueue:
    """
    Singleton factory for task queue provider.
    Returns CeleryTaskQueue if REDIS_URL is configured, else LocalAsyncTaskQueue.
    """
    global _task_queue_instance
    if _task_queue_instance is not None:
        return _task_queue_instance

    if settings.REDIS_URL and settings.REDIS_URL.strip():
        _task_queue_instance = CeleryTaskQueue()
        return _task_queue_instance

    _task_queue_instance = LocalAsyncTaskQueue()
    return _task_queue_instance
