"""Testes unitários dos Models (regras de negócio e integridade)."""
import pytest

from app.models import ValidationError, pilar, post, usuario


@pytest.fixture
def uid(app):
    with app.app_context():
        yield usuario.criar("Ana Silva", "ana@exemplo.com", "senha1234")


def test_usuario_cria_e_autentica(app, uid):
    with app.app_context():
        assert usuario.autenticar("ANA@exemplo.com ", "senha1234")["id"] == uid
        assert usuario.autenticar("ana@exemplo.com", "errada123") is None


def test_usuario_senha_nao_fica_em_texto_puro(app, uid):
    with app.app_context():
        from app.db import get_db
        h = get_db().execute("SELECT senha_hash FROM usuario WHERE id=?", (uid,)).fetchone()[0]
        assert "senha1234" not in h


@pytest.mark.parametrize("nome,email,senha,campo", [
    ("A", "a@a.com", "senha1234", "nome"),
    ("Ana", "sem-arroba", "senha1234", "email"),
    ("Ana", "a@a.com", "curta", "senha"),
])
def test_usuario_validacao(app, nome, email, senha, campo):
    with app.app_context(), pytest.raises(ValidationError) as e:
        usuario.criar(nome, email, senha)
    assert campo in e.value.errors


def test_usuario_email_duplicado(app, uid):
    with app.app_context(), pytest.raises(ValidationError) as e:
        usuario.criar("Outra", "ana@exemplo.com", "senha1234")
    assert "email" in e.value.errors


def test_pilar_criar_listar_duplicado(app, uid):
    with app.app_context():
        pilar.criar(uid, "Rotina", "#ff0000")
        assert [p["nome"] for p in pilar.listar(uid)] == ["Rotina"]
        with pytest.raises(ValidationError):
            pilar.criar(uid, "Rotina", "#00ff00")
        with pytest.raises(ValidationError):
            pilar.criar(uid, "Viagem", "vermelho")


def test_post_crud(app, uid):
    with app.app_context():
        pid = post.criar(uid, {"titulo": "Tour Sydney", "plataforma": "YouTube"})
        assert post.buscar(uid, pid)["status"] == "ideia"
        assert post.atualizar(uid, pid, {"titulo": "Tour Bondi", "plataforma": "TikTok", "status": "gravado"})
        assert post.buscar(uid, pid)["titulo"] == "Tour Bondi"
        assert post.excluir(uid, pid)
        assert post.buscar(uid, pid) is None


@pytest.mark.parametrize("dados,campo", [
    ({"titulo": "ab", "plataforma": "Instagram"}, "titulo"),
    ({"titulo": "x" * 121, "plataforma": "Instagram"}, "titulo"),
    ({"titulo": "Válido", "plataforma": "Orkut"}, "plataforma"),
    ({"titulo": "Válido", "plataforma": "Blog", "status": "arquivado"}, "status"),
    ({"titulo": "Válido", "plataforma": "Blog", "data_publicacao": "31/12/2026"}, "data_publicacao"),
    ({"titulo": "Válido", "plataforma": "Blog", "data_publicacao": "2026-02-30"}, "data_publicacao"),
    ({"titulo": "Válido", "plataforma": "Blog", "status": "publicado"}, "data_publicacao"),
    ({"titulo": "Válido", "plataforma": "Blog", "roteiro": "x" * 2001}, "roteiro"),
    ({"titulo": "Válido", "plataforma": "Blog", "pilar_id": "999"}, "pilar_id"),
    ({"titulo": "Válido", "plataforma": "Blog", "pilar_id": "abc"}, "pilar_id"),
])
def test_post_validacao(app, uid, dados, campo):
    with app.app_context(), pytest.raises(ValidationError) as e:
        post.criar(uid, dados)
    assert campo in e.value.errors


def test_post_nao_aceita_pilar_de_outra_usuaria(app, uid):
    with app.app_context():
        outra = usuario.criar("Bia", "bia@exemplo.com", "senha1234")
        pilar_alheio = pilar.criar(outra, "Segredo", "#000000")
        with pytest.raises(ValidationError):
            post.criar(uid, {"titulo": "Teste", "plataforma": "Blog", "pilar_id": str(pilar_alheio)})


def test_post_isolamento_entre_usuarias(app, uid):
    with app.app_context():
        pid = post.criar(uid, {"titulo": "Privado", "plataforma": "Blog"})
        outra = usuario.criar("Bia", "bia@exemplo.com", "senha1234")
        assert post.buscar(outra, pid) is None
        assert post.excluir(outra, pid) is False
        assert post.listar(outra) == []


def test_avancar_status_percorre_o_funil(app, uid):
    with app.app_context():
        pid = post.criar(uid, {"titulo": "Funil", "plataforma": "Blog"})
        vistos = [post.avancar_status(uid, pid) for _ in range(4)]
        assert vistos == ["roteirizado", "gravado", "editado", "publicado"]
        assert post.buscar(uid, pid)["data_publicacao"]  # preenchida automaticamente
        assert post.avancar_status(uid, pid) is None


def test_excluir_pilar_mantem_posts(app, uid):
    with app.app_context():
        pi = pilar.criar(uid, "Receitas", "#123456")
        pid = post.criar(uid, {"titulo": "Bolo", "plataforma": "Blog", "pilar_id": str(pi)})
        pilar.excluir(uid, pi)
        assert post.buscar(uid, pid)["pilar_id"] is None


def test_filtros_e_contagem(app, uid):
    with app.app_context():
        post.criar(uid, {"titulo": "Café em Melbourne", "plataforma": "Instagram"})
        post.criar(uid, {"titulo": "Praia", "plataforma": "TikTok", "status": "gravado"})
        assert len(post.listar(uid, busca="café")) == 1
        assert len(post.listar(uid, status="gravado")) == 1
        assert post.contar_por_status(uid)["ideia"] == 1


def test_sql_injection_na_busca_e_tratada_como_texto(app, uid):
    with app.app_context():
        post.criar(uid, {"titulo": "Normal", "plataforma": "Blog"})
        assert post.listar(uid, busca="' OR 1=1 --") == []
        assert len(post.listar(uid)) == 1
