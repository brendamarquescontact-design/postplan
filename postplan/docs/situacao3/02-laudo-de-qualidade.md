# Laudo de qualidade — PostPlan

## 1. Verificação e validação feitas pelo desenvolvimento

### Testes automatizados
- **41 testes, 41 aprovados** (`python -m pytest`). Saída completa em [`../situacao2/resultado-testes-automatizados.txt`](../situacao2/resultado-testes-automatizados.txt).
- Unitários (Models): cadastro, autenticação, hash de senha, validações de cada campo, isolamento entre usuários, funil de status, exclusão de pilar, filtros, tentativa de SQL injection.
- Integração (Controllers + Views + banco): fluxo cadastro/login, CRUD de posts e pilares, páginas de erro, calendário, XSS escapado, bloqueio por CSRF.

### Erros encontrados e corrigidos durante o desenvolvimento
| # | Erro | Como foi encontrado | Correção | Evidência |
|---|---|---|---|---|
| 1 | Erro 500 ao abrir a lista de posts: `STATUS_ROTULO is undefined` dentro do macro do selo de status | Falha de 6 testes de integração na primeira execução | `STATUS_ROTULO` registrado como global do Jinja em `app/__init__.py`; os 6 testes passaram | Saída do pytest |
| 2 | Coluna “Ações” da tabela com borda desalinhada | Inspeção visual do print da tela de posts | Botões envolvidos em `<div class="acoes">` dentro da célula | `evidencias/05-lista-posts.png` |

## 2. Checklist de requisitos
| Requisito | Situação | Evidência |
|---|---|---|
| RF01 Cadastro | Atendido | testes + `evidencias/02-cadastro-erro-validacao.png` |
| RF02 Login/logout | Atendido | testes + `evidencias/01-login.png` |
| RF03 CRUD de posts | Atendido | testes + `evidencias/05-lista-posts.png` |
| RF04 Campos do post | Atendido | `evidencias/06-post-erros-validacao.png` |
| RF05 Avançar status | Atendido | `test_avancar_status_percorre_o_funil` |
| RF06 Pilares | Atendido | `evidencias/03-pilares.png` |
| RF07 Filtros e busca | Atendido | `test_filtro_por_status_na_lista` |
| RF08 Calendário | Atendido | `evidencias/07-calendario.png` |
| RF09 Painel | Atendido | `evidencias/04-painel.png` |
| RNF03 Responsividade | Atendido | `evidencias/09-mobile-lista.png` |
| Tratamento de erros (404) | Atendido | `evidencias/08-erro-404.png` |

## 3. Feedback dos 5 testadores (PREENCHER)
> Preencha esta seção com o que os colegas reportaram no formulário (`01-formulario-de-teste.md`). Não omita falhas: o professor pede expressamente que elas apareçam.

| # | Testador | Problema ou sugestão | Gravidade (alta/média/baixa) | Evidência (print) | Correção feita | Status |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |

## 4. Limitações conhecidas
- No plano gratuito de hospedagem o arquivo SQLite pode ser apagado a cada reinício; para uso real, usar PostgreSQL ou disco persistente.
- Não há recuperação de senha por e-mail.
- Não há limite de tentativas de login (proteção contra força bruta).
- O calendário é uma lista agrupada por dia, não uma grade mensal.
