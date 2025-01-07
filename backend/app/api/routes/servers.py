import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    Server,
    ServerCreate,
    ServerPublic,
    ServerUpdate,
    ServersPublic,
    Message,
)

router = APIRouter(prefix="/servers", tags=["servers"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ServersPublic,
)
def read_servers(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve servers.
    """
    count_statement = select(func.count()).select_from(Server)
    count = session.exec(count_statement).one()

    statement = select(Server).offset(skip).limit(limit)
    servers = session.exec(statement).all()

    return ServersPublic(data=servers, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=ServerPublic
)
def create_server(*, session: SessionDep, server_in: ServerCreate) -> Any:
    """
    Create a new server.
    """
    # 중복 검증: IP 주소, 이름, 포트
    existing_server_ip = crud.get_server_by_ip(session=session, ip_address=server_in.ip_address)
    if existing_server_ip:
        raise HTTPException(
            status_code=400,
            detail="A server with this IP address already exists in the system.",
        )
    existing_server_name = crud.get_server_by_name(session=session, name=server_in.name)
    if existing_server_name:
        raise HTTPException(
            status_code=400,
            detail="A server with this name already exists in the system.",
        )

    server = crud.create_server(session=session, server_create=server_in)
    return server


@router.get("/{server_id}", response_model=ServerPublic)
def read_server_by_id(
    server_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific server by id.
    """
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(
            status_code=404,
            detail="The server with this id does not exist in the system.",
        )
    return server


@router.patch(
    "/{server_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ServerPublic,
)
def update_server(
    *,
    session: SessionDep,
    server_id: uuid.UUID,
    server_in: ServerUpdate,
) -> Any:
    """
    Update a server.
    """
    db_server = session.get(Server, server_id)
    if not db_server:
        raise HTTPException(
            status_code=404,
            detail="The server with this id does not exist in the system.",
        )

    db_server = crud.update_server(session=session, db_server=db_server, server_in=server_in)
    return db_server


@router.delete("/{server_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_server(session: SessionDep, server_id: uuid.UUID) -> Message:
    """
    Delete a server.
    """
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    session.delete(server)
    session.commit()
    return Message(message="Server deleted successfully")
