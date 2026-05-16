from datetime import date
from unittest.mock import patch


# ── 15. Editar: GET sem sessão redireciona ────────────────
def test_editar_sem_sessao(client):
    r = client.get('/editar/1', follow_redirects=False)
    assert r.status_code == 302
    assert 'login' in r.headers['Location']


# ── 16. Editar: GET com sessão retorna 200 ───────────────
def test_editar_get(client, set_session, make_conn):
    set_session(client)
    conn = make_conn(fetchone=(1, 'Teste', date(2026, 4, 12), 100.0, 'receita', 'pendente'))
    with patch('app.get_connection', return_value=conn):
        r = client.get('/editar/1')
    assert r.status_code == 200


# ── 17. Editar: POST com dados válidos redireciona ────────
def test_editar_post_sucesso(client, set_session, make_conn):
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
def test_editar_post_campos_faltando(client, set_session, make_conn):
    set_session(client)
    conn = make_conn(fetchone=(1, 'Teste', date(2026, 4, 12), 100.0, 'receita', 'pendente'))
    with patch('app.get_connection', return_value=conn):
        r = client.post('/editar/1', data={
            'descricao': '', 'data_lancamento': '', 'valor': '', 'tipo_lancamento': ''
        })
    assert r.status_code == 200
    assert 'obrigat' in r.data.decode()
