import os
from celery import Celery

def make_celery(app_name=__name__):
    """
    Creates and configures a Celery instance.
    """
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    celery_app = Celery(
        app_name,
        backend=redis_url,
        broker=redis_url,
        include=[
            'app.tasks.notification_tasks',
            'app.tasks.sla_tasks',
            'app.tasks.report_tasks',
            'app.tasks.storage_tasks'
        ]
    )
    
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=3600, # 1 hour max
        worker_max_tasks_per_child=1000,
        worker_prefetch_multiplier=1
    )
    
    return celery_app

celery_app = make_celery('civicfix')
celery_app.set_default()

def init_celery(app, celery):
    """
    Initializes Celery with the Flask app context.
    Allows tasks to access Flask extensions like SQLAlchemy (db).
    """
    celery.conf.update(app.config)
    
    # Ensure broker and result backend are preserved
    redis_url = app.config.get('REDIS_URL') or os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    celery.conf.broker_url = redis_url
    celery.conf.result_backend = redis_url
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
                
    celery.Task = ContextTask
