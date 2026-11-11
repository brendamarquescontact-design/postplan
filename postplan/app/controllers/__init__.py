from functools import wraps

from flask import flash, g, redirect, url_for


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.usuario is None:
            flash("Faça login para continuar.", "info")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped
