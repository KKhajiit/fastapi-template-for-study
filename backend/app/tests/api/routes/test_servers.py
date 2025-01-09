import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import crud
from app.core.config import settings
from app.models import Server, ServerCreate
from app.tests.utils.utils import random_ip_address, random_server_name, random_port


def test_create_server(
        client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    ip_address = random_ip_address
    name = random_server_name
    port = random_port

    data = {"ip_address": ip_address, "name": random_server_name, "port": random_port}
    r = client.post(
        f"{settings.API_V1_STR}/servers/",
        headers=superuser_token_headers,
        json=data,
    )
    assert 200 <= r.status_code < 300
    created_server = r.json()
    server = crud.get_server_by_ip(session=db, ip_address=ip_address)
    assert server
    assert server.ip_address == created_server["ip_address"]


def test_get_existing_server(
        client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    ip_address = random_ip_address
    name = random_server_name
    port = random_port
    server_in = ServerCreate(ip_address=ip_address, name=name, port=port)
    server = crud.create_server(session=db, server_create=server_in)
    server_id = server.id

    r = client.get(
        f"{settings.API_V1_STR}/servers/{server_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_server = r.json()

    existing_server = crud.get_server_by_ip(session=db, ip_address=ip_address)
    assert existing_server
    assert existing_server.ip_address == api_server["ip_address"]

    existing_server = crud.get_server_by_name(session=db, name=name)
    assert existing_server
    assert existing_server.name == api_server["name"]


def test_retrieve_users(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    ip_address1 = random_ip_address
    name1 = random_server_name
    port1 = random_port
    server_in1 = ServerCreate(ip_address=ip_address1, name=name1, port=port1)
    crud.create_server(session=db, server_create=server_in1)

    ip_address2 = random_ip_address
    name2 = random_server_name
    port2 = random_port
    server_in2 = ServerCreate(ip_address=ip_address2, name=name2, port=port2)
    crud.create_server(session=db, server_create=server_in2)

    r = client.get(f"{settings.API_V1_STR}/servers/", headers=superuser_token_headers)
    all_servers = r.json()

    assert len(all_servers["data"]) > 1
    assert "count" in all_servers
    for item in all_servers["data"]:
        assert "ip_address" in item
        assert "name" in item
        assert "port" in item

def test_update_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    ip_address = random_ip_address
    name = random_server_name
    port = random_port
    server_in = ServerCreate(ip_address=ip_address, name=name, port=port)
    server = crud.create_server(session=db, server_create=server_in)

    data = {"name": "Updated_server_name"}
    r = client.patch(
        f"{settings.API_V1_STR}/servers/{server.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_server = r.json()

    assert updated_server["name"] == "Updated_server_name"

    server_query = select(Server).where(Server.ip_address == ip_address)
    server_db = db.exec(server_query).first()
    db.refresh(server_db)
    assert server_db
    assert server_db.name == "Updated_server_name"