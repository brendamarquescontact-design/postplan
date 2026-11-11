"""Model: Usuario."""
import re
import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db
from app.models import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar(nome, email, senha):
    erros = {}
    nome = (nome or "").strip()
    email = (email or "").strip().lower()
    senha = senha or ""
    if not 2 <= len(nome) <= 80:
        erros["nome"] = "O nome deve ter entre 2 e 80 caracteres."
    if not EMAIL_RE.match(email):
        erros["email"] = "Informe um e-mail válido."
    if len(senha) < 8:
        erros["senha"] = "A senha deve ter pelo menos 8 caracteres."
    if erros:
        raise ValidationError(erros)
    return nome, email, senha


def criar(nome, email, senha):
    nome, email, senha = validar(nome, email, senha)
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO usuario (nome, email, senha_hash) VALUES (?, ?, ?)",
            (nome, email, generate_password_hash(senha)),
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise ValidationError({"email": "Este e-mail já está cadastrado."})
    return cur.lastrowid


def buscar(usuario_id):
    return get_db().execute("SELECT id, nome, email FROM usuario WHERE id = ?", (usuario_id,)).fetchone()


def autenticar(email, senha):
    row = get_db().execute(
        "SELECT * FROM usuario WHERE email = ?", ((email or "").strip().lower(),)
    ).fetchone()
    if row and check_password_hash(row["senha_hash"], senha or ""):
        return row
    return None
