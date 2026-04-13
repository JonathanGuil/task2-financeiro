-- Tabela usuario
CREATE TABLE IF NOT EXISTS usuario (
    id       SERIAL PRIMARY KEY,
    nome     TEXT NOT NULL,
    login    TEXT NOT NULL UNIQUE,
    senha    TEXT NOT NULL,
    situacao TEXT NOT NULL DEFAULT 'ativo'
);

-- Tabela lancamento
CREATE TABLE IF NOT EXISTS lancamento (
    id               SERIAL PRIMARY KEY,
    descricao        TEXT NOT NULL,
    data_lancamento  DATE NOT NULL,
    valor            NUMERIC(10,2) NOT NULL,
    tipo_lancamento  TEXT NOT NULL CHECK (tipo_lancamento IN ('receita','despesa')),
    situacao         TEXT NOT NULL DEFAULT 'pendente'
);

-- Dados iniciais: usuario
INSERT INTO usuario (nome, login, senha, situacao) VALUES
    ('Administrador', 'admin', 'admin123', 'ativo');

-- Dados iniciais: 10 lancamentos
INSERT INTO lancamento (descricao, data_lancamento, valor, tipo_lancamento, situacao) VALUES
    ('Salário mensal',          '2026-04-01', 5000.00, 'receita',  'efetivado'),
    ('Aluguel escritório',      '2026-04-02',  800.00, 'despesa',  'efetivado'),
    ('Venda de produto A',      '2026-04-03',  320.50, 'receita',  'efetivado'),
    ('Conta de energia',        '2026-04-05',  210.75, 'despesa',  'efetivado'),
    ('Freelance consultoria',   '2026-04-07',  900.00, 'receita',  'pendente'),
    ('Internet corporativa',    '2026-04-08',  150.00, 'despesa',  'efetivado'),
    ('Venda de produto B',      '2026-04-10',  480.00, 'receita',  'pendente'),
    ('Material de escritório',  '2026-04-11',   95.30, 'despesa',  'pendente'),
    ('Reembolso despesas',      '2026-04-12',  200.00, 'receita',  'pendente'),
    ('Manutenção equipamento',  '2026-04-12',  350.00, 'despesa',  'pendente');
