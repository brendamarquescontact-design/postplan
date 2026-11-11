import re

import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "teste.sqlite3"), "CSRF_ENABLED": False})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logado(client):
    """Cliente com uma usuária cadastrada e autenticada."""
    client.post("/cadastro", data={"nome": "Brenda Teste", "email": "brenda@exemplo.com", "senha": "senha1234"})
    client.post("/login", data={"email": "brenda@exemplo.com", "senha": "senha1234"})
    return client


def post_valido(**extra):
    d = {"titulo": "Rotina da manhã", "plataforma": "Instagram", "status": "ideia",
         "roteiro": "Abrir com café", "data_publicacao": "", "pilar_id": ""}
    d.update(extra)
    return d


def extrair_csrf(html):
    return re.search(r'name="csrf_token" value="([0-9a-f]+)"', html).group(1)
