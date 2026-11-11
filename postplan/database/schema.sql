-- PostPlan - Projeto físico do banco de dados (SQLite 3)
-- Normalizado até a 3FN. Integridade referencial ativada via PRAGMA foreign_keys = ON.

CREATE TABLE IF NOT EXISTS usuario (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL CHECK (length(nome) BETWEEN 2 AND 80),
    email       TEXT    NOT NULL UNIQUE,
    senha_hash  TEXT    NOT NULL,
    criado_em   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS pilar (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id  INTEGER NOT NULL,
    nome        TEXT    NOT NULL CHECK (length(nome) BETWEEN 2 AND 40),
    cor         TEXT    NOT NULL DEFAULT '#7c5cff' CHECK (cor GLOB '#[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]'),
    UNIQUE (usuario_id, nome),
    FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS post (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id       INTEGER NOT NULL,
    pilar_id         INTEGER,
    titulo           TEXT    NOT NULL CHECK (length(titulo) BETWEEN 3 AND 120),
    roteiro          TEXT    NOT NULL DEFAULT '' CHECK (length(roteiro) <= 2000),
    plataforma       TEXT    NOT NULL CHECK (plataforma IN ('Instagram','TikTok','YouTube','Pinterest','Blog')),
    status           TEXT    NOT NULL DEFAULT 'ideia' CHECK (status IN ('ideia','roteirizado','gravado','editado','publicado')),
    data_publicacao  TEXT,
    criado_em        TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE,
    FOREIGN KEY (pilar_id)   REFERENCES pilar (id)   ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_post_usuario_status ON post (usuario_id, status);
CREATE INDEX IF NOT EXISTS idx_post_data           ON post (usuario_id, data_publicacao);
