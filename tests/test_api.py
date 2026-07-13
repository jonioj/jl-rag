import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app, get_db as get_db_dependency, get_llm_provider


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    class DummyLLM:
        def answer(self, prompt: str) -> str:
            return f"answered:{prompt}"

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_get_llm_provider():
        return DummyLLM()

    app.dependency_overrides[get_db_dependency] = override_get_db
    app.dependency_overrides[get_llm_provider] = override_get_llm_provider
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Users & Messages API is running"}


def test_create_and_list_users(client):
    response = client.post("/users", json={"email": "alice@example.com"})
    assert response.status_code == 200
    created_user = response.json()
    assert created_user["email"] == "alice@example.com"

    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert any(user["id"] == created_user["id"] and user["email"] == created_user["email"] for user in data)


def test_create_and_list_messages(client):
    user_response = client.post("/users", json={"email": "bob@example.com"})
    user_id = user_response.json()["id"]

    response = client.post(
        "/messages",
        json={
            "u_id": user_id,
            "questions": "Hello",
            "answer": "Hi there",
        },
    )
    assert response.status_code == 200
    created_message = response.json()
    assert created_message["questions"] == "Hello"

    response = client.get("/messages")
    assert response.status_code == 200
    data = response.json()
    assert any(message["id"] == created_message["id"] and message["u_id"] == user_id for message in data)


def test_ask_question_uses_semantic_search(client):
    user_response = client.post("/users", json={"email": "carol@example.com"})
    user_id = user_response.json()["id"]

    response = client.post(
        f"/users/{user_id}/ask",
        json={
            "u_id": user_id,
            "questions": "What is a vector database?",
            "answer": None,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["questions"] == "What is a vector database?"
    assert body["answer"].startswith("answered:")
