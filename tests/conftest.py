import logging

import pytest
from pytest_server_fixtures.rethink import _rethink_server
import rethinkdb
from tests.common import as_db_and_table
from tests.common import load_stock_data

from rethinkdb_mock import MockThink

logging.basicConfig()


def pytest_addoption(parser):
    group = parser.getgroup("rethinkdb_mock", "Mockthink Testing")
    group._addoption(
        "--run",
        dest="conn_type",
        default="rethinkdb_mock",
        action="store",
        choices=["rethinkdb_mock", "rethink"],
        help="Select whether tests are run on a rethinkdb_mock connection or rethink connection or both")


@pytest.fixture(scope="session")
def conn_sess(request):
    cfg = request.config
    conn_type = cfg.getvalue("conn_type")
    if conn_type == "rethink":
        try:
            server = _rethink_server(request)
            conn = server.conn
        except rethinkdb.errors.ReqlDriverError:
            pytest.exit("Unable to connect to rethink")
        except OSError:
            pytest.exit("No rethinkdb binary found")
    elif conn_type == "rethinkdb_mock":
        conn = MockThink(as_db_and_table('nothing', 'nothing', [])).get_conn()
    else:
        pytest.exit(f"Unknown rethinkdb_mock test connection type: {conn_type}")
    return conn


@pytest.fixture(scope="function")
def conn(request, conn_sess):
    data = request.instance.get_data()
    load_stock_data(data, conn_sess)
    return conn_sess
