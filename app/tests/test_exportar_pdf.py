from datetime import date
from unittest.mock import patch


# ── 20. Exportar PDF: retorna content-type PDF ───────────
def test_exportar_pdf(client, set_session, make_conn):
    set_session(client)
    rows = [(1, 'Teste', date(2026, 4, 12), 100.0, 'receita', 'pendente')]
    conn = make_conn(fetchall=rows)
    with patch('app.get_connection', return_value=conn):
        r = client.get('/exportar-pdf')
    assert r.status_code == 200
    assert r.content_type == 'application/pdf'
