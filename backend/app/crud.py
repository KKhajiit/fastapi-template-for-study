import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate, Server, ServerCreate, ServerUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def create_server(*, session: Session, server_create: ServerCreate) -> Server:
    """
    Creates a new server record in the database.
    """
    db_server = Server.model_validate(server_create)
    session.add(db_server)
    session.commit()
    session.refresh(db_server)
    return db_server


def update_server(*, session: Session, db_server: Server, server_in: ServerUpdate) -> Server:
    """
    Updates an existing server record.
    """
    server_data = server_in.model_dump(exclude_unset=True)
    db_server.sqlmodel_update(server_data)
    session.add(db_server)
    session.commit()
    session.refresh(db_server)
    return db_server


def get_server_by_ip(*, session: Session, ip_address: str) -> Server | None:
    """
    Fetches a server record by its IP address.
    """
    statement = select(Server).where(Server.ip_address == ip_address)
    server = session.exec(statement).first()
    return server


def get_server_by_name(*, session: Session, name: str) -> Server | None:
    """
    Fetches a server record by its name.
    """
    statement = select(Server).where(Server.name == name)
    server = session.exec(statement).first()
    return server


def delete_server(*, session: Session, db_server: Server) -> None:
    """
    Deletes an existing server record.
    """
    session.delete(db_server)
    session.commit()


def get_servers(*, session: Session, offset: int = 0, limit: int = 10) -> list[Server]:
    """
    Fetches a paginated list of servers.
    """
    statement = select(Server).offset(offset).limit(limit)
    servers = session.exec(statement).all()
    return servers