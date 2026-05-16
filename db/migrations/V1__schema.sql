-- Tabela usuario
CREATE TABLE usuario (
    id       SERIAL PRIMARY KEY,
    nome     TEXT NOT NULL,
    login    TEXT NOT NULL UNIQUE,
    senha    TEXT NOT NULL,
    email    TEXT,
    situacao TEXT NOT NULL DEFAULT 'ativo'
);

-- Tabela lancamento
CREATE TABLE lancamento (
    id               SERIAL PRIMARY KEY,
    descricao        TEXT NOT NULL,
    data_lancamento  DATE NOT NULL,
    valor            NUMERIC(10,2) NOT NULL,
    tipo_lancamento  TEXT NOT NULL CHECK (tipo_lancamento IN ('receita','despesa')),
    situacao         TEXT NOT NULL DEFAULT 'pendente'
);
