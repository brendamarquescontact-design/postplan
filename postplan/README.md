# PostPlan

Planejador de conteúdo para criadores: organize cada post da ideia à publicação.
Projeto Integrador Transdisciplinar (PIT II) — Engenharia de Software.

**Stack:** Python + Flask (MVC) · SQLite · HTML/CSS/JS · pytest

## Rodar localmente
```bash
pip install -r requirements.txt
python run.py          # http://localhost:5000
python -m pytest       # 41 testes
```

## Documentação
| Situação | Conteúdo |
|---|---|
| 1 — Planejamento | [`docs/situacao1`](docs/situacao1): escopo, requisitos, UML, IHC, DER, dicionário de dados |
| 2 — Desenvolvimento | [`docs/situacao2`](docs/situacao2): arquitetura, manual de uso, resultado dos testes |
| 3 — Validação | [`docs/situacao3`](docs/situacao3): formulário de teste, laudo de qualidade, roteiro do vídeo, evidências |

Esquema do banco: [`database/schema.sql`](database/schema.sql)

## Publicar online (exemplo: Render)
1. Suba este repositório no GitHub.
2. No Render, crie um *Web Service* a partir do repositório.
3. Build: `pip install -r requirements.txt` · Start: `gunicorn run:app`
4. Defina a variável `SECRET_KEY` com um valor aleatório longo.
5. Observação: no plano gratuito o disco é temporário, então o arquivo SQLite é recriado a cada deploy/reinício. Para uso real, troque por PostgreSQL ou adicione um disco persistente.
