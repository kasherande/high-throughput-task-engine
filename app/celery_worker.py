import time
from celery import Celery
from app.config import settings
from app.core.database import SessionLocal
from app.models.task import TaskLog, TaskStatus

celery_app = Celery("tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

@celery_app.task(bind=True, name="process_heavy_task")
def process_heavy_task(self, payload: str):
    db = SessionLocal()
    task_id = self.request.id
    
    # Update status to PROCESSING
    task = db.query(TaskLog).filter(TaskLog.task_id == task_id).first()
    if task:
        task.status = TaskStatus.PROCESSING
        db.commit()

    try:
        # Simulate CPU-heavy background workload (3 seconds)
        time.sleep(3)
        processed_result = f"Successfully processed workload: {payload.upper()}"

        # Update status to COMPLETED
        if task:
            task.status = TaskStatus.COMPLETED
            task.result = processed_result
            db.commit()

        return processed_result

    except Exception as e:
        if task:
            task.status = TaskStatus.FAILED
            task.result = str(e)
            db.commit()
        raise e
    finally:
        db.close()