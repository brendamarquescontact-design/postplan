"""Testes de integração: controllers + views + banco."""
from conftest import extrair_csrf, post_valido


def test_rotas_protegidas_redirecionam_para_login(client):
    for url in ["/", "/posts", "/posts/novo", "/calendario", "/pilares/"]:
        r = client.get(url)
        assert r.status_code == 302 and "/login" in r.headers["Location"], url


def test_cadastro_e_login_fluxo_completo(client):
    r = client.post("/cadastro", data={"nome": "Brenda", "email": "b@x.com", "senha": "senha1234"}, follow_redirects=True)
    assert "Conta criada" in r.get_data(as_text=True)
    r = client.post("/login", data={"email": "b@x.com", "senha": "senha1234"}, follow_redirects=True)
    assert "Seu painel" in r.get_data(as_text=True)


def test_login_invalido_mostra_mensagem(client):
    r = client.post("/login", data={"email": "x@x.com", "senha": "qualquer123"})
    assert "E-mail ou senha incorretos" in r.get_data(as_text=True)


def test_cadastro_com_erro_mostra_mensagens_e_mantem_dados(client):
    r = client.post("/cadastro", data={"nome": "Bia", "email": "invalido", "senha": "123"})
    html = r.get_data(as_text=True)
    assert "Informe um e-mail válido" in html and "pelo menos 8 caracteres" in html
    assert 'value="Bia"' in html


def test_logout(logado):
    logado.post("/logout")
    assert logado.get("/").status_code == 302


def test_criar_post_aparece_na_lista(logado):
    r = logado.post("/posts/novo", data=post_valido(titulo="Meu primeiro Reel"), follow_redirects=True)
    html = r.get_data(as_text=True)
    assert "Post criado com sucesso" in html and "Meu primeiro Reel" in html


def test_criar_post_invalido_mantem_formulario_com_erros(logado):
    r = logado.post("/posts/novo", data=post_valido(titulo="ab", roteiro="texto digitado"))
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "entre 3 e 120 caracteres" in html and "texto digitado" in html


def test_editar_e_excluir_post(logado):
    logado.post("/posts/novo", data=post_valido())
    r = logado.post("/posts/1/editar", data=post_valido(titulo="Título novo"), follow_redirects=True)
    assert "Título novo" in r.get_data(as_text=True)
    r = logado.post("/posts/1/excluir", follow_redirects=True)
    assert "Post excluído" in r.get_data(as_text=True)
    assert logado.get("/posts/1/editar").status_code == 404


def test_avancar_etapa_pela_interface(logado):
    logado.post("/posts/novo", data=post_valido())
    r = logado.post("/posts/1/avancar", follow_redirects=True)
    assert "Roteirizado" in r.get_data(as_text=True)


def test_post_inexistente_da_404_com_pagina_amigavel(logado):
    r = logado.get("/posts/999/editar")
    assert r.status_code == 404 and "Página não encontrada" in r.get_data(as_text=True)


def test_nao_acessa_post_de_outra_usuaria(app):
    a, b = app.test_client(), app.test_client()
    for c, mail in ((a, "a@x.com"), (b, "b@x.com")):
        c.post("/cadastro", data={"nome": "Usuária", "email": mail, "senha": "senha1234"})
        c.post("/login", data={"email": mail, "senha": "senha1234"})
    a.post("/posts/novo", data=post_valido(titulo="Só da A"))
    assert b.get("/posts/1/editar").status_code == 404
    assert b.post("/posts/1/excluir").status_code == 404
    assert "Só da A" not in b.get("/posts").get_data(as_text=True)


def test_filtro_por_status_na_lista(logado):
    logado.post("/posts/novo", data=post_valido(titulo="Ideia solta"))
    logado.post("/posts/novo", data=post_valido(titulo="Já gravado", status="gravado"))
    html = logado.get("/posts?status=gravado").get_data(as_text=True)
    assert "Já gravado" in html and "Ideia solta" not in html


def test_pilares_criar_duplicado_e_excluir(logado):
    logado.post("/pilares/", data={"nome": "Rotina", "cor": "#aa00ff"})
    r = logado.post("/pilares/", data={"nome": "Rotina", "cor": "#aa00ff"})
    assert "já tem um pilar" in r.get_data(as_text=True)
    r = logado.post("/pilares/1/excluir", follow_redirects=True)
    assert "Pilar excluído" in r.get_data(as_text=True)


def test_calendario_agrupa_por_data(logado):
    logado.post("/posts/novo", data=post_valido(titulo="Dia 1", data_publicacao="2026-12-01"))
    html = logado.get("/calendario").get_data(as_text=True)
    assert "01/12/2026" in html and "Dia 1" in html


def test_xss_e_escapado_na_lista(logado):
    logado.post("/posts/novo", data=post_valido(titulo="<script>alert(1)</script>"))
    html = logado.get("/posts").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;" in html


def test_csrf_bloqueia_post_sem_token(app):
    app.config["CSRF_ENABLED"] = True
    c = app.test_client()
    assert c.post("/login", data={"email": "a@a.com", "senha": "x"}).status_code == 400


def test_csrf_aceita_post_com_token(app):
    app.config["CSRF_ENABLED"] = True
    c = app.test_client()
    token = extrair_csrf(c.get("/login").get_data(as_text=True))
    r = c.post("/login", data={"email": "a@a.com", "senha": "x", "csrf_token": token})
    assert r.status_code == 200
