from uuid import UUID, uuid4

from celery.result import AsyncResult

from app.celery_app import celery_app
from app.schemas import AnalysisResult, JobOut, JobStatus
from app.tasks import analyze_text_task

# O Celery devolve PENDING tanto para "na fila" quanto para "id inexistente".
# Para distinguir, gravamos um marcador no mesmo backend ao criar o job.
_STATE_MAP = {
    "PENDING": JobStatus.QUEUED,
    "RECEIVED": JobStatus.QUEUED,
    "STARTED": JobStatus.RUNNING,
    "RETRY": JobStatus.RUNNING,
    "SUCCESS": JobStatus.COMPLETED,
    "FAILURE": JobStatus.FAILED,
    "REVOKED": JobStatus.FAILED,
}


def _marker_key(job_id: UUID) -> str:
    return f"jobflow-job-{job_id}"


def map_state(celery_state: str) -> JobStatus:
    return _STATE_MAP.get(celery_state, JobStatus.QUEUED)


def submit_job(text: str, delay_seconds: int) -> UUID:
    job_id = uuid4()
    # O marcador é gravado ANTES de enfileirar, para o worker nunca terminar antes dele existir
    celery_app.backend.set(_marker_key(job_id), "1")
    analyze_text_task.apply_async(args=[text, delay_seconds], task_id=str(job_id))
    return job_id


def get_job(job_id: UUID) -> JobOut | None:
    if celery_app.backend.get(_marker_key(job_id)) is None:
        return None

    async_result = AsyncResult(str(job_id), app=celery_app)
    status = map_state(async_result.state)

    if status is JobStatus.COMPLETED:
        return JobOut(id=job_id, status=status, result=AnalysisResult(**async_result.result))
    if status is JobStatus.FAILED:
        return JobOut(id=job_id, status=status, error=str(async_result.result))
    return JobOut(id=job_id, status=status)
