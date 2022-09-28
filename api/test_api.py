import os
from unittest import mock

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import main
import models


@pytest.fixture(autouse=True)
def session_maker(monkeypatch):
    try:
        os.remove("/tmp/test.db")
    except FileNotFoundError:
        pass

    engine = create_engine("sqlite:////tmp/test.db", connect_args={"check_same_thread": False})
    monkeypatch.setattr(main, "engine", engine)
    monkeypatch.setattr(main, "SessionLocal", sessionmaker(autocommit=False, autoflush=False, bind=engine))
    models.Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(main.app)


def test_users(client):
    response = client.get("/users", params={"search_str": "jack"})
    assert response.status_code == 200
    assert response.json() == []

    response = client.post("/users/", json={"name": "Jack Sparrow", "email": "jack@me.com"})
    assert response.status_code == 200
    assert response.json() == {"name": "Jack Sparrow", "email": "jack@me.com", "id": mock.ANY}

    user_id = response.json()["id"]
    response = client.post("/users/", json={"name": "Jack Bauer", "email": "jack@me.com"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Duplicate user email"}

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"name": "Jack Sparrow", "email": "jack@me.com", "id": user_id}

    response = client.get("/users", params={"search_str": "jack"})
    assert response.status_code == 200
    assert response.json() == [{"name": "Jack Sparrow", "email": "jack@me.com", "id": user_id}]

    response = client.put(f"/users/{user_id}", json={"name": "Jack Bauer", "email": "jack@me.com"})
    assert response.status_code == 200
    assert response.json() == {"name": "Jack Bauer", "email": "jack@me.com", "id": user_id}

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"name": "Jack Bauer", "email": "jack@me.com", "id": user_id}

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200


def test_notes(client):
    response = client.post("/users/", json={"name": "Jack Sparrow", "email": "jack@me.com"})
    assert response.status_code == 200
    assert response.json() == {"name": "Jack Sparrow", "email": "jack@me.com", "id": mock.ANY}

    user_id = response.json()["id"]
    response = client.get(f"/users/{user_id}/notes")
    assert response.status_code == 200
    assert response.json() == []

    response = client.post(f"/users/{user_id}/notes", json={"content": "note 1"})
    assert response.status_code == 200
    assert response.json() == {"id": mock.ANY, "created_at": mock.ANY, "user_id": user_id, "content": "note 1"}
    note1_id = response.json()["id"]

    response = client.get(f"/users/{user_id}/notes")
    assert response.status_code == 200
    assert response.json() == [{"id": note1_id, "created_at": mock.ANY, "user_id": user_id, "content": "note 1"}]

    response = client.post(f"/users/{user_id}/notes", json={"content": "note 2"})
    assert response.status_code == 200
    assert response.json() == {"id": mock.ANY, "created_at": mock.ANY, "user_id": user_id, "content": "note 2"}

    response = client.get(f"/users/{user_id}/notes")
    assert response.status_code == 200
    assert response.json() == [
        {"id": note1_id, "created_at": mock.ANY, "user_id": user_id, "content": "note 1"},
        {"id": mock.ANY, "created_at": mock.ANY, "user_id": user_id, "content": "note 2"},
    ]

    note2_id = response.json()[1]["id"]

    response = client.put(f"/users/{user_id}/notes/{note2_id}", json={"content": "second note"})
    assert response.status_code == 200
    assert response.json() == {"id": note2_id, "created_at": mock.ANY, "user_id": user_id, "content": "second note"}

    response = client.delete(f"/users/{user_id}/notes/{note1_id}")
    assert response.status_code == 200

    response = client.get(f"/users/{user_id}/notes")
    assert response.status_code == 200
    assert response.json() == [
        {"id": note2_id, "created_at": mock.ANY, "user_id": user_id, "content": "second note"},
    ]
