import datetime

from rethinkdb import r
from rethinkdb.ast import RqlTzinfo
from rethinkdb.errors import ReqlDriverCompileError
from rethinkdb.errors import RqlCompileError
from tests.common import as_db_and_table
from tests.common import assertEqual
from tests.common import assertEqUnordered
from tests.functional.common import MockTest

from rethinkdb_mock import rtime


class TestDateTimeGetters(MockTest):
    @staticmethod
    def get_data():
        data = [
            {'id': 'joe', 'last_updated': rtime.make_time(2014, 6, 3, 12, 10, 32)},
            {'id': 'sam', 'last_updated': rtime.make_time(2014, 8, 25, 17, 3, 54)}
        ]
        return as_db_and_table('d', 'people', data)

    def test_year(self, conn):
        expected = [2014, 2014]
        result = r.db('d').table('people').map(
            lambda doc: doc['last_updated'].year()
        ).run(conn)
        assertEqual(expected, list(result))

    def test_month(self, conn):
        expected = set([6, 8])
        result = r.db('d').table('people').map(
            lambda doc: doc['last_updated'].month()
        ).run(conn)
        assertEqual(expected, set(list(result)))

    def test_day(self, conn):
        expected = set([3, 25])
        result = r.db('d').table('people').map(
            lambda doc: doc['last_updated'].day()
        ).run(conn)
        assertEqual(expected, set(list(result)))

    def test_hours(self, conn):
        expected = set([12, 17])
        result = r.db('d').table('people').map(
            lambda doc: doc['last_updated'].hours()
        ).run(conn)
        assertEqual(expected, set(list(result)))

    def test_minutes(self, conn):
        expected = set([10, 3])
        result = r.db('d').table('people').map(
            lambda doc: doc['last_updated'].minutes()
        ).run(conn)
        assertEqual(expected, set(list(result)))

    def test_seconds(self, conn):
        expected = set([32, 54])
        result = r.db('d').table('people').map(
            lambda doc: doc['last_updated'].seconds()
        ).run(conn)
        assertEqual(expected, set(list(result)))

    def test_time_of_day(self, conn):
        expected = set([
            ((((12 * 60) + 10) * 60) + 32),
            ((((17 * 60) + 3) * 60) + 54)
        ])
        result = r.db('d').table('people').map(
            lambda doc: doc['last_updated'].time_of_day()
        ).run(conn)
        assertEqual(expected, set(list(result)))

    def test_day_of_week(self, conn):
        expected = set([
            1,  # 2014 August 25 -> Monday
            2   # 2014 June 3 -> Tuesday
        ])
        result = r.db('d').table('people').map(
            lambda doc: doc['last_updated'].day_of_week()
        ).run(conn)
        assertEqual(expected, set(list(result)))

    def test_date(self, conn):
        expected = set([
            datetime.datetime(2014, 8, 25, tzinfo=r.make_timezone('00:00')),
            datetime.datetime(2014, 6, 3, tzinfo=r.make_timezone('00:00'))
        ])
        result = r.db('d').table('people').map(
            lambda doc: doc['last_updated'].date()
        ).run(conn)
        assertEqual(expected, set(list(result)))


class TestMoreTime(MockTest):
    @staticmethod
    def get_data():
        data = [
            {'id': 'joe', 'last_updated': datetime.datetime(2014, 6, 3, 0, 0, 1, tzinfo=r.make_timezone('00:00'))},
            {'id': 'sam', 'last_updated': datetime.datetime(2014, 8, 25, 0, 0, 0, tzinfo=r.make_timezone('00:00'))}
        ]
        return as_db_and_table('d', 'people', data)

    def test_epoch_time(self, conn):
        results = r.db('d').table('people').map(
            lambda d: d.merge({'as_epoch': d['last_updated'].to_epoch_time()})
        ).run(conn)
        results = list(results)
        jan1 = datetime.datetime(1970, 1, 1, tzinfo=r.make_timezone('00:00'))
        for doc in results:
            expected = int((doc['last_updated'] - jan1).total_seconds())
            assertEqual(expected, doc['as_epoch'])


class TestTime(MockTest):
    @staticmethod
    def get_data():
        data = [
            {'id': 'say_anything'},
        ]
        return as_db_and_table('unimportant', 'very', data)

    def test_time_year_month_day_tz(self, conn):
        r.db('unimportant').table('very').update(
            lambda doc: doc.merge({'updated': r.time(2014, 6, 10, 'Z')})
        ).run(conn)

        result = r.db('unimportant').table('very').get('say_anything').run(conn)
        update_time = result['updated']
        assertEqual(2014, update_time.year)
        assertEqual(6, update_time.month)
        assertEqual(10, update_time.day)
        assert (isinstance(update_time.tzinfo, RqlTzinfo))

    def test_time_year_month_day_hour_minute_second_tz(self, conn):
        r.db('unimportant').table('very').update({
            'updated': r.time(2014, 6, 10, 15, 30, 45, 'Z')
        }).run(conn)

        result = r.db('unimportant').table('very').get('say_anything').run(conn)
        update_time = result['updated']
        assertEqual(2014, update_time.year)
        assertEqual(6, update_time.month)
        assertEqual(10, update_time.day)
        assertEqual(15, update_time.hour)
        assertEqual(30, update_time.minute)
        assertEqual(45, update_time.second)
        assert (isinstance(update_time.tzinfo, RqlTzinfo))

    def test_error_with_less_than_4_args(self, conn):
        try:
            r.db('unimportant').table('very').update({
                'update_time': r.time(2014, 3, 24)
            }).run(conn)
        except RqlCompileError as e:
            err = e
        assert ('expected between 4 and 7' in err.message.lower())

    def test_error_with_no_timezone(self, conn):
        date = datetime.datetime(2014, 3, 24, 12)
        try:
            r.db('unimportant').table('very').update({
                'update_time': date
            }).run(conn)
        except ReqlDriverCompileError as e:
            err = e
        assert ('datetime' in err.message.lower())
        assert ('timezone' in err.message.lower())


class TestDuring(MockTest):
    @staticmethod
    def get_data():
        data = [
            {'id': 'joe', 'last_updated': r.time(2014, 6, 3, 'Z')},
            {'id': 'sam', 'last_updated': r.time(2014, 8, 25, 'Z')}
        ]
        return as_db_and_table('d', 'people', data)

    def test_during_1(self, conn):
        expected = [
            {'id': 'joe', 'is_during': False},
            {'id': 'sam', 'is_during': True}
        ]
        result = r.db('d').table('people').map(
            lambda doc: {
                'id': doc['id'],
                'is_during': doc['last_updated'].during(r.time(2014, 7, 10, 'Z'), r.time(2014, 12, 1, 'Z'))
            }
        ).run(conn)
        assertEqUnordered(expected, list(result))

    def test_during_2(self, conn):
        expected = [
            {'id': 'joe', 'is_during': True},
            {'id': 'sam', 'is_during': False}
        ]
        result = r.db('d').table('people').map(
            lambda doc: {
                'id': doc['id'],
                'is_during': doc['last_updated'].during(
                    r.time(2014, 5, 10, 'Z'),
                    r.time(2014, 7, 1, 'Z')
                )
            }
        ).run(conn)
        assertEqUnordered(expected, list(result))

    def test_during_3(self, conn):
        expected = [
            {'id': 'joe', 'is_during': True},
            {'id': 'sam', 'is_during': False}
        ]
        result = r.db('d').table('people').map(
            lambda doc: {
                'id': doc['id'],
                'is_during': doc['last_updated'].during(
                    r.time(2014, 6, 3, 'Z'),
                    r.time(2014, 8, 25, 'Z')
                )
            }
        ).run(conn)
        assertEqUnordered(expected, list(result))

    def test_during_closed_right(self, conn):
        expected = [
            {'id': 'joe', 'is_during': True}
        ]
        result = r.db('d').table('people').map(
            lambda doc: {
                'id': doc['id'],
                'is_during': doc['last_updated'].during(
                    r.time(2014, 6, 2, 'Z'),
                    r.time(2014, 8, 25, 'Z'),
                    right_bound='closed'
                )
            }
        ).run(conn)
        assertEqUnordered(expected, list(result))

    def test_during_open_left(self, conn):
        expected = [
            {'id': 'joe', 'is_during': False},
            {'id': 'sam', 'is_during': False}
        ]
        result = r.db('d').table('people').map(
            lambda doc: {
                'id': doc['id'],
                'is_during': doc['last_updated'].during(
                    r.time(2014, 6, 3, 'Z'),
                    r.time(2014, 8, 25, 'Z'),
                    left_bound='open'
                )
            }
        ).run(conn)
        assertEqUnordered(expected, list(result))

    def test_during_open_left_closed_right(self, conn):
        expected = [
            {'id': 'joe', 'is_during': False},
            {'id': 'sam', 'is_during': True}
        ]
        result = r.db('d').table('people').map(
            lambda doc: {
                'id': doc['id'],
                'is_during': doc['last_updated'].during(
                    r.time(2014, 6, 3, 'Z'),
                    r.time(2014, 8, 25, 'Z'),
                    left_bound='open',
                    right_bound='closed'
                )
            }
        ).run(conn)
        assertEqUnordered(expected, list(result))


class TestDuring2(MockTest):
    @staticmethod
    def get_data():
        data = [
            {'id': 'joe', 'last_updated': rtime.make_time(2014, 6, 3)},
            {'id': 'sam', 'last_updated': rtime.make_time(2014, 7, 25)},
            {'id': 'bob', 'last_updated': rtime.make_time(2014, 6, 17)},
            {'id': 'sam', 'last_updated': rtime.make_time(2014, 5, 1)}
        ]
        return as_db_and_table('d', 'people', data)

    def test_filter_during(self, conn):
        table = r.db('d').table('people')
        result = table.filter(
            lambda doc: doc['last_updated'].during(
                r.time(2014, 6, 1, 'Z'),
                r.time(2014, 6, 30, 'Z')
            )
        ).run(conn)
        result = list(result)
        assertEqual(2, len(result))


class TestTimeComparison(MockTest):
    @staticmethod
    def get_data():
        data = [
            {'id': 'joe', 'last_updated': rtime.make_time(2019, 6, 2)},
            {'id': 'sam', 'last_updated': rtime.make_time(2020, 6, 3)},
            {'id': 'mia', 'last_updated': rtime.make_time(2030, 6, 3)}
        ]
        return as_db_and_table('d', 'people', data)

    def test_filter_older_than_now(self, conn):
        table = r.db('d').table('people')

        old = r.row["last_updated"] <= r.now()
        result = table.filter(old).run(conn)
        result = list(result)
        assertEqual(2, len(result))

    def test_filter_newer_than_now(self, conn):
        table = r.db('d').table('people')

        new = r.row["last_updated"] >= r.now()
        result = table.filter(new).run(conn)
        result = list(result)
        assertEqual(1, len(result))


class TestTimeCalculation(MockTest):
    @staticmethod
    def get_data():
        data = [
            {'id': 'present', 'last_updated': rtime.now()},  # Present
            {'id': 'past', 'last_updated': rtime.make_time(2020, 6, 3)},  # Past
            {'id': 'future', 'last_updated': rtime.make_time(2030, 6, 3)}  # Future
        ]
        return as_db_and_table('d', 'people', data)

    def test_subtract_seconds(self, conn):
        """
        Find entries older than 3 hours
        """
        table = r.db('d').table('people')

        three_hours = 10_800
        old = r.row["last_updated"].lt(r.now().sub(three_hours))
        result = table.filter(old).run(conn)
        result = list(result)
        assertEqual("past", result[0]['id'])

    def test_add_seconds(self, conn):
        """
        Find entries from 3 hours ago to now
        """
        table = r.db('d').table('people')

        three_hours = 10_800
        old = r.row["last_updated"].lt(r.now().add(three_hours))
        result = table.filter(old).run(conn)
        result = list(result)
        assertEqual(2, len(result))  # present and future
