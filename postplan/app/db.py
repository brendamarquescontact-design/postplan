"""Conexão com o banco de dados (SQLite) e criação do esquema."""
import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA = Path(__file__).resolve().parent.parent / "database" / "schema.sql"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(SCHEMA.read_text(encoding="utf-8"))
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def _init_db_command():
        """Cria as tabelas do banco de dados."""
        init_db()
        print("Banco de dados inicializado.")
