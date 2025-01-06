import uuid
from sqlmodel import Session
from app.models import Server, ServerCreate
from app.crud import create_server

def create_random_server(session: Session) -> Server:
    """
    Create a random server in the database for testing purposes.

    Args:
        session (Session): The database session to use.

    Returns:
        Server: The created Server object.
    """
    ip_address = f"192.168.1.{uuid.uuid4().int % 255}"  # Generate a random IP address
    server_in = ServerCreate(ip_address=ip_address)
    server = create_server(session=session, server_create=server_in)
    return server
