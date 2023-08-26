from rethinkdb import r
from tests.common import as_db_and_table
from tests.common import assertEqUnordered
from tests.functional.common import MockTest


class TestWithout(MockTest):
    @staticmethod
    def get_data():
        data = [
            {"id": "joe-id", "name": "joe", "hobby": "guitar"},
            {"id": "bob-id", "name": "bob", "hobby": "pseudointellectualism"},
            {"id": "bill-id", "name": "bill"},
            {"id": "kimye-id", "name": "kimye", "hobby": "being kimye"},
        ]
        return as_db_and_table("x", "people", data)

    def test_without_missing_attr(self, conn):
        expected = [
            {"id": "joe-id"},
            {"id": "bob-id"},
            {"id": "bill-id"},
            {"id": "kimye-id"},
        ]
        result = r.db("x").table("people").without("name", "hobby").run(conn)
        assertEqUnordered(expected, list(result))

    def test_without_missing_attr_list(self, conn):
        expected = [
            {"id": "joe-id"},
            {"id": "bob-id"},
            {"id": "bill-id"},
            {"id": "kimye-id"},
        ]
        result = r.db("x").table("people").without(["name", "hobby"]).run(conn)
        assertEqUnordered(expected, list(result))

    def test_sub_without(self, conn):
        expected = [
            {"id": "joe-id"},
            {"id": "bob-id"},
            {"id": "bill-id"},
            {"id": "kimye-id"},
        ]
        result = (
            r.db("x")
            .table("people")
            .map(lambda p: p.without("name", "hobby"))
            .run(conn)
        )
        assertEqUnordered(expected, list(result))

    def test_sub_without_list(self, conn):
        expected = [
            {"id": "joe-id"},
            {"id": "bob-id"},
            {"id": "bill-id"},
            {"id": "kimye-id"},
        ]
        result = (
            r.db("x")
            .table("people")
            .map(lambda p: p.without(["name", "hobby"]))
            .run(conn)
        )
        assertEqUnordered(expected, list(result))


class TestWithout2(MockTest):
    @staticmethod
    def get_data():
        data = [
            {
                "id": "thing-1",
                "values": {"a": "a-1", "b": "b-1", "c": "c-1", "d": "d-1"},
            },
            {
                "id": "thing-2",
                "values": {"a": "a-2", "b": "b-2", "c": "c-2", "d": "d-2"},
            },
        ]
        return as_db_and_table("some_db", "things", data)

    def test_sub_sub(self, conn):
        expected = [{"b": "b-1", "c": "c-1"}, {"b": "b-2", "c": "c-2"}]
        result = (
            r.db("some_db")
            .table("things")
            .map(lambda t: t["values"].without("a", "d"))
            .run(conn)
        )
        assertEqUnordered(expected, list(result))

    def test_sub_sub_list(self, conn):
        expected = [{"b": "b-1", "c": "c-1"}, {"b": "b-2", "c": "c-2"}]
        result = (
            r.db("some_db")
            .table("things")
            .map(lambda t: t["values"].without(["a", "d"]))
            .run(conn)
        )
        assertEqUnordered(expected, list(result))
