from pprint import pprint
import unittest
from unittest import mock

from tests.common import assertEqual

from rethinkdb_mock import util


class TestUtil(unittest.TestCase):
    def test_curry2(self):
        def fun(x, y):
            return x + y

        curried = util.curry2(fun)
        assertEqual(8, curried(5, 3))
        assertEqual(8, curried(5)(3))

    def test_curry3(self):
        def fun(x, y, z):
            return x + y + z

        curried = util.curry3(fun)
        assertEqual(15, curried(3, 5, 7))
        assertEqual(15, curried(3, 5)(7))
        assertEqual(15, curried(3)(5, 7))
        assertEqual(15, curried(3)(5)(7))

    def test_extend(self):
        dict_1 = {"x": "x1-val", "y": "y1-val"}
        dict_2 = {"x": "x2-val", "z": "z2-val"}

        extended = util.extend(dict_1, dict_2)
        assertEqual({"x": "x2-val", "y": "y1-val", "z": "z2-val"}, extended)

        assertEqual({"x": "x1-val", "y": "y1-val"}, dict_1)

        assertEqual({"x": "x2-val", "z": "z2-val"}, dict_2)

    def test_cat(self):
        list_1 = [1, 2, 3]
        list_2 = [7, 8, 9]
        result = util.cat(list_1, list_2)
        assertEqual([1, 2, 3, 7, 8, 9], result)
        assertEqual([1, 2, 3], list_1)
        assertEqual([7, 8, 9], list_2)

    def test_extend_with(self):
        with mock.patch("rethinkdb_mock.util.extend") as extend:
            extend.return_value = "EXTENDED"
            util.extend_with("X", "Y")
            util.extend_with("X")("Y")

            extend.assert_has_calls([mock.call("Y", "X"), mock.call("Y", "X")])

    def test_map_with(self):
        def add_1(x):
            return x + 1

        nums = [10, 20, 30]
        # map_fn = util.map_with(add_1)
        assertEqual([11, 21, 31], util.map_with(add_1)(nums))
        assertEqual([11, 21, 31], util.map_with(add_1, nums))

    def test_has_attrs(self):
        thing1 = {"a": "a-val", "b": "b-val"}
        thing2 = {"x": "x-val"}
        self.assertTrue(util.has_attrs(["a"], thing1))
        self.assertTrue(util.has_attrs(["a", "b"], thing1))
        self.assertFalse(util.has_attrs(["a"], thing2))
        self.assertFalse(util.has_attrs(["a", "b"], thing2))

    def test_nth(self):
        nums = [10, 20, 30, 40, 50]
        assertEqual(20, util.nth(1)(nums))
        assertEqual(40, util.nth(3)(nums))

    def test_as_obj(self):
        expected = {"x": "x-val", "y": "y-val"}
        pairs = [["x", "x-val"], ["y", "y-val"]]
        assertEqual(expected, util.as_obj(pairs))

    def test_without(self):
        obj = {"x": "x-val", "y": "y-val", "z": "z-val"}
        assertEqual({"z": "z-val"}, util.without(["x", "y"], obj))

        assertEqual({"x": "x-val", "y": "y-val"}, util.without(["z"], obj))

    def test_pluck_with(self):
        obj = {"x": "x-val", "y": "y-val", "z": "z-val"}
        assertEqual(
            {
                "x": "x-val",
            },
            util.pluck_with("x")(obj),
        )
        assertEqual(
            {
                "x": "x-val",
                "y": "y-val",
            },
            util.pluck_with(["x", "y"])(obj),
        )

    def test_pipeline(self):
        def add_5(x):
            return x + 5

        def mul_2(x):
            return x * 2

        assertEqual(24, util.pipeline(add_5, mul_2)(7))
        assertEqual(19, util.pipeline(mul_2, add_5)(7))

    def test_match_attrs_matching(self):
        to_match = {"x": "good-x", "y": "good-y"}
        good_test = {"x": "good-x", "y": "good-y", "z": "good-z"}
        self.assertTrue(util.match_attrs(to_match, good_test))

    def test_match_attrs_not_matching(self):
        to_match = {"x": "good-x", "y": "good-y"}
        bad_test = {"x": "good-x", "y": "bad-y", "z": "good-z"}
        self.assertFalse(util.match_attrs(to_match, bad_test))

    def test_match_attrs_missing_val(self):
        to_match = {"x": "good-x", "y": "good-y"}
        bad_test = {"x": "good-x", "z": "good-z"}
        self.assertFalse(util.match_attrs(to_match, bad_test))

    def test_getter_dict(self):
        a_dict = {"x": "x-val"}
        assertEqual("x-val", util.getter("x")(a_dict))
        assertEqual(None, util.getter("y")(a_dict))

    def test_getter_obj(self):
        class Thing(object):
            def __init__(self, a_dict):
                for k, v in list(a_dict.items()):
                    setattr(self, k, v)

        thing = Thing({"x": "x-val"})

        assertEqual("x-val", util.getter("x")(thing))
        assertEqual(None, util.getter("y")(thing))

    def test_maybe_map_simple(self):
        def add_5(x):
            return x + 5

        assertEqual(13, util.maybe_map(add_5, 8))
        assertEqual([5, 10, 15], util.maybe_map(add_5, [0, 5, 10]))

    def test_maybe_map_dict(self):
        def set_y_by_x(thing):
            return {"x": thing["x"], "y": thing["x"] + 1}

        assertEqual({"x": 5, "y": 6}, util.maybe_map(set_y_by_x, {"x": 5}))
        assertEqual(
            [{"x": 5, "y": 6}, {"x": 10, "y": 11}],
            util.maybe_map(set_y_by_x, [{"x": 5}, {"x": 10}]),
        )

    def test_splice(self):
        nums = [1, 2, 3, 4]
        result = util.splice_at([10, 20], 2, nums)
        assertEqual([1, 2, 10, 20, 3, 4], result)

    def test_insert(self):
        nums = [1, 2, 3, 4]
        result = util.insert_at(10, 2, nums)
        assertEqual([1, 2, 10, 3, 4], result)

    def test_change_at(self):
        nums = [1, 2, 3, 4]
        assertEqual([1, 10, 3, 4], util.change_at(10, 1, nums))

    def test_sort_by_one(self):
        people = [
            {"id": "joe", "age": 26, "score": 60},
            {"id": "todd", "age": 52, "score": 15},
            {"id": "bill", "age": 35, "score": 78},
        ]
        expected = [
            {"id": "joe", "age": 26, "score": 60},
            {"id": "bill", "age": 35, "score": 78},
            {"id": "todd", "age": 52, "score": 15},
        ]
        result = util.sort_by_one("age", people)
        for index in range(0, len(expected)):
            assertEqual(expected[index], result[index])

    def test_sort_by_many_1(self):
        people = [
            {"id": "joe", "age": 26, "score": 60},
            {"id": "todd", "age": 52, "score": 15},
            {"id": "bill", "age": 35, "score": 78},
        ]
        expected = [
            {"id": "joe", "age": 26, "score": 60},
            {"id": "bill", "age": 35, "score": 78},
            {"id": "todd", "age": 52, "score": 15},
        ]
        result = util.sort_by_many([("age", "ASC")], people)
        for index in range(0, len(expected)):
            assertEqual(expected[index], result[index])

    def test_sort_by_many_2(self):
        people = [
            {"id": "joe", "age": 26, "score": 60},
            {"id": "todd", "age": 52, "score": 15},
            {"id": "joe", "age": 26, "score": 20},
            {"id": "bill", "age": 35, "score": 78},
            {"id": "todd", "age": 52, "score": 80},
        ]
        expected = [
            {"id": "joe", "age": 26, "score": 20},
            {"id": "joe", "age": 26, "score": 60},
            {"id": "bill", "age": 35, "score": 78},
            {"id": "todd", "age": 52, "score": 15},
            {"id": "todd", "age": 52, "score": 80},
        ]
        result = util.sort_by_many([("age", "ASC"), ("score", "ASC")], people)
        pprint({"RESULT": result})
        for index in range(0, len(expected)):
            assertEqual(expected[index], result[index])

    def test_sort_by_many_3(self):
        people = [
            {"id": "joe", "age": 26, "score": 60},
            {"id": "todd", "age": 52, "score": 15},
            {"id": "joe", "age": 26, "score": 20},
            {"id": "bill", "age": 35, "score": 78},
            {"id": "todd", "age": 52, "score": 80},
        ]
        expected = [
            {"id": "joe", "age": 26, "score": 60},
            {"id": "joe", "age": 26, "score": 20},
            {"id": "bill", "age": 35, "score": 78},
            {"id": "todd", "age": 52, "score": 80},
            {"id": "todd", "age": 52, "score": 15},
        ]
        result = util.sort_by_many([("age", "ASC"), ("score", "DESC")], people)
        pprint({"RESULT": result})
        for index in range(0, len(expected)):
            assertEqual(expected[index], result[index])

    def test_min_mapped(self):
        sequence = [
            {"val": 5},
            {"val": 10},
            {"val": 17},
            {"val": 2},
            {"val": 28},
            {"val": 8},
        ]

        def get_val(doc):
            return doc["val"]

        assertEqual({"val": 2}, util.min_mapped(get_val, sequence))

    def test_max_mapped(self):
        sequence = [
            {"val": 5},
            {"val": 10},
            {"val": 17},
            {"val": 2},
            {"val": 28},
            {"val": 8},
        ]

        def get_val(doc):
            return doc["val"]

        assertEqual({"val": 28}, util.max_mapped(get_val, sequence))

    def test_deep_extend_pair(self):
        obj = {"x": {"x1": {"v1": 5, "v2": 7}, "nums": [1, 3, 5]}, "a_list": [10, 20]}
        ext_with = {
            "x": {
                "x2": {"x2-key": "x2-val"},
                "x1": {"v2": "new-v2-val", "v3": "v3-val"},
                "nums": [7, 9],
            },
            "a_list": "new-a-list-val",
        }
        expected = {
            "x": {
                "x2": {"x2-key": "x2-val"},
                "x1": {"v1": 5, "v2": "new-v2-val", "v3": "v3-val"},
                "nums": [1, 3, 5, 7, 9],
            },
            "a_list": "new-a-list-val",
        }
        result = util.deep_extend_pair(obj, ext_with)
        assertEqual(expected, result)


class TestDictableSet(unittest.TestCase):
    def test_simple(self):
        x = {"x": 10}
        foo = util.DictableSet([x])
        self.assertTrue(foo.has(x))
        y = {"y": 15}
        self.assertFalse(foo.has(y))

    def test_reordered_vals(self):
        def get_doc():
            return {"x": [5, 10]}

        foo = util.DictableSet([get_doc()])
        self.assertTrue(foo.has(get_doc()))
        self.assertTrue(foo.has({"x": [10, 5]}))
