# ── 5. Logout: limpa sessão e redireciona ─────────────────
def test_logout(client, set_session):
    set_session(client)
    r = client.get('/logout', follow_redirects=False)
    assert r.status_code == 302
    assert 'login' in r.headers['Location']
