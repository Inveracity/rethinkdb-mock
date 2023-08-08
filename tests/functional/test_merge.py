from rethinkdb import r
from tests.common import assertEqUnordered
from tests.functional.common import MockTest


class TestMerge(MockTest):
    @staticmethod
    def get_data():
        data = [
            {
                'id': 'id-1',
                'extra_id': 'extra-id-1',
                'x': {
                    'x-val': 'x-val-1'
                },
                'y': {
                    'y-val': 'y-val-1'
                }
            },
            {
                'id': 'id-2',
                'x': {
                    'x-val': 'x-val-2'
                },
                'y': {
                    'y-val': 'y-val-2'
                }
            }
        ]
        data2 = [
            {
                'id': 'extra-id-1',
                'extra_info': {
                    'key': 'value'
                }
            }
        ]

        return {
            'dbs': {
                'jezebel': {
                    'tables': {
                        'things': data,
                        'extra_things': data2,
                    }
                }
            }
        }

    def test_merge_toplevel(self, conn):
        expected = [
            {
                'id': 'id-1',
                'extra_id': 'extra-id-1',
                'x': {
                    'x-val': 'x-val-1'
                },
                'y': {
                    'y-val': 'y-val-1'
                },
                'z': 'Z-VALUE'
            },
            {
                'id': 'id-2',
                'x': {
                    'x-val': 'x-val-2'
                },
                'y': {
                    'y-val': 'y-val-2'
                },
                'z': 'Z-VALUE'
            }
        ]
        result = r.db('jezebel').table('things').merge({'z': 'Z-VALUE'}).run(conn)
        assertEqUnordered(expected, list(result))

    def test_merge_nested(self, conn):
        expected = [
            {
                'y-val': 'y-val-1',
                'extra-y-val': 'extra'
            },
            {
                'y-val': 'y-val-2',
                'extra-y-val': 'extra'
            }
        ]
        result = r.db('jezebel').table('things').map(
            lambda d: d['y'].merge({'extra-y-val': 'extra'})
        ).run(conn)
        assertEqUnordered(expected, list(result))

    def test_merge_nested_with_prop(self, conn):
        expected = [
            {
                'x-val': 'x-val-1',
                'y-val': 'y-val-1'
            },
            {
                'x-val': 'x-val-2',
                'y-val': 'y-val-2'
            }
        ]
        result = r.db('jezebel').table('things').map(
            lambda d: d['x'].merge(d['y'])
        ).run(conn)
        assertEqUnordered(expected, list(result))

    def test_merge_nested_with_prop2(self, conn):
        expected = [
            {
                'x-val': 'x-val-1',
                'nested': {
                    'y-val': 'y-val-1'
                }
            },
            {
                'x-val': 'x-val-2',
                'nested': {
                    'y-val': 'y-val-2'
                }
            }
        ]
        result = r.db('jezebel').table('things').map(
            lambda d: d['x'].merge({'nested': d['y']})
        ).run(conn)
        assertEqUnordered(expected, list(result))

    def test_merge_wihtout_map(self, conn):
        expected = {
            'id': 'id-1',
            'extra_id': 'extra-id-1',
            'x': {
                'x-val': 'x-val-1'
            },
            'y': {
                'y-val': 'y-val-1'
            },
            'extra': {
                'key': 'value'
            },
        }
        result = r.db('jezebel').table('things').get('id-1').merge(lambda t: {
            'extra': r.db('jezebel').table('extra_things').get(t['extra_id'])["extra_info"]
        }).run(conn)
        assertEqUnordered(expected, result)
