from unittest.mock import patch


# ── 19. Excluir: POST redireciona para index ──────────────
def test_excluir_post(client, set_session, make_conn):
    set_session(client)
    conn = make_conn()
    with patch('app.get_connection', return_value=conn):
        r = client.post('/excluir/1', follow_redirects=False)
    assert r.status_code == 302
    assert '/' in r.headers['Location']
