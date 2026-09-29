"""
Portfólio pessoal em Flask com autenticação SHA-256 + SQLite.
Complementa a atividade de hash/força bruta (Prof. Felipe Garbin):
páginas públicas + 2 páginas com acesso restrito e conteúdo dinâmico.
"""

from __future__ import annotations

import hashlib
import hmac
import sqlite3
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

BASE_DIR = Path(__file__).resolve().parent
CAMINHO_BANCO = BASE_DIR / "portfolio.db"

app = Flask(__name__)
app.secret_key = "dev-chave-didatica-troque-em-producao"


# ---------------------------------------------------------------------------
# Banco e hash (mesmo padrão da atividade de senhas)
# ---------------------------------------------------------------------------

def calcular_hash(senha: str) -> str:
    """Transforma uma string em um resumo hexadecimal SHA-256."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(CAMINHO_BANCO)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def fechar_db(_exc=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Cria tabelas e popula dados iniciais (idempotente)."""
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        conexao.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                usuario TEXT PRIMARY KEY,
                senha_hash TEXT NOT NULL,
                nome_exibicao TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS perfil (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                nome TEXT NOT NULL,
                titulo TEXT NOT NULL,
                resumo TEXT NOT NULL,
                localizacao TEXT NOT NULL,
                email TEXT NOT NULL,
                linkedin TEXT,
                github TEXT,
                telefone TEXT
            );

            CREATE TABLE IF NOT EXISTS experiencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cargo TEXT NOT NULL,
                empresa TEXT NOT NULL,
                periodo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS formacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                curso TEXT NOT NULL,
                instituicao TEXT NOT NULL,
                periodo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS habilidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                nivel TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS projetos_privados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                status TEXT NOT NULL,
                resumo TEXT NOT NULL,
                tecnologias TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS laboratorio_hashes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                conceito TEXT NOT NULL,
                exemplo TEXT NOT NULL,
                conclusao TEXT NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS logs_acesso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                pagina TEXT NOT NULL,
                momento TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            );
            """
        )

        # Credenciais fictícias da atividade (NÃO use senhas pessoais).
        demo_user = "aluno_exemplo"
        demo_pass = "Aula@1234"
        demo_hash = calcular_hash(demo_pass)
        conexao.execute(
            """
            INSERT INTO usuarios (usuario, senha_hash, nome_exibicao) VALUES (?, ?, ?)
            ON CONFLICT(usuario) DO UPDATE SET
                senha_hash = excluded.senha_hash,
                nome_exibicao = excluded.nome_exibicao
            """,
            (demo_user, demo_hash, "Aluno Exemplo"),
        )

        # Perfil estilo LinkedIn — edite com seus dados reais.
        perfil = conexao.execute("SELECT id FROM perfil WHERE id = 1").fetchone()
        if perfil is None:
            conexao.execute(
                """
                INSERT INTO perfil (
                    id, nome, titulo, resumo, localizacao, email, linkedin, github, telefone
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "Lucas Lohan",
                    "Estudante de Ciência de Dados",
                    (
                        "Página pessoal em Flask. Tem páginas públicas e duas áreas "
                        "com login (hash SHA-256 + SQLite)."
                    ),
                    "Brasil",
                    "lucas.lohan@email.com",
                    "https://www.linkedin.com/in/seu-perfil",
                    "https://github.com/seu-usuario",
                    None,
                ),
            )

        if conexao.execute("SELECT COUNT(*) FROM experiencias").fetchone()[0] == 0:
            conexao.executemany(
                """
                INSERT INTO experiencias (cargo, empresa, periodo, descricao, ordem)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        "Estudante — Ciência de Dados",
                        "Instituição de Ensino",
                        "2024 — Atual",
                        "Cursando ciência de dados. Uso Python, SQL e Flask nas aulas.",
                        1,
                    ),
                    (
                        "Projetos da disciplina",
                        "Laboratório de Python",
                        "2025 — 2026",
                        "Atividades com Flask, SQLite e hash de senhas.",
                        2,
                    ),
                ],
            )

        if conexao.execute("SELECT COUNT(*) FROM formacoes").fetchone()[0] == 0:
            conexao.executemany(
                """
                INSERT INTO formacoes (curso, instituicao, periodo, descricao, ordem)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        "Ciência de Dados",
                        "Instituição de Ensino",
                        "Em andamento",
                        "Ênfase em Python, SQL, estatística e segurança aplicada.",
                        1,
                    ),
                    (
                        "Segurança em Python — Atividade Hash & SQLite",
                        "Prof. Felipe Garbin",
                        "2026",
                        (
                            "Cadastro/login com SHA-256, comparação segura de hashes "
                            "e demonstração de força bruta em PIN fictício."
                        ),
                        2,
                    ),
                ],
            )

        if conexao.execute("SELECT COUNT(*) FROM habilidades").fetchone()[0] == 0:
            conexao.executemany(
                """
                INSERT INTO habilidades (nome, categoria, nivel)
                VALUES (?, ?, ?)
                """,
                [
                    ("Python", "Linguagens", "Intermediário"),
                    ("Flask", "Web", "Básico / Intermediário"),
                    ("SQLite", "Dados", "Intermediário"),
                    ("SQL", "Dados", "Intermediário"),
                    ("Hash SHA-256", "Segurança", "Conceitos aplicados"),
                    ("Análise de dados", "Ciência de Dados", "Em formação"),
                    ("Git / GitHub", "Ferramentas", "Intermediário"),
                    ("HTML / CSS", "Web", "Intermediário"),
                ],
            )

        if conexao.execute("SELECT COUNT(*) FROM projetos_privados").fetchone()[0] == 0:
            conexao.executemany(
                """
                INSERT INTO projetos_privados
                    (titulo, status, resumo, tecnologias, atualizado_em)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        "API de anotações pessoais",
                        "Em progresso",
                        (
                            "Rascunho de API Flask para notas privadas, com login "
                            "baseado em hash e armazenamento em SQLite."
                        ),
                        "Flask, SQLite, hashlib",
                        "2026-09-20",
                    ),
                    (
                        "Dashboard de métricas acadêmicas",
                        "Planejado",
                        (
                            "Painel interno para acompanhar entregas, notas e "
                            "atividade de laboratório — conteúdo dinâmico do banco."
                        ),
                        "Python, SQLite, Chart.js (previsto)",
                        "2026-09-18",
                    ),
                    (
                        "Checklist de hardening de senhas",
                        "Concluído (didático)",
                        (
                            "Documento interno contrastando SHA-256 puro vs. "
                            "Argon2id / scrypt / PBKDF2 (OWASP Password Storage)."
                        ),
                        "Markdown, OWASP",
                        "2026-09-15",
                    ),
                ],
            )

        if conexao.execute("SELECT COUNT(*) FROM laboratorio_hashes").fetchone()[0] == 0:
            conexao.executemany(
                """
                INSERT INTO laboratorio_hashes
                    (titulo, conceito, exemplo, conclusao, ordem)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        "Cadastro guarda o hash, não a senha",
                        (
                            "No cadastro o sistema calcula SHA-256(senha) e grava "
                            "apenas o resumo na coluna senha_hash."
                        ),
                        "aluno_exemplo → e4c0d05c70ec8149… (senha Aula@1234)",
                        (
                            "A senha original não aparece na tabela. Isso evita "
                            "expor o texto em claro, mas não basta sozinho."
                        ),
                        1,
                    ),
                    (
                        "Login compara hashes",
                        (
                            "Na tentativa de login, o sistema hasheia a senha "
                            "informada e compara com o valor guardado "
                            "(hmac.compare_digest)."
                        ),
                        "Senha errada → Login negado. Senha correta → autorizado.",
                        (
                            "O banco não precisa recuperar a senha original: "
                            "basta comparar dois resumos hexadecimais."
                        ),
                        2,
                    ),
                    (
                        "Força bruta em PIN curto",
                        (
                            "Com o hash exposto e um espaço pequeno (ex.: 4–7 dígitos), "
                            "é possível testar todas as combinações localmente."
                        ),
                        "PIN 0427211 encontrado após ~427 mil tentativas em < 1 s.",
                        (
                            "Hash rápido + segredo curto = quebra fácil. Em sistemas "
                            "reais use Argon2id/scrypt/PBKDF2 com salt e custo alto."
                        ),
                        3,
                    ),
                    (
                        "Recorte didático vs. produção",
                        (
                            "SHA-256 puro facilita visualizar o processo em aula, "
                            "mas não deve armazenar senhas reais."
                        ),
                        "Referência: OWASP Password Storage Cheat Sheet.",
                        (
                            "Limites de tentativas no login ajudam na interface, "
                            "mas não substituem armazenamento adequado após vazamento."
                        ),
                        4,
                    ),
                ],
            )

        conexao.commit()


def login_obrigatorio(view):
    """Decorator: redireciona para /login se a sessão não estiver autenticada."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if "usuario" not in session:
            flash("Faça login para acessar esta área restrita.", "aviso")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def registrar_acesso(pagina: str) -> None:
    usuario = session.get("usuario")
    if not usuario:
        return
    get_db().execute(
        "INSERT INTO logs_acesso (usuario, pagina) VALUES (?, ?)",
        (usuario, pagina),
    )
    get_db().commit()


# ---------------------------------------------------------------------------
# Contexto global dos templates
# ---------------------------------------------------------------------------

@app.context_processor
def injetar_perfil():
    try:
        perfil = get_db().execute("SELECT * FROM perfil WHERE id = 1").fetchone()
    except sqlite3.OperationalError:
        perfil = None
    return {
        "perfil_global": perfil,
        "usuario_logado": session.get("usuario"),
        "nome_logado": session.get("nome_exibicao"),
    }


# ---------------------------------------------------------------------------
# Rotas públicas
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    db = get_db()
    perfil = db.execute("SELECT * FROM perfil WHERE id = 1").fetchone()
    habilidades = db.execute(
        "SELECT * FROM habilidades ORDER BY categoria, nome"
    ).fetchall()
    return render_template("index.html", perfil=perfil, habilidades=habilidades)


@app.route("/experiencia")
def experiencia():
    db = get_db()
    experiencias = db.execute(
        "SELECT * FROM experiencias ORDER BY ordem"
    ).fetchall()
    formacoes = db.execute(
        "SELECT * FROM formacoes ORDER BY ordem"
    ).fetchall()
    return render_template(
        "experiencia.html",
        experiencias=experiencias,
        formacoes=formacoes,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("usuario"):
        return redirect(url_for("painel"))

    if request.method == "POST":
        usuario = (request.form.get("usuario") or "").strip()
        senha = request.form.get("senha") or ""
        db = get_db()
        registro = db.execute(
            "SELECT usuario, senha_hash, nome_exibicao FROM usuarios WHERE usuario = ?",
            (usuario,),
        ).fetchone()

        if registro is None:
            flash("Usuário não encontrado.", "erro")
        else:
            hash_tentativa = calcular_hash(senha)
            if hmac.compare_digest(hash_tentativa, registro["senha_hash"]):
                session.clear()
                session["usuario"] = registro["usuario"]
                session["nome_exibicao"] = registro["nome_exibicao"]
                flash("Login autorizado.", "ok")
                destino = request.args.get("next") or url_for("painel")
                if not destino.startswith("/"):
                    destino = url_for("painel")
                return redirect(destino)
            flash("Senha incorreta.", "erro")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "ok")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Rotas restritas (autenticação obrigatória)
# ---------------------------------------------------------------------------

@app.route("/painel")
@login_obrigatorio
def painel():
    """Página restrita 1: projetos internos dinâmicos do SQLite."""
    registrar_acesso("painel")
    db = get_db()
    projetos = db.execute(
        "SELECT * FROM projetos_privados ORDER BY atualizado_em DESC"
    ).fetchall()
    logs = db.execute(
        """
        SELECT * FROM logs_acesso
        WHERE usuario = ?
        ORDER BY id DESC
        LIMIT 8
        """,
        (session["usuario"],),
    ).fetchall()
    return render_template("painel.html", projetos=projetos, logs=logs)


@app.route("/laboratorio")
@login_obrigatorio
def laboratorio():
    """Página restrita 2: conceitos da atividade de hash / força bruta."""
    registrar_acesso("laboratorio")
    db = get_db()
    cards = db.execute(
        "SELECT * FROM laboratorio_hashes ORDER BY ordem"
    ).fetchall()
    # Demonstra que só o hash (não a senha) está no banco.
    usuario_demo = db.execute(
        "SELECT usuario, senha_hash FROM usuarios WHERE usuario = ?",
        ("aluno_exemplo",),
    ).fetchone()
    return render_template(
        "laboratorio.html",
        cards=cards,
        usuario_demo=usuario_demo,
    )


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=45217, debug=True)
