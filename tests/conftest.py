import os

# Precisam ser definidas ANTES de importar a aplicação.
# Em modo "eager" o Celery executa a task na hora, sem Redis nem worker.
os.environ["BROKER_URL"] = "memory://"
os.environ["RESULT_BACKEND"] = "cache+memory://"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.celery_app import celery_app  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def eager_celery():
    celery_app.conf.update(task_always_eager=True, task_store_eager_result=True)
    yield
    celery_app.conf.update(task_always_eager=False, task_store_eager_result=False)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
