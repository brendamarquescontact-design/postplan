"""Model: Post (ideia/peça de conteúdo planejada pela criadora)."""
from datetime import date, datetime

from app.db import get_db
from app.models import ValidationError, pilar as pilar_model

STATUS = ["ideia", "roteirizado", "gravado", "editado", "publicado"]
STATUS_ROTULO = {
    "ideia": "Ideia",
    "roteirizado": "Roteirizado",
    "gravado": "Gravado",
    "editado": "Editado",
    "publicado": "Publicado",
}
PLATAFORMAS = ["Instagram", "TikTok", "YouTube", "Pinterest", "Blog"]

_SELECT = """SELECT po.*, pi.nome AS pilar_nome, pi.cor AS pilar_cor
             FROM post po LEFT JOIN pilar pi ON pi.id = po.pilar_id"""


def validar(usuario_id, dados):
    """Valida e normaliza os dados do formulário. Lança ValidationError."""
    erros = {}
    titulo = (dados.get("titulo") or "").strip()
    roteiro = (dados.get("roteiro") or "").strip()
    plataforma = (dados.get("plataforma") or "").strip()
    status = (dados.get("status") or "ideia").strip()
    data_raw = (dados.get("data_publicacao") or "").strip()
    pilar_raw = (dados.get("pilar_id") or "").strip()

    if not 3 <= len(titulo) <= 120:
        erros["titulo"] = "O título deve ter entre 3 e 120 caracteres."
    if len(roteiro) > 2000:
        erros["roteiro"] = "O roteiro pode ter no máximo 2000 caracteres."
    if plataforma not in PLATAFORMAS:
        erros["plataforma"] = "Escolha uma plataforma válida."
    if status not in STATUS:
        erros["status"] = "Escolha um status válido."

    data = None
    if data_raw:
        try:
            data = datetime.strptime(data_raw, "%Y-%m-%d").date().isoformat()
        except ValueError:
            erros["data_publicacao"] = "Data inválida. Use o formato AAAA-MM-DD."
    if status == "publicado" and not data and "data_publicacao" not in erros:
        erros["data_publicacao"] = "Informe a data de publicação para posts publicados."

    pilar_id = None
    if pilar_raw:
        if not pilar_raw.isdigit() or not pilar_model.buscar(usuario_id, int(pilar_raw)):
            erros["pilar_id"] = "Pilar inválido."
        else:
            pilar_id = int(pilar_raw)

    if erros:
        raise ValidationError(erros)
    return {
        "titulo": titulo, "roteiro": roteiro, "plataforma": plataforma,
        "status": status, "data_publicacao": data, "pilar_id": pilar_id,
    }


def listar(usuario_id, status=None, pilar_id=None, busca=None):
    sql = _SELECT + " WHERE po.usuario_id = ?"
    params = [usuario_id]
    if status in STATUS:
        sql += " AND po.status = ?"
        params.append(status)
    if pilar_id and str(pilar_id).isdigit():
        sql += " AND po.pilar_id = ?"
        params.append(int(pilar_id))
    if busca and busca.strip():
        sql += " AND po.titulo LIKE ?"
        params.append(f"%{busca.strip()}%")
    sql += " ORDER BY (po.data_publicacao IS NULL), po.data_publicacao, po.id DESC"
    return get_db().execute(sql, params).fetchall()


def buscar(usuario_id, post_id):
    return get_db().execute(
        _SELECT + " WHERE po.id = ? AND po.usuario_id = ?", (post_id, usuario_id)
    ).fetchone()


def criar(usuario_id, dados):
    d = validar(usuario_id, dados)
    db = get_db()
    cur = db.execute(
        """INSERT INTO post (usuario_id, pilar_id, titulo, roteiro, plataforma, status, data_publicacao)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (usuario_id, d["pilar_id"], d["titulo"], d["roteiro"], d["plataforma"], d["status"], d["data_publicacao"]),
    )
    db.commit()
    return cur.lastrowid


def atualizar(usuario_id, post_id, dados):
    d = validar(usuario_id, dados)
    db = get_db()
    cur = db.execute(
        """UPDATE post SET pilar_id=?, titulo=?, roteiro=?, plataforma=?, status=?, data_publicacao=?
           WHERE id=? AND usuario_id=?""",
        (d["pilar_id"], d["titulo"], d["roteiro"], d["plataforma"], d["status"], d["data_publicacao"],
         post_id, usuario_id),
    )
    db.commit()
    return cur.rowcount > 0


def excluir(usuario_id, post_id):
    db = get_db()
    cur = db.execute("DELETE FROM post WHERE id = ? AND usuario_id = ?", (post_id, usuario_id))
    db.commit()
    return cur.rowcount > 0


def avancar_status(usuario_id, post_id):
    """Move o post para a próxima etapa. Ao publicar sem data, usa a data de hoje.
    Retorna o novo status, ou None se o post não existe ou já está publicado."""
    post = buscar(usuario_id, post_id)
    if not post or post["status"] == "publicado":
        return None
    novo = STATUS[STATUS.index(post["status"]) + 1]
    data = post["data_publicacao"]
    if novo == "publicado" and not data:
        data = date.today().isoformat()
    db = get_db()
    db.execute(
        "UPDATE post SET status = ?, data_publicacao = ? WHERE id = ? AND usuario_id = ?",
        (novo, data, post_id, usuario_id),
    )
    db.commit()
    return novo


def contar_por_status(usuario_id):
    rows = get_db().execute(
        "SELECT status, COUNT(*) AS total FROM post WHERE usuario_id = ? GROUP BY status", (usuario_id,)
    ).fetchall()
    contagem = {s: 0 for s in STATUS}
    for r in rows:
        contagem[r["status"]] = r["total"]
    return contagem


def proximos(usuario_id, limite=5):
    return get_db().execute(
        _SELECT + """ WHERE po.usuario_id = ? AND po.status != 'publicado'
                      AND po.data_publicacao IS NOT NULL AND po.data_publicacao >= ?
                      ORDER BY po.data_publicacao LIMIT ?""",
        (usuario_id, date.today().isoformat(), limite),
    ).fetchall()


def agendados(usuario_id):
    """Posts com data, para a visão de calendário (agrupados por data na view)."""
    return get_db().execute(
        _SELECT + " WHERE po.usuario_id = ? AND po.data_publicacao IS NOT NULL ORDER BY po.data_publicacao, po.id",
        (usuario_id,),
    ).fetchall()
