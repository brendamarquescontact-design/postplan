"""Controller: painel, lista, calendário e CRUD de posts."""
from itertools import groupby

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.controllers import login_required
from app.models import ValidationError, pilar as pilar_model, post as post_model

bp = Blueprint("posts", __name__)


@bp.route("/")
@login_required
def painel():
    uid = g.usuario["id"]
    return render_template(
        "posts/painel.html",
        contagem=post_model.contar_por_status(uid),
        proximos=post_model.proximos(uid),
    )


@bp.route("/posts")
@login_required
def lista():
    uid = g.usuario["id"]
    filtros = {
        "status": request.args.get("status", ""),
        "pilar": request.args.get("pilar", ""),
        "q": request.args.get("q", ""),
    }
    posts = post_model.listar(uid, filtros["status"], filtros["pilar"], filtros["q"])
    return render_template("posts/lista.html", posts=posts, filtros=filtros, pilares=pilar_model.listar(uid))


@bp.route("/calendario")
@login_required
def calendario():
    posts = post_model.agendados(g.usuario["id"])
    dias = [(d, list(itens)) for d, itens in groupby(posts, key=lambda p: p["data_publicacao"])]
    return render_template("posts/calendario.html", dias=dias)


@bp.route("/posts/novo", methods=["GET", "POST"])
@login_required
def novo():
    uid = g.usuario["id"]
    erros, form = {}, {"status": "ideia"}
    if request.method == "POST":
        form = request.form
        try:
            post_model.criar(uid, form)
            flash("Post criado com sucesso!", "success")
            return redirect(url_for("posts.lista"))
        except ValidationError as e:
            erros = e.errors
            flash("Corrija os campos destacados.", "error")
    return render_template("posts/form.html", erros=erros, form=form, pilares=pilar_model.listar(uid), editando=None)


@bp.route("/posts/<int:post_id>/editar", methods=["GET", "POST"])
@login_required
def editar(post_id):
    uid = g.usuario["id"]
    post = post_model.buscar(uid, post_id)
    if not post:
        abort(404)
    erros, form = {}, dict(post)
    if request.method == "POST":
        form = request.form
        try:
            post_model.atualizar(uid, post_id, form)
            flash("Post atualizado.", "success")
            return redirect(url_for("posts.lista"))
        except ValidationError as e:
            erros = e.errors
            flash("Corrija os campos destacados.", "error")
    return render_template("posts/form.html", erros=erros, form=form, pilares=pilar_model.listar(uid), editando=post)


@bp.route("/posts/<int:post_id>/avancar", methods=["POST"])
@login_required
def avancar(post_id):
    novo_status = post_model.avancar_status(g.usuario["id"], post_id)
    if novo_status is None:
        if not post_model.buscar(g.usuario["id"], post_id):
            abort(404)
        flash("Este post já está publicado.", "info")
    else:
        flash(f"Status atualizado para “{post_model.STATUS_ROTULO[novo_status]}”.", "success")
    return redirect(request.referrer or url_for("posts.lista"))


@bp.route("/posts/<int:post_id>/excluir", methods=["POST"])
@login_required
def excluir(post_id):
    if not post_model.excluir(g.usuario["id"], post_id):
        abort(404)
    flash("Post excluído.", "info")
    return redirect(url_for("posts.lista"))
