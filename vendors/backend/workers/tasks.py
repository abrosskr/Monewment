import time
from .celery_app import celery_app
# from database.crud import update_task_status
# from database.database import SessionLocal
from typing import Dict, Any

@celery_app.task(bind=True)
def process_data(self, task_id: int, input_data: Dict[str, Any]):
    """
    Simulates long-running data processing.
    """
    print(f"Task {task_id}: Processing started with input: {input_data}")
    # Simulate work
    time.sleep(10)
    
    result = {
        "task_id": task_id,
        "processed": True,
        "timestamp": time.time()
    }
    print(f"Task {task_id}: Completed.")
    return result
