-- Usuario inicial
INSERT INTO usuario (nome, login, senha, email, situacao) VALUES
    ('Administrador', 'admin', 'admin123', 'jonathanguilhermequinot@gmail.com', 'ativo');

-- 10 lancamentos iniciais
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

-- V3__categoria.sql
-- CREATE TABLE categoria (
--    id   SERIAL PRIMARY KEY,
--    nome TEXT NOT NULL);