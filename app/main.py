import time
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import Base, engine, get_db
from app.models.task import TaskLog, TaskStatus
from app.celery_worker import process_heavy_task

app = FastAPI(title="High-Throughput Task Engine")

# Wait for MySQL to finish initializing
for i in range(15):
    try:
        Base.metadata.create_all(bind=engine)
        print("Successfully connected to MySQL!")
        break
    except Exception as e:
        print(f"Waiting for database connection... ({i+1}/15)")
        time.sleep(2)

@app.post("/tasks/enqueue")
def enqueue_task(payload: str, db: Session = Depends(get_db)):
    task_job = process_heavy_task.delay(payload)
    new_task = TaskLog(task_id=task_job.id, payload=payload, status=TaskStatus.PENDING)
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return {"task_id": new_task.task_id, "status": new_task.status}

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(TaskLog).filter(TaskLog.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task.task_id, "status": task.status, "result": task.result}