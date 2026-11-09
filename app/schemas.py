from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from app.config import settings


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JobCreate(BaseModel):
    text: str = Field(min_length=1, max_length=settings.max_text_length)
    delay_seconds: int = Field(default=0, ge=0, le=30, description="Simulates heavy work")


class WordCount(BaseModel):
    word: str
    count: int


class AnalysisResult(BaseModel):
    characters: int
    words: int
    unique_words: int
    sentences: int
    reading_time_seconds: int
    top_words: list[WordCount]


class JobCreated(BaseModel):
    id: UUID
    status: JobStatus


class JobOut(BaseModel):
    id: UUID
    status: JobStatus
    result: AnalysisResult | None = None
    error: str | None = None
