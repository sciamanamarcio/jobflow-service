from uuid import UUID

from fastapi import FastAPI, HTTPException, Response, status

from app import jobs
from app.schemas import JobCreate, JobCreated, JobOut, JobStatus

app = FastAPI(
    title="JobFlow Service",
    version="1.0.0",
    description="Submit text for analysis and poll the result. Processing runs in Celery workers.",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/jobs", response_model=JobCreated, status_code=status.HTTP_202_ACCEPTED)
def create_job(payload: JobCreate, response: Response) -> JobCreated:
    job_id = jobs.submit_job(payload.text, payload.delay_seconds)
    response.headers["Location"] = f"/jobs/{job_id}"
    return JobCreated(id=job_id, status=JobStatus.QUEUED)


@app.get("/jobs/{job_id}", response_model=JobOut)
def read_job(job_id: UUID) -> JobOut:
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
