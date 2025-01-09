import random
import string

from fastapi.testclient import TestClient

from app.core.config import settings

# random names for servers
word_list = [
    "Alfa", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", 
    "India", "Juliett", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", 
    "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", 
    "X-ray", "Yankee", "Zulu"
]

def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_ip_address():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4)) 


def random_server_name():
    return random.choice(word_list) + "-" + random.choice(word_list)


def random_port():
    return random.randint(1024, 65535)


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers