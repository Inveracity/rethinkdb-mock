from rethinkdb import r
from tests.common import as_db_and_table
from tests.common import assertEqual
from tests.common import assertEqUnordered
from tests.functional.common import MockTest


class TestStrings(MockTest):
    @staticmethod
    def get_data():
        data = [
            {"id": "a", "text": "something  with spaces"},
            {"id": "b", "text": "some,csv,file"},
            {"id": "c", "text": "someething"},
        ]
        return as_db_and_table("library", "texts", data)

    def test_upcase(self, conn):
        expected = set(["SOMETHING  WITH SPACES", "SOME,CSV,FILE", "SOMEETHING"])
        result = (
            r.db("library")
            .table("texts")
            .map(lambda doc: doc["text"].upcase())
            .run(conn)
        )
        assertEqual(expected, set(list(result)))

    def test_downcase(self, conn):
        expected = set(["something  with spaces", "some,csv,file", "someething"])
        result = (
            r.db("library")
            .table("texts")
            .map(lambda doc: doc["text"].downcase())
            .run(conn)
        )
        assertEqual(expected, set(list(result)))

    def test_split_1(self, conn):
        expected = [["something", "with", "spaces"], ["some,csv,file"], ["someething"]]
        result = (
            r.db("library")
            .table("texts")
            .map(lambda doc: doc["text"].split())
            .run(conn)
        )
        assertEqUnordered(expected, list(result))

    def test_split_2(self, conn):
        expected = [["something  with spaces"], ["some", "csv", "file"], ["someething"]]
        result = (
            r.db("library")
            .table("texts")
            .map(lambda doc: doc["text"].split(","))
            .run(conn)
        )
        assertEqUnordered(expected, list(result))

    def test_split_3(self, conn):
        expected = [
            ["som", "thing  with spac", "s"],
            ["som", ",csv,fil", ""],
            ["som", "", "thing"],
        ]
        result = (
            r.db("library")
            .table("texts")
            .map(lambda doc: doc["text"].split("e"))
            .run(conn)
        )
        assertEqUnordered(expected, list(result))

    def test_split_4(self, conn):
        expected = [
            ["som", "thing  with spaces"],
            ["som", ",csv,file"],
            ["som", "ething"],
        ]
        result = (
            r.db("library")
            .table("texts")
            .map(lambda doc: doc["text"].split("e", 1))
            .run(conn)
        )
        assertEqUnordered(expected, list(result))
