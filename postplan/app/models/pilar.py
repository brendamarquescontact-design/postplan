"""Model: Pilar de conteúdo (categoria temática dos posts)."""
import re
import sqlite3

from app.db import get_db
from app.models import ValidationError

COR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def listar(usuario_id):
    return get_db().execute(
        """SELECT p.*, (SELECT COUNT(*) FROM post WHERE pilar_id = p.id) AS total_posts
           FROM pilar p WHERE p.usuario_id = ? ORDER BY p.nome COLLATE NOCASE""",
        (usuario_id,),
    ).fetchall()


def buscar(usuario_id, pilar_id):
    return get_db().execute(
        "SELECT * FROM pilar WHERE id = ? AND usuario_id = ?", (pilar_id, usuario_id)
    ).fetchone()


def criar(usuario_id, nome, cor):
    nome = (nome or "").strip()
    cor = (cor or "#7c5cff").strip()
    erros = {}
    if not 2 <= len(nome) <= 40:
        erros["nome"] = "O nome do pilar deve ter entre 2 e 40 caracteres."
    if not COR_RE.match(cor):
        erros["cor"] = "Cor inválida."
    if erros:
        raise ValidationError(erros)
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO pilar (usuario_id, nome, cor) VALUES (?, ?, ?)", (usuario_id, nome, cor)
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise ValidationError({"nome": "Você já tem um pilar com esse nome."})
    return cur.lastrowid


def excluir(usuario_id, pilar_id):
    db = get_db()
    cur = db.execute("DELETE FROM pilar WHERE id = ? AND usuario_id = ?", (pilar_id, usuario_id))
    db.commit()
    return cur.rowcount > 0
