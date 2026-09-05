import os
from celery import shared_task
from app.services.reporting_service import ReportingService
from app.models.user import User
from .base_task import BaseTask
import uuid

@shared_task(bind=True, base=BaseTask, name="tasks.generate_report")
def generate_report_task(self, user_id: int, filters: dict, report_format: str = 'csv'):
    """
    Celery task to generate an asynchronous report.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Invalid user ID")
            
        file_name = f"report_{uuid.uuid4().hex}.{report_format}"
        # For demonstration, we save it to the instance folder or static folder
        upload_folder = os.environ.get('UPLOAD_FOLDER', 'instance/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file_name)
        
        if report_format == 'csv':
            data = ReportingService.generate_csv(user, filters)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
        elif report_format == 'pdf':
            data = ReportingService.generate_pdf(user, filters)
            with open(file_path, 'wb') as f:
                f.write(data)
        else:
            raise ValueError("Unsupported format")
            
        return {"status": "success", "file_url": f"/downloads/{file_name}", "format": report_format}
    except Exception as e:
        self.retry(exc=e)
