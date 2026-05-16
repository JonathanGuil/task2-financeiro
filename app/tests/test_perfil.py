from unittest.mock import patch


# ── Perfil: POST sem sessão redireciona para login ────────
def test_perfil_sem_sessao(client):
    r = client.post('/perfil', data={'email': 'novo@exemplo.com'},
                     follow_redirects=False)
    assert r.status_code == 302
    assert 'login' in r.headers['Location']


# ── Perfil: POST com email atualiza e redireciona ─────────
def test_perfil_post_sucesso(client, set_session, make_conn):
    set_session(client)
    conn = make_conn()
    with patch('app.get_connection', return_value=conn):
        r = client.post('/perfil', data={'email': 'novo@exemplo.com'},
                        follow_redirects=False)
    assert r.status_code == 302
    assert '/' in r.headers['Location']
