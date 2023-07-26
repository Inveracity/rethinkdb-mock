![build](https://github.com/Inveracity/rethinkdb-mock/workflows/build/badge.svg?branch=master)
![rethinkdb](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Inveracity/ee29dbdeafff4549e9a7fb0ad114358c/raw/a4f809e51f9c269af81490c03a7c88a38764b8f3/rethinkdb-python)
[![PyPI version](https://badge.fury.io/py/rethinkdb-mock.svg)](https://pypi.org/project/rethinkdb-mock/)

# RethinkDB Mock

Formerly known as [MockThink](https://github.com/scivey/mockthink) by Scivey, this is a continuation of that work released under a new name.

Rethinkdb-mock is an in-process Python clone of RethinkDB's API. For testing.

MockThink provides a stub connection object which can be passed to normal ReQL queries. Instead of being serialized and sent to the server, the ReQL AST is run through an interpreter in the same process. "Tables" and "databases" are based on data given to the MockThink constructor.

Avoiding network calls (for tests themselves as well as setup/teardown) makes testing queries with MockThink orders of magnitude faster.

# Install

```sh
pip install rethinkdb-mock
# or
pipenv install --dev rethinkdb-mock
```

## Usage

### Basic

```python
    from pprint import pprint
    from rethinkdb_mock import MockThink
    import rethinkdb as r

    db = MockThink({
        'dbs': {
            'tara': {
                'tables': {
                    'people': [
                        {'id': 'john-id', 'name': 'John'},
                        {'id': 'sam-id', 'name': 'Sam'}
                    ]
                }
            }
        }
    })

    with db.connect() as conn:
        result = r.db('tara').table('people').map(
            lambda doc: doc.merge({'also_name': doc['name']})
        ).run(conn)
        pprint(list(result))

        # [
        #    {'also_name': 'John', 'id': 'john-id', 'name': 'John'},
        #    {'also_name': 'Sam', 'id': 'sam-id', 'name': 'Sam'}
        # ]

        r.db('tara').table('people').update(
            {'likes_fonz': True}
        ).run(conn)

        result = r.db('tara').table('people').run(conn)
        pprint(list(result))

        # [
        #    {'id': 'john-id', 'likes_fonz': True, 'name': 'John'},
        #    {'id': 'sam-id', 'likes_fonz': True, 'name': 'Sam'}
        # ]

    # data is reset at exit of context manager above

    with db.connect() as conn:
        result = r.db('tara').table('people').run(conn)
        pprint(list(result))
        # [
        #    {'id': 'john-id', 'name': 'John'},
        #    {'id': 'sam-id', 'name': 'Sam'}
        # ]
```

### Set the default database for the connection

> Like `r.connect(db='database')`

```python
    from pprint import pprint
    from rethinkdb_mock import MockThink
    import rethinkdb as r

    db = MockThink({
        'dbs': {
            'tara': {
                'tables': {
                    'people': [
                        {'id': 'john-id', 'first_name': 'John', 'last_name': 'Generic'},
                        {'id': 'sam-id', 'first_name': 'Sam', 'last_name': 'Dull'},
                        {'id': 'adam-id', 'first_name': 'Adam', 'last_name': 'Average'}
                    ]
                }
            }
        }
        'default': 'tara'
    })

    with db.connect() as conn:

        r.db('tara').table('people').index_create(
            'full_name',
            lambda doc: doc['last_name'] + doc['first_name']
        ).run(conn)

        r.table('people').index_wait().run(conn)

        result = r..table('people').get_all(
            'GenericJohn', 'AverageAdam', index='full_name'
        ).run(conn)
        pprint(list(result))
        # {'id': 'john-id', 'first_name': 'John', 'last_name': 'Generic'},
        # {'id': 'adam-id', 'first_name': 'Adam', 'last_name': 'Average'}
```

### Full support for secondary indexes

```python
    from pprint import pprint
    from rethinkdb_mock import MockThink
    import rethinkdb as r

    db = MockThink({
        'dbs': {
            'tara': {
                'tables': {
                    'people': [
                        {'id': 'john-id', 'first_name': 'John', 'last_name': 'Generic'},
                        {'id': 'sam-id', 'first_name': 'Sam', 'last_name': 'Dull'},
                        {'id': 'adam-id', 'first_name': 'Adam', 'last_name': 'Average'}
                    ]
                }
            }
        }
    })

    with db.connect() as conn:

        r.db('tara').table('people').index_create(
            'full_name',
            lambda doc: doc['last_name'] + doc['first_name']
        ).run(conn)

        r.db('tara').table('people').index_wait().run(conn)

        result = r.db('tara').table('people').get_all(
            'GenericJohn', 'AverageAdam', index='full_name'
        ).run(conn)
        pprint(list(result))
        # {'id': 'john-id', 'first_name': 'John', 'last_name': 'Generic'},
        # {'id': 'adam-id', 'first_name': 'Adam', 'last_name': 'Average'}

```

## Testing

The most confusing test failures are those caused by errors in test frameworks and harnesses themselves.
This means they need to be tested very thoroughly.

The main testing is a [suite of functional tests](https://github.com/scivey/rethinkdb_mock/tree/master/rethinkdb_mock/test/functional) which are targeted at the individual query level,
e.g. [testing all the ways in which `r.merge` might be called](https://github.com/scivey/rethinkdb_mock/blob/master/rethinkdb_mock/test/functional/test_merge.py).

These are all complete ReQL queries, but avoid complexity beyond the target query to make failures easier to diagnose.

The [integration tests](https://github.com/scivey/rethinkdb_mock/blob/master/rethinkdb_mock/test/integration/__init__.py) cover more complicated queries, e.g. `eq_join`->`map`->`eq_join`->`map`.

Both the functional and integration tests have two modes of execution, `rethinkdb_mock` and `rethink`. The second mode runs the same tests against a running RethinkDB instance, and is much slower due to the network calls. `rethinkdb_mock` mode is for testing MockThink's behavior against our expectations; `rethink` mode is for testing our expectations against reality.

### Run tests

```bash
# Install dependencies
pip install pipenv
pipenv sync --dev

# Run the unit tests
pipenv run test
```

### Run tests against a live server

The docker folder contains a dockerfile that grabs rethinkdb and runs the python tests

Simply running the below command outputs the results

```bash
docker-compose up --build
```

## Code formatting

The `tox.ini` file contains the configuration for code formatting

```bash
# Install dependencies
pip install pipenv
pipenv sync --dev

# Format imports
pipenv run isort

# Check styling with Flake8
pipenv run lint
```

## License

[The MIT License (MIT)](LICENSE)
