from unittest.mock import patch


# ── 6. Index: sem sessão redireciona para login ───────────
def test_index_sem_sessao(client):
    r = client.get('/', follow_redirects=False)
    assert r.status_code == 302
    assert 'login' in r.headers['Location']


# ── 7. Index: com sessão retorna 200 ─────────────────────
def test_index_com_sessao(client, set_session, make_conn):
    set_session(client)
    conn = make_conn(fetchall=[])
    with patch('app.get_connection', return_value=conn):
        r = client.get('/')
    assert r.status_code == 200


# ── 8. Index: filtro por tipo ─────────────────────────────
def test_index_filtro_tipo(client, set_session, make_conn):
    set_session(client)
    conn = make_conn(fetchall=[])
    with patch('app.get_connection', return_value=conn):
        r = client.get('/?tipo=receita')
    assert r.status_code == 200


# ── 9. Index: filtro por situação ─────────────────────────
def test_index_filtro_situacao(client, set_session, make_conn):
    set_session(client)
    conn = make_conn(fetchall=[])
    with patch('app.get_connection', return_value=conn):
        r = client.get('/?situacao=pendente')
    assert r.status_code == 200


# ── 10. Index: filtro por data ────────────────────────────
def test_index_filtro_data(client, set_session, make_conn):
    set_session(client)
    conn = make_conn(fetchall=[])
    with patch('app.get_connection', return_value=conn):
        r = client.get('/?data_inicio=2026-04-01&data_fim=2026-04-30')
    assert r.status_code == 200
