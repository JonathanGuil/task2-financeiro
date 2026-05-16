import sys, os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config['TESTING']            = True
    flask_app.config['MAIL_SUPPRESS_SEND'] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def set_session():
    def _set(client):
        with client.session_transaction() as sess:
            sess['usuario_id']   = 1
            sess['usuario_nome'] = 'Administrador'
    return _set


@pytest.fixture
def make_conn():
    def _make(fetchone=None, fetchall=None):
        conn = MagicMock()
        cur  = MagicMock()
        cur.fetchone.return_value = fetchone
        cur.fetchall.return_value = fetchall or []
        conn.cursor.return_value  = cur
        return conn
    return _make
