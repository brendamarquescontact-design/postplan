"""PostPlan - planejador de conteúdo para criadores (Flask, padrão MVC)."""
import os
import secrets
from pathlib import Path

from flask import Flask, abort, g, render_template, request, session

from app import db
from app.models import usuario as usuario_model
from app.models.post import PLATAFORMAS, STATUS, STATUS_ROTULO


def create_app(test_config=None):
    app = Flask(__name__)
    base = Path(__file__).resolve().parent.parent
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-troque-em-producao"),
        DATABASE=os.environ.get("DATABASE", str(base / "postplan.sqlite3")),
        CSRF_ENABLED=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    # Globais visíveis também dentro de macros importados.
    app.jinja_env.globals.update(STATUS=STATUS, STATUS_ROTULO=STATUS_ROTULO, PLATAFORMAS=PLATAFORMAS)

    # Cria as tabelas automaticamente se ainda não existirem (idempotente).
    with app.app_context():
        db.init_db()

    from app.controllers import auth, pilares, posts

    app.register_blueprint(auth.bp)
    app.register_blueprint(posts.bp)
    app.register_blueprint(pilares.bp)

    @app.before_request
    def _carregar_usuario_e_csrf():
        uid = session.get("usuario_id")
        g.usuario = usuario_model.buscar(uid) if uid else None
        if app.config["CSRF_ENABLED"] and request.method == "POST":
            token = session.get("csrf_token")
            if not token or not secrets.compare_digest(token, request.form.get("csrf_token", "")):
                abort(400, description="Sessão expirada ou formulário inválido. Recarregue a página e tente de novo.")

    @app.context_processor
    def _globais():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(16)
        return {
            "csrf_token": session["csrf_token"],
            "STATUS": STATUS,
            "STATUS_ROTULO": STATUS_ROTULO,
            "PLATAFORMAS": PLATAFORMAS,
        }

    @app.errorhandler(400)
    def _400(e):
        return render_template("erro.html", codigo=400, titulo="Requisição inválida", mensagem=e.description), 400

    @app.errorhandler(404)
    def _404(_e):
        return render_template("erro.html", codigo=404, titulo="Página não encontrada",
                               mensagem="O que você procurou não existe ou foi removido."), 404

    @app.errorhandler(500)
    def _500(_e):
        return render_template("erro.html", codigo=500, titulo="Algo deu errado",
                               mensagem="Tivemos um problema inesperado. Tente novamente em instantes."), 500

    return app
