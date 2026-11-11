# Situação 2 — Arquitetura e manual de uso

## Stack
| Item | Escolha |
|---|---|
| Back-end | Python 3 + Flask |
| Padrão | MVC (Model / View / Controller) |
| Banco de dados | SQLite 3 (`database/schema.sql`) |
| Front-end | HTML5 (templates Jinja2), CSS3 e JavaScript puro |
| Testes | pytest (41 testes: unitários dos Models + integração das rotas) |
| Modo de codificação | Tradicional |

## Estrutura (MVC)
```
app/
  models/        -> Model: regras de negócio, validação e SQL (usuario, pilar, post)
  controllers/   -> Controller: rotas Flask (auth, posts, pilares)
  templates/     -> View: HTML com Jinja2
  static/        -> CSS e JS
  db.py          -> conexão e criação do esquema
tests/           -> testes automatizados
database/        -> schema.sql
docs/            -> documentação das 3 situações
```
Fluxo: requisição → Controller → Model (valida e acessa o banco) → Controller → View.

## Tratamento de erros
- Validação no servidor com mensagens por campo (`ValidationError`); o formulário volta preenchido.
- Páginas amigáveis para 400, 404 e 500.
- Acesso a post/pilar de outra pessoa retorna 404 (não revela que existe).
- CSRF: formulários POST sem token válido são recusados (400).

## Manual de uso
1. **Criar conta:** em “Cadastre-se”, informe nome, e-mail e senha de pelo menos 8 caracteres.
2. **Entrar:** use e-mail e senha cadastrados.
3. **Criar pilares (opcional):** menu “Pilares” → nome e cor → “Adicionar”.
4. **Criar um post:** “Posts” → “+ Novo post” → título, plataforma, pilar, status, data e roteiro → “Criar post”.
5. **Avançar etapa:** na lista, “Avançar etapa” move o post no funil (Ideia → Roteirizado → Gravado → Editado → Publicado).
6. **Filtrar:** escolha status ou pilar, ou busque pelo título.
7. **Calendário:** veja os posts que têm data, agrupados por dia.
8. **Excluir:** o sistema pede confirmação antes.

## Como executar
```bash
pip install -r requirements.txt
python run.py            # abre em http://localhost:5000
python -m pytest         # roda os testes
```
Variáveis opcionais: `SECRET_KEY` (obrigatória em produção), `DATABASE` (caminho do arquivo .sqlite3), `PORT`.
