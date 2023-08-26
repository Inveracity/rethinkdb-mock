# MIT License

# Copyright (c) 2016 Man AHL

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

################################################################################
# The following code is taken from https://github.com/man-group/pytest-plugins #
# and adapted to be compatible with Rethinkdb Python Client 2.4.8              #
################################################################################

import logging
import uuid

import pytest
from pytest_fixture_config import requires_config
from pytest_server_fixtures import CONFIG
from pytest_server_fixtures.base2 import TestServerV2

log = logging.getLogger(__name__)
rethinkdb = None


def _rethink_server(request):
    """This does the actual work - there are several versions of this used
    with different scopes.
    """
    test_server = RethinkDBServer()
    request.addfinalizer(lambda p=test_server: p.teardown())
    test_server.start()
    return test_server


@pytest.fixture(scope="function")
@requires_config(CONFIG, ["rethink_executable"])
def rethink_server(request):
    """Function-scoped RethinkDB server in a local thread.

    Attributes
    ----------
    conn: (``rethinkdb.Connection``)  Connection to this server instance
    .. also inherits all attributes from the `workspace` fixture

    """
    return _rethink_server(request)


@pytest.fixture(scope="session")
@requires_config(CONFIG, ["rethink_executable"])
def rethink_server_sess(request):
    """Same as rethink_server fixture, scoped as session instead."""
    return _rethink_server(request)


@pytest.fixture(scope="function")
def rethink_unique_db(rethink_server_sess):
    """Starts up a session-scoped server, and returns a connection to
    a unique database for the life of a single test, and drops it after
    """
    dbid = uuid.uuid4().hex
    conn = rethink_server_sess.conn
    r.db_create(dbid).run(conn)
    conn.use(dbid)
    yield conn
    r.db_drop(dbid).run(conn)


@pytest.fixture(scope="module")
def rethink_module_db(rethink_server_sess):
    """Starts up a module-scoped server, and returns a connection to
    a unique database for all the tests in one module.
    Drops the database after module tests are complete.
    """
    dbid = uuid.uuid4().hex
    conn = rethink_server_sess.conn
    log.info("Making database")
    r.db_create(dbid).run(conn)
    conn.use(dbid)
    yield conn
    log.info("Dropping database")
    r.db_drop(dbid).run(conn)


@pytest.fixture(scope="module")
def rethink_make_tables(request, rethink_module_db):
    """Module-scoped fixture that creates all tables specified in the test
    module attribute FIXTURE_TABLES.

    """
    reqd_table_list = getattr(request.module, "FIXTURE_TABLES")
    log.debug("Do stuff before all module tests with {0}".format(reqd_table_list))
    conn = rethink_module_db
    for table_name, primary_key in reqd_table_list:
        try:
            r.db(conn.db).table_create(
                table_name,
                primary_key=primary_key,
            ).run(conn)
            log.info('Made table "{0}" with key "{1}"'.format(table_name, primary_key))
        except rethinkdb.errors.RqlRuntimeError as err:
            log.debug('Table "{0}" not made: {1}'.format(table_name, err.message))


@pytest.fixture(scope="function")
def rethink_empty_db(request, rethink_module_db, rethink_make_tables):
    """Function-scoped fixture that will empty all the tables defined
    for the `rethink_make_tables` fixture.

    This is a useful approach, because of the long time taken to
    create a new RethinkDB table, compared to the time to empty one.
    """
    tables_to_emptied = (
        table[0] for table in getattr(request.module, "FIXTURE_TABLES")
    )
    conn = rethink_module_db

    for table_name in tables_to_emptied:
        rethinkdb.db(conn.db).table(table_name).delete().run(conn)
        log.debug('Emptied "{0}" before test'.format(table_name))
    yield conn


class RethinkDBServer(TestServerV2):
    random_hostname = False

    def __init__(self, **kwargs):
        # defer loading of rethinkdb
        global r
        global rethinkdb
        import rethinkdb
        from rethinkdb import r

        super(RethinkDBServer, self).__init__(**kwargs)
        self._driver_port = self._get_port(28015)
        self._cluster_port = self._get_port(29015)
        self._http_port = self._get_port(8080)
        self.db = None

    @property
    def cmd(self):
        return "rethinkdb"

    @property
    def cmd_local(self):
        return CONFIG.rethink_executable

    def get_args(self, **kwargs):
        cmd = [
            "--bind",
            self._listen_hostname,
            "--driver-port",
            str(self.port),
            "--http-port",
            str(self.http_port),
            "--cluster-port",
            str(self.cluster_port),
        ]

        if "workspace" in kwargs:
            cmd += ["--directory", str(kwargs["workspace"] / "db")]

        return cmd

    @property
    def image(self):
        return CONFIG.rethink_image

    @property
    def port(self):
        return self._driver_port

    @property
    def cluster_port(self):
        return self._cluster_port

    @property
    def http_port(self):
        return self._http_port

    def check_server_up(self):
        """Test connection to the server."""
        log.info("Connecting to RethinkDB at {0}:{1}".format(self.hostname, self.port))

        if not self.hostname:
            return False

        try:
            self.conn = r.connect(host=self.hostname, port=self.port, db="test")
            return True
        except rethinkdb.errors.RqlDriverError as err:
            log.warning(err)
        return False
