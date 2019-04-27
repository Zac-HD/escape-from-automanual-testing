""" (this file is problem set one of three)


INSTRUCTIONS
============

Clone this repository, and `pip install pytest hypothesis`.
Then run `pytest pbt-101.py`.  You should see nine passing tests.
(see README.md for more details on installation)


There are four exercises in this file.  For each (and I suggest in order):

1. Fix the test, so that it detects the "bug".
2. Run the tests with `pytest pbt-101.py` - if they don't fail, go to step 1.
3. Fix the code, and run the tests again to confirm that it's working.

Good luck, and enjoy!
"""

import json
from collections import Counter

import pytest

from hypothesis import given, strategies as st


##############################################################################


def sort_a_list(lst):
    # TODO: sort the list however you wish (use a builtin OR write a sort func)
    # Consider writing the test first so you see it fail!
    return lst[::-1]


def test_sort_a_list_basic():
    # Assertions with hand-picked examples.
    assert sort_a_list([]) == []
    assert sort_a_list([1]) == [1]
    assert sort_a_list([1, 1]) == [1, 1]
    assert sort_a_list([3, 2, 1]) == [1, 2, 3]


@pytest.mark.parametrize("lst", ([], [1], [1, 1], [3, 2, 1]))
def test_sort_a_list_parametrize(lst):
    # Assert a general property on many inputs.
    # (we'll discuss this specific pattern more later)
    assert sorted(lst) == sort_a_list(lst)


@given(lst=st.lists(st.integers()))
def test_sort_a_list(lst):
    # Note: even before the assertion, we're checking that sort_a_list
    #  doesn't raise an exception for any list of integers!
    new = sort_a_list(lst.copy())
    assert Counter(lst) == Counter(new)  # sorted list must have same elements
    # TODO: assert that the list is in correct order


##############################################################################


@given(st.just([1, 2, 3]))  # lists of integers with the following constraint:
def test_sum_of_list_greater_than_max(lst):
    # TODO: *without* changing the test body, write the most general
    #       argument to @given that will pass for lists of integers.
    # hint: both lists() and integers() take arguments that will help.
    #       See https://hypothesis.readthedocs.io/en/latest/data.html
    assert max(lst) < sum(lst)


##############################################################################


def leftpad(string, width, fillchar):
    # TODO: if len(string) < width, add fillchar to the left until it isn't.
    # Bonus points for finding a trivial or pythonic solution.
    return string


@given(st.text(), st.just(0), st.characters())
def test_leftpad(string, width, fillchar):
    # TODO: allow any length from zero up to e.g. 1000 (capped for performance)
    padded = leftpad(string, width, fillchar)
    assert len(padded) == max(width, len(string))
    assert padded.endswith(string)
    # TODO: assert that correct padding has been added
    # (the trick is to write code and tests which will have different bugs)


##############################################################################


class Record(object):
    # Consider using the `attrs` package (attrs.org) or dataclasses instead.

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Record(value={!r})".format(self.value)

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    def to_json(self):
        return json.dumps(self.value, indent=4, sort_keys=True)

    @classmethod
    def from_json(cls, string):
        value = string
        return cls(value)


# We can define recursive strategies like so:
json_strat = st.recursive(
    # JSON values are defined as nil, false, true, number, string, ...
    st.none() | st.booleans() | st.floats() | st.text(),
    # or arrays of json, or "objects" ie string: json dictionaries.
    lambda substrat: st.lists(substrat) | st.dictionaries(st.text(), substrat),
)


# `builds` draws an example from `json_strat`, then calls `Record(value=...)`
# In this one-argument case, we could also use `json_strat.map(Record)`.
@given(st.builds(Record, value=json_strat))
def test_record_json_roundtrip(record):
    string = record.to_json()
    new = Record.from_json(string)
    # assert record == new
    # TODO: fix the first problem in the code being tested
    # TODO: fix the second problem by using hypothesis.assume in the test,
    #       or an argument to one of the strategies defining json


##############################################################################
# Done early?  Check out the run-length encoding excercise at
# https://github.com/DRMacIver/hypothesis-training as a bonus!
