from rethinkdb import r
from tests.common import as_db_and_table
from tests.common import assertEqual
from tests.functional.common import MockTest


class TestContains(MockTest):
    @staticmethod
    def get_data():
        data = [
            {"id": "bob-id", "age": 32, "nums": [5, 7]},
            {"id": "sam-id", "age": 45},
            {"id": "joe-id", "age": 36},
        ]
        return as_db_and_table("d", "people", data)

    def test_contains_table_dict_true(self, conn):
        result = (
            r.db("d").table("people").contains({"id": "sam-id", "age": 45}).run(conn)
        )
        assertEqual(True, result)

    def test_contains_table_dict_multi_true(self, conn):
        result = (
            r.db("d")
            .table("people")
            .contains({"id": "sam-id", "age": 45}, {"id": "joe-id", "age": 36})
            .run(conn)
        )
        assertEqual(True, result)

    def test_contains_table_dict_false(self, conn):
        result = (
            r.db("d")
            .table("people")
            .contains({"id": "tara-muse-id", "age": "timeless"})
            .run(conn)
        )
        assertEqual(False, result)

    def test_contains_table_dict_multi_false(self, conn):
        result = (
            r.db("d")
            .table("people")
            .contains(
                {"id": "sam-id", "age": 45}, {"id": "tara-muse-id", "age": "timeless"}
            )
            .run(conn)
        )
        assertEqual(False, result)

    def test_contains_table_pred_true(self, conn):
        result = (
            r.db("d")
            .table("people")
            .contains(lambda doc: doc["id"] == "sam-id")
            .run(conn)
        )
        assertEqual(True, result)

    def test_contains_table_pred_multi_true(self, conn):
        result = (
            r.db("d")
            .table("people")
            .contains(
                lambda doc: doc["id"] == "sam-id", lambda doc: doc["id"] == "joe-id"
            )
            .run(conn)
        )
        assertEqual(True, result)

    def test_contains_table_pred_false(self, conn):
        result = (
            r.db("d")
            .table("people")
            .contains(lambda doc: doc["id"] == "tara-muse-id")
            .run(conn)
        )
        assertEqual(False, result)

    def test_contains_table_pred_multi_false(self, conn):
        result = (
            r.db("d")
            .table("people")
            .contains(
                lambda doc: doc["id"] == "sam-id",
                lambda doc: doc["id"] == "tara-muse-id",
            )
            .run(conn)
        )
        assertEqual(False, result)

    def test_contains_lambda(self, conn):
        expected = [
            {"id": "bob-id", "age": 32, "nums": [5, 7]},
            {"id": "sam-id", "age": 45},
        ]
        result = (
            r.db("d")
            .table("people")
            .filter(
                lambda doc: r.expr(["non_existent", "sam-id", "bob-id"]).contains(
                    doc["id"]
                )
            )
            .run(conn)
        )
        assertEqual(expected, list(result))
