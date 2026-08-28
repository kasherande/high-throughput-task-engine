import time
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import redis

from app.core.database import Base, engine, get_db
from app.models.task import TaskLog, TaskStatus
from app.celery_worker import process_heavy_task

app = FastAPI(title="High-Throughput Task Engine")

redis_client = redis.Redis(host="redis", port=6379, db=0)

def rate_limiter(request: Request):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    current_requests = redis_client.incr(key)
    if current_requests == 1:
        redis_client.expire(key, 10)  # 10-second window
        
    if current_requests > 5:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait.")

for i in range(15):
    try:
        Base.metadata.create_all(bind=engine)
        print("Successfully connected to MySQL!")
        break
    except Exception:
        time.sleep(2)

@app.post("/tasks/enqueue", dependencies=[Depends(rate_limiter)])
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