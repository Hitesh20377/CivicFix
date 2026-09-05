import os
import time
from celery import shared_task
from .base_task import BaseTask
import structlog

logger = structlog.get_logger()

@shared_task(bind=True, base=BaseTask, name="tasks.cleanup_temp_files")
def cleanup_temp_files_task(self, max_age_hours: int = 24):
    """
    Celery task to clean up temporary files in the uploads folder older than a certain age.
    """
    try:
        upload_folder = os.environ.get('UPLOAD_FOLDER', 'instance/uploads')
        if not os.path.exists(upload_folder):
            return {"status": "success", "deleted_files": 0}

        now = time.time()
        deleted_count = 0
        
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                # Check if file is older than max_age_hours
                if os.stat(file_path).st_mtime < now - (max_age_hours * 3600):
                    os.remove(file_path)
                    deleted_count += 1
                    logger.info("Deleted old temp file", file_path=file_path)

        return {"status": "success", "deleted_files": deleted_count}
    except Exception as e:
        self.retry(exc=e)
