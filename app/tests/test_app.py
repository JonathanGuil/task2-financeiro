import pytest
from unittest.mock import patch, MagicMock
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app as flask_app

# ── fixtures ──────────────────────────────────────────────
@pytest.fixture
def client():
    flask_app.config['TESTING']            = True
    flask_app.config['MAIL_SUPPRESS_SEND'] = True
    with flask_app.test_client() as c:
        yield c

def set_session(client):
    with client.session_transaction() as sess:
        sess['usuario_id']   = 1
        sess['usuario_nome'] = 'Administrador'

def make_conn(fetchone=None, fetchall=None):
    conn = MagicMock()
    cur  = MagicMock()
    cur.fetchone.return_value  = fetchone
    cur.fetchall.return_value  = fetchall or []
    conn.cursor.return_value   = cur
    return conn

# ── 1. Login: GET carrega a página ────────────────────────
def test_login_get(client):
    r = client.get('/login')
    assert r.status_code == 200
    assert 'Login' in r.data.decode()

# ── 2. Login: POST com credenciais corretas ───────────────
def test_login_post_sucesso(client):
    conn = make_conn(fetchone=(1, 'Administrador'))
    with patch('app.get_connection', return_value=conn):
        r = client.post('/login', data={'login': 'admin', 'senha': 'admin123'},
                        follow_redirects=False)
    assert r.status_code == 302
    assert '/' in r.headers['Location']

# ── 3. Login: POST com senha errada ───────────────────────
def test_login_post_senha_errada(client):
    conn = make_conn(fetchone=None)
    with patch('app.get_connection', return_value=conn):
        r = client.post('/login', data={'login': 'admin', 'senha': 'errada'})
    assert r.status_code == 200
    assert 'incorretos' in r.data.decode()

# ── 4. Login: POST com usuário inexistente ────────────────
def test_login_post_usuario_inexistente(client):
    conn = make_conn(fetchone=None)
    with patch('app.get_connection', return_value=conn):
        r = client.post('/login', data={'login': 'naoexiste', 'senha': '123'})
    assert r.status_code == 200
    assert 'incorretos' in r.data.decode()

# ── 5. Logout: limpa sessão e redireciona ─────────────────
def test_logout(client):
    set_session(client)
    r = client.get('/logout', follow_redirects=False)
    assert r.status_code == 302
    assert 'login' in r.headers['Location']

# ── 6. Index: sem sessão redireciona para login ───────────
def test_index_sem_sessao(client):
    r = client.get('/', follow_redirects=False)
    assert r.status_code == 302
    assert 'login' in r.headers['Location']

# ── 7. Index: com sessão retorna 200 ─────────────────────
def test_index_com_sessao(client):
    set_session(client)
    conn = make_conn(fetchall=[])
    with patch('app.get_connection', return_value=conn):
        r = client.get('/')
    assert r.status_code == 200

# ── 8. Index: filtro por tipo ─────────────────────────────
def test_index_filtro_tipo(client):
    set_session(client)
    conn = make_conn(fetchall=[])
    with patch('app.get_connection', return_value=conn):
        r = client.get('/?tipo=receita')
    assert r.status_code == 200

# ── 9. Index: filtro por situação ─────────────────────────
def test_index_filtro_situacao(client):
    set_session(client)
    conn = make_conn(fetchall=[])
    with patch('app.get_connection', return_value=conn):
        r = client.get('/?situacao=pendente')
    assert r.status_code == 200

# ── 10. Index: filtro por data ────────────────────────────
def test_index_filtro_data(client):
    set_session(client)
    conn = make_conn(fetchall=[])
    with patch('app.get_connection', return_value=conn):
        r = client.get('/?data_inicio=2026-04-01&data_fim=2026-04-30')
    assert r.status_code == 200

# ── 11. Novo: GET sem sessão redireciona ──────────────────
def test_novo_sem_sessao(client):
    r = client.get('/novo', follow_redirects=False)
    assert r.status_code == 302
    assert 'login' in r.headers['Location']

# ── 12. Novo: GET com sessão retorna 200 ─────────────────
def test_novo_get(client):
    set_session(client)
    r = client.get('/novo')
    assert r.status_code == 200
    assert 'Novo' in r.data.decode()

# ── 13. Novo: POST com dados válidos redireciona ──────────
def test_novo_post_sucesso(client):
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
def test_novo_post_campos_faltando(client):
    set_session(client)
    r = client.post('/novo', data={
        'descricao': '', 'data_lancamento': '', 'valor': '', 'tipo_lancamento': ''
    })
    assert r.status_code == 200
    assert 'obrigat' in r.data.decode()

# ── 15. Editar: GET sem sessão redireciona ────────────────
def test_editar_sem_sessao(client):
    r = client.get('/editar/1', follow_redirects=False)
    assert r.status_code == 302
    assert 'login' in r.headers['Location']

# ── 16. Editar: GET com sessão retorna 200 ───────────────
def test_editar_get(client):
    set_session(client)
    from datetime import date
    conn = make_conn(fetchone=(1, 'Teste', date(2026, 4, 12), 100.0, 'receita', 'pendente'))
    with patch('app.get_connection', return_value=conn):
        r = client.get('/editar/1')
    assert r.status_code == 200

# ── 17. Editar: POST com dados válidos redireciona ────────
def test_editar_post_sucesso(client):
    set_session(client)
    conn = make_conn()
    with patch('app.get_connection', return_value=conn), \
         patch('app.enviar_email') as mock_email:
        r = client.post('/editar/1', data={
            'descricao': 'Editado', 'data_lancamento': '2026-04-12',
            'valor': '200.00', 'tipo_lancamento': 'despesa', 'situacao': 'efetivado'
        }, follow_redirects=False)
    assert r.status_code == 302
    mock_email.assert_called_once()

# ── 18. Editar: POST com campos faltando mostra erro ─────
def test_editar_post_campos_faltando(client):
    set_session(client)
    from datetime import date
    conn = make_conn(fetchone=(1, 'Teste', date(2026, 4, 12), 100.0, 'receita', 'pendente'))
    with patch('app.get_connection', return_value=conn):
        r = client.post('/editar/1', data={
            'descricao': '', 'data_lancamento': '', 'valor': '', 'tipo_lancamento': ''
        })
    assert r.status_code == 200
    assert 'obrigat' in r.data.decode()

# ── 19. Excluir: POST redireciona para index ──────────────
def test_excluir_post(client):
    set_session(client)
    conn = make_conn()
    with patch('app.get_connection', return_value=conn):
        r = client.post('/excluir/1', follow_redirects=False)
    assert r.status_code == 302
    assert '/' in r.headers['Location']

# ── 20. Exportar PDF: retorna content-type PDF ───────────
def test_exportar_pdf(client):
    set_session(client)
    from datetime import date
    rows = [(1, 'Teste', date(2026, 4, 12), 100.0, 'receita', 'pendente')]
    conn = make_conn(fetchall=rows)
    with patch('app.get_connection', return_value=conn):
        r = client.get('/exportar-pdf')
    assert r.status_code == 200
    assert r.content_type == 'application/pdf'
