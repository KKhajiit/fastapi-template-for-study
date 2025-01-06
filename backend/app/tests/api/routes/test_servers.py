import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import Server, ServerCreate
from app.main import app
from app.api.deps import get_db
from app.tests.utils.user import get_superuser_token_headers
from app.tests.utils.server import create_random_server

# Setup FastAPI test client
client = TestClient(app)

# Dependency override for test database session
def override_get_db():
    from app.tests.utils.session import get_test_session
    yield from get_test_session()

app.dependency_overrides[get_db] = override_get_db


def test_create_server(session: Session):
    superuser_headers = get_superuser_token_headers(client, session)
    server_data = {
        "ip_address": "192.168.1.1",
    }

    response = client.post("/servers/", json=server_data, headers=superuser_headers)
    assert response.status_code == 200
    created_server = response.json()
    assert created_server["ip_address"] == server_data["ip_address"]


def test_read_servers(session: Session):
    superuser_headers = get_superuser_token_headers(client, session)
    create_random_server(session)

    response = client.get("/servers/", headers=superuser_headers)
    assert response.status_code == 200
    servers = response.json()
    assert "data" in servers
    assert "count" in servers
    assert len(servers["data"]) > 0


def test_read_server_by_id(session: Session):
    superuser_headers = get_superuser_token_headers(client, session)
    server = create_random_server(session)

    response = client.get(f"/servers/{server.id}", headers=superuser_headers)
    assert response.status_code == 200
    fetched_server = response.json()
    assert fetched_server["id"] == str(server.id)


def test_update_server(session: Session, client: TestClient):
    superuser_headers = get_superuser_token_headers(client, session)
    server = create_random_server(session)
    update_data = {"ip_address": "192.168.1.2"}

    response = client.patch(
        f"/servers/{server.id}", json=update_data, headers=superuser_headers
    )
    assert response.status_code == 200
    updated_server = response.json()
    assert updated_server["ip_address"] == update_data["ip_address"]


def test_delete_server(session: Session):
    superuser_headers = get_superuser_token_headers(client, session)
    server = create_random_server(session)

    response = client.delete(f"/servers/{server.id}", headers=superuser_headers)
    assert response.status_code == 200
    message = response.json()
    assert message["message"] == "Server deleted successfully"

    # Ensure server is deleted
    response = client.get(f"/servers/{server.id}", headers=superuser_headers)
    assert response.status_code == 404
