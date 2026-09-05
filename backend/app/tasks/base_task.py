import structlog
from celery import Task
from celery.exceptions import MaxRetriesExceededError

logger = structlog.get_logger()

class BaseTask(Task):
    """
    Base Celery Task that provides:
    - Automatic error logging
    - Exponential backoff retry logic
    """
    abstract = True
    
    # Retry configurations
    autoretry_for = (Exception,)
    max_retries = 3
    retry_backoff = True
    retry_backoff_max = 3600
    retry_jitter = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Log task failure.
        """
        logger.error(
            "Task failed",
            task_id=task_id,
            task_name=self.name,
            exc_info=exc,
            args=args,
            kwargs=kwargs
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """
        Log task retry.
        """
        logger.warning(
            "Task retrying",
            task_id=task_id,
            task_name=self.name,
            exc_info=exc
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """
        Log task success.
        """
        logger.info(
            "Task succeeded",
            task_id=task_id,
            task_name=self.name,
            result=retval
        )
        super().on_success(retval, task_id, args, kwargs)
