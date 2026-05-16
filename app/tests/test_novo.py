from unittest.mock import patch


# ── 11. Novo: GET sem sessão redireciona ──────────────────
def test_novo_sem_sessao(client):
    r = client.get('/novo', follow_redirects=False)
    assert r.status_code == 302
    assert 'login' in r.headers['Location']


# ── 12. Novo: GET com sessão retorna 200 ─────────────────
def test_novo_get(client, set_session):
    set_session(client)
    r = client.get('/novo')
    assert r.status_code == 200
    assert 'Novo' in r.data.decode()


# ── 13. Novo: POST com dados válidos redireciona ──────────
def test_novo_post_sucesso(client, set_session, make_conn):
    set_session(client)
    conn = make_conn()
    with patch('app.get_connection', return_value=conn), \
         patch('app.enviar_email') as mock_email:
        r = client.post('/novo', data={
            'descricao': 'Teste', 'data_lancamento': '2026-04-12',
            'valor': '100.00', 'tipo_lancamento': 'receita', 'situacao': 'pendente'
        }, follow_redirects=False)
    assert r.status_code == 302
    assert '/' in r.headers['Location']
    mock_email.assert_called_once()


# ── 14. Novo: POST com campos faltando mostra erro ────────
def test_novo_post_campos_faltando(client, set_session):
    set_session(client)
    r = client.post('/novo', data={
        'descricao': '', 'data_lancamento': '', 'valor': '', 'tipo_lancamento': ''
    })
    assert r.status_code == 200
    assert 'obrigat' in r.data.decode()
