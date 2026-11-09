import time

from app.analysis import analyze_text
from app.celery_app import celery_app


@celery_app.task(name="jobs.analyze_text", acks_late=True, soft_time_limit=60)
def analyze_text_task(text: str, delay_seconds: int = 0) -> dict:
    # delay_seconds simula um processamento pesado, útil para ver o job "RUNNING"
    if delay_seconds:
        time.sleep(delay_seconds)
    return analyze_text(text)
