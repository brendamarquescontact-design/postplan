"""Controller: cadastro, login e logout."""
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from app.models import ValidationError, usuario as usuario_model

bp = Blueprint("auth", __name__)


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if g.usuario:
        return redirect(url_for("posts.painel"))
    erros, form = {}, {}
    if request.method == "POST":
        form = request.form
        try:
            usuario_model.criar(form.get("nome"), form.get("email"), form.get("senha"))
            flash("Conta criada! Agora é só entrar.", "success")
            return redirect(url_for("auth.login"))
        except ValidationError as e:
            erros = e.errors
    return render_template("auth/cadastro.html", erros=erros, form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.usuario:
        return redirect(url_for("posts.painel"))
    form = {}
    if request.method == "POST":
        form = request.form
        user = usuario_model.autenticar(form.get("email"), form.get("senha"))
        if user:
            session.clear()
            session["usuario_id"] = user["id"]
            # "Lembrar de mim": mantém a sessão por 31 dias (padrão do Flask); sem marcar, termina ao fechar o navegador.
            session.permanent = bool(form.get("lembrar"))
            return redirect(url_for("posts.painel"))
        flash("E-mail ou senha incorretos.", "error")
    return render_template("auth/login.html", form=form)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth.login"))
