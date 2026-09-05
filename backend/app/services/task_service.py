from celery.result import AsyncResult
from app.celery_app import celery_app

class TaskService:
    @staticmethod
    def get_task_status(task_id: str) -> dict:
        """
        Retrieves the status and result of a Celery task.
        """
        task_result = AsyncResult(task_id, app=celery_app)
        
        response = {
            "task_id": task_id,
            "status": task_result.status,
            "successful": task_result.successful(),
        }
        
        if task_result.status == 'SUCCESS':
            response['result'] = task_result.result
        elif task_result.status == 'FAILURE':
            response['error'] = str(task_result.result)
            
        return response

    @staticmethod
    def revoke_task(task_id: str, terminate: bool = False):
        """
        Revokes a running or pending task.
        """
        celery_app.control.revoke(task_id, terminate=terminate)
        return {"task_id": task_id, "revoked": True}
