from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.api.deps import get_current_active_superuser, SessionDep
from app.crud import get_server_by_ip, create_server, get_servers, delete_server_by_id
from app.models import Server
from app.models import Message

router = APIRouter(prefix="/servers", tags=["servers"])


@router.get("/", dependencies=[Depends(get_current_active_superuser)])
def read_servers(session: SessionDep, skip: int = 0, limit: int = 100):
    """
    Retrieve servers.
    """
    servers = get_servers(session=session, skip=skip, limit=limit)
    return {"data": servers, "count": len(servers)}


@router.post("/", dependencies=[Depends(get_current_active_superuser)])
def create_server_endpoint(*, session: SessionDep, server_data: Server):
    """
    Create a new server.
    """
    existing_server = get_server_by_ip(session=session, ip_address=server_data.ip_address)
    if existing_server:
        raise HTTPException(status_code=400, detail="A server with this IP already exists.")
    server = create_server(session=session, server_data=server_data.dict())
    return server


@router.delete("/{server_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_server(server_id: str, session: SessionDep):
    """
    Delete a server by ID.
    """
    delete_server_by_id(session=session, server_id=server_id)
    return Message(message="Server deleted successfully.")
