import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import Server
from app.core.config import settings
from app.tests.utils.utils import random_ip_address


def test_read_servers(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create some servers
    ip1 = random_ip_address()
    ip2 = random_ip_address()
    server1 = Server(ip_address=ip1)
    server2 = Server(ip_address=ip2)
    db.add(server1)
    db.add(server2)
    db.commit()

    # Read servers
    response = client.get(
        f"{settings.API_V1_STR}/servers/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    servers = response.json()
    assert "data" in servers
    assert "count" in servers
    assert len(servers["data"]) >= 2
    assert servers["count"] >= 2
    assert any(s["ip_address"] == ip1 for s in servers["data"])
    assert any(s["ip_address"] == ip2 for s in servers["data"])


def test_create_server(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    ip_address = random_ip_address()
    data = {"ip_address": ip_address}
    response = client.post(
        f"{settings.API_V1_STR}/servers/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    created_server = response.json()
    assert created_server["ip_address"] == ip_address

    # Verify in the database
    db_server = db.exec(select(Server).where(Server.ip_address == ip_address)).first()
    assert db_server
    assert db_server.ip_address == ip_address


def test_create_server_duplicate(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    ip_address = random_ip_address()
    server = Server(ip_address=ip_address)
    db.add(server)
    db.commit()

    data = {"ip_address": ip_address}
    response = client.post(
        f"{settings.API_V1_STR}/servers/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "The server with this IP address already exists in the system."


def test_delete_server(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    ip_address = random_ip_address()
    server = Server(ip_address=ip_address)
    db.add(server)
    db.commit()
    db.refresh(server)

    server_id = str(server.id)
    response = client.delete(
        f"{settings.API_V1_STR}/servers/{server_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Server deleted successfully"

    # Verify deletion
    db_server = db.get(Server, uuid.UUID(server_id))
    assert db_server is None


def test_delete_server_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    random_uuid = str(uuid.uuid4())
    response = client.delete(
        f"{settings.API_V1_STR}/servers/{random_uuid}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Server not found"
