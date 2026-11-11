"""Controller: pilares de conteúdo."""
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.controllers import login_required
from app.models import ValidationError, pilar as pilar_model

bp = Blueprint("pilares", __name__, url_prefix="/pilares")


@bp.route("/", methods=["GET", "POST"])
@login_required
def lista():
    uid = g.usuario["id"]
    erros, form = {}, {}
    if request.method == "POST":
        form = request.form
        try:
            pilar_model.criar(uid, form.get("nome"), form.get("cor"))
            flash("Pilar criado!", "success")
            return redirect(url_for("pilares.lista"))
        except ValidationError as e:
            erros = e.errors
    return render_template("pilares/lista.html", pilares=pilar_model.listar(uid), erros=erros, form=form)


@bp.route("/<int:pilar_id>/excluir", methods=["POST"])
@login_required
def excluir(pilar_id):
    if not pilar_model.excluir(g.usuario["id"], pilar_id):
        abort(404)
    flash("Pilar excluído. Os posts dele ficaram sem pilar.", "info")
    return redirect(url_for("pilares.lista"))
