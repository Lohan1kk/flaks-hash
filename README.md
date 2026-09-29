# Portfólio Flask — páginas pessoais + área restrita (hash + SQLite)

Aplicação Flask com:

- **Páginas públicas** sobre o perfil (estilo LinkedIn): Sobre e Experiência/Formação
- **Login** com hash **SHA-256** e comparação via `hmac.compare_digest` (mesmo padrão da atividade de senhas)
- **2 páginas com acesso restrito**, conteúdo dinâmico vindo do **SQLite**:
  1. `/painel` — projetos internos + logs de acesso
  2. `/laboratorio` — conceitos da atividade de hash / força bruta

> Recorte didático: SHA-256 puro facilita a visualização em aula, mas **não** deve ser usado para senhas reais. Em produção use Argon2id, scrypt ou PBKDF2 (OWASP Password Storage Cheat Sheet).

## Como rodar

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abra [http://127.0.0.1:45217](http://127.0.0.1:45217).

Na primeira execução o arquivo `portfolio.db` é criado e populado automaticamente.

## Credenciais fictícias (atividade)

| Usuário         | Senha      |
|-----------------|------------|
| `aluno_exemplo` | `Aula@1234` |

Não use senhas pessoais. Para alterar o perfil, edite o seed em `init_db()` dentro de `app.py` (ou atualize as linhas nas tabelas `perfil`, `experiencias`, etc.).

## Rotas

| Rota            | Acesso     | Origem dos dados                          |
|-----------------|------------|-------------------------------------------|
| `/`             | Público    | `perfil`, `habilidades`                   |
| `/experiencia`  | Público    | `experiencias`, `formacoes`               |
| `/login`        | Público    | `usuarios` (compara hashes)               |
| `/painel`       | Autenticado| `projetos_privados`, `logs_acesso`        |
| `/laboratorio`  | Autenticado| `laboratorio_hashes`, hash do usuário demo|
| `/logout`       | Sessão     | —                                         |

## Personalizar com seus dados do LinkedIn

1. Abra `app.py` e localize o `INSERT INTO perfil` em `init_db()`.
2. Troque nome, título, resumo, e-mail, LinkedIn e GitHub.
3. Ajuste experiências, formações e habilidades nas listas abaixo.
4. Apague `portfolio.db` e rode de novo **ou** atualize as tabelas com SQL.

## Estrutura

```
app.py
requirements.txt
templates/
  base.html, index.html, experiencia.html,
  login.html, painel.html, laboratorio.html
static/css/style.css
portfolio.db   # gerado em runtime
```
