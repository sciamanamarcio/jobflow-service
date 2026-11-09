import uuid

import pytest

from app import tasks
from app.jobs import map_state
from app.schemas import JobStatus


def test_health(client):
    res = client.get("/health")

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_create_job_returns_202_with_location(client):
    res = client.post("/jobs", json={"text": "Hello world"})

    assert res.status_code == 202
    body = res.json()
    assert body["status"] == "QUEUED"
    assert res.headers["location"] == f"/jobs/{body['id']}"


def test_job_result_is_available_after_processing(client):
    job_id = client.post("/jobs", json={"text": "Hello world. Hello again!"}).json()["id"]

    res = client.get(f"/jobs/{job_id}")

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "COMPLETED"
    assert body["result"]["words"] == 4
    assert body["result"]["top_words"][0] == {"word": "hello", "count": 2}
    assert body["error"] is None


def test_failed_job_exposes_the_error(client, monkeypatch):
    def boom(_text):
        raise ValueError("boom")

    monkeypatch.setattr(tasks, "analyze_text", boom)
    job_id = client.post("/jobs", json={"text": "anything"}).json()["id"]

    body = client.get(f"/jobs/{job_id}").json()

    assert body["status"] == "FAILED"
    assert body["error"] == "boom"
    assert body["result"] is None


def test_delay_seconds_is_forwarded_to_the_task(client, monkeypatch):
    slept = []
    monkeypatch.setattr(tasks.time, "sleep", slept.append)

    client.post("/jobs", json={"text": "slow job", "delay_seconds": 3})

    assert slept == [3]


def test_unknown_job_returns_404(client):
    res = client.get(f"/jobs/{uuid.uuid4()}")

    assert res.status_code == 404


def test_invalid_job_id_returns_422(client):
    res = client.get("/jobs/not-a-uuid")

    assert res.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {"text": ""},
        {},
        {"text": "ok", "delay_seconds": 31},
        {"text": "ok", "delay_seconds": -1},
    ],
)
def test_invalid_payload_returns_422(client, payload):
    res = client.post("/jobs", json=payload)

    assert res.status_code == 422


@pytest.mark.parametrize(
    ("celery_state", "expected"),
    [
        ("PENDING", JobStatus.QUEUED),
        ("STARTED", JobStatus.RUNNING),
        ("RETRY", JobStatus.RUNNING),
        ("SUCCESS", JobStatus.COMPLETED),
        ("FAILURE", JobStatus.FAILED),
        ("REVOKED", JobStatus.FAILED),
    ],
)
def test_celery_states_are_mapped_to_api_statuses(celery_state, expected):
    assert map_state(celery_state) == expected
