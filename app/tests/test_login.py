from unittest.mock import patch


# ── 1. Login: GET carrega a página ────────────────────────
def test_login_get(client):
    r = client.get('/login')
    assert r.status_code == 200
    assert 'Login' in r.data.decode()


# ── 2. Login: POST com credenciais corretas ───────────────
def test_login_post_sucesso(client, make_conn):
    conn = make_conn(fetchone=(1, 'Administrador'))
    with patch('app.get_connection', return_value=conn):
        r = client.post('/login', data={'login': 'admin', 'senha': 'admin123'},
                        follow_redirects=False)
    assert r.status_code == 302
    assert '/' in r.headers['Location']


# ── 3. Login: POST com senha errada ───────────────────────
def test_login_post_senha_errada(client, make_conn):
    conn = make_conn(fetchone=None)
    with patch('app.get_connection', return_value=conn):
        r = client.post('/login', data={'login': 'admin', 'senha': 'errada'})
    assert r.status_code == 200
    assert 'incorretos' in r.data.decode()


# ── 4. Login: POST com usuário inexistente ────────────────
def test_login_post_usuario_inexistente(client, make_conn):
    conn = make_conn(fetchone=None)
    with patch('app.get_connection', return_value=conn):
        r = client.post('/login', data={'login': 'naoexiste', 'senha': '123'})
    assert r.status_code == 200
    assert 'incorretos' in r.data.decode()
