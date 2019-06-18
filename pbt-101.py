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
"""
Testing a List-Sorting Function
-------------------------------
In this problem, we have a bad sorting function and several tests that fail to
catch the bug in the function.

Improve the tests so that they catch the bug in the sorting function.

Also see the Python documentation for lists at:
https://docs.python.org/3/tutorial/datastructures.html
"""


def sort_a_list(lst):
    """This is a *bad* sorting function. It is meant to take a list of
    integers and return a sorted list in ascending order.
    """
    # TODO: After fixing the tests, fix this function.
    #       You may use a builtin function  OR write
    #       a sort function yourself.
    return lst[::-1]


def test_sort_a_list_basic():
    """This is a manual test. Add an assertion by-hand that catches the
    bug in the sorting function"""
    assert sort_a_list([]) == []
    assert sort_a_list([1]) == [1]
    assert sort_a_list([1, 1]) == [1, 1]
    assert sort_a_list([3, 2, 1]) == [1, 2, 3]
    # add an assertion here


@pytest.mark.parametrize(
    "lst",
    (
        [],
        [1],
        [1, 1],
        [3, 2, 1]
        # add an example case here
    ),
)
def test_sort_a_list_parametrize(lst):
    """This is a parameterized test that leverages the built-in `sorted`
    function as an 'oracle' that we can compare against.

    It asserts that a general property holds for many inputs - in fact,
    all the same inputs that we tested in the version above.

    Add the same input as above to see that it catches the same problem"""
    assert sorted(lst) == sort_a_list(lst)


@given(lst=st.lists(st.integers()))
def test_sort_a_list_hypothesis(lst):
    """This test leverages hypothesis to generate lists of integers for us.

    Add an assertion that the sorted list is indeed in the correct order."""
    # Note: Even before the assertion, we're checking that `sort_a_list`
    #       doesn't raise an exception for any list of integers! This is
    #       a form of testing in its own right!
    new = sort_a_list(list(lst))
    assert Counter(lst) == Counter(new)  # sorted list must have same elements
    # TODO: assert that the list is in correct order


"""
Takeaway
--------
This demonstrates varying degrees of manual, auto-manual, and automated testing.
Even though we were able to devise hand-crafted examples that caught the bug in
our sorting function, we would have to add many more examples by hand before we
can have any sort of real confidence that our manual tests are robust.

On the other hand, our hypothesis-driven test is generating hundreds of incisive
examples for us. This test gives us much stronger assurances about the correctness
of our sorting function.
"""

##############################################################################

"""
Testing Summation Properties
----------------------------
In this problem we want to devise the most general hypothesis search strategy that
generates lists-of-integers that satisfy the property:

    max(lst) < sum(lst)

The search strategies `st.lists()` and `st.integers()` both take arguments that will
help us restrict the values produced by our search strategy so that this property is
satisfied.

Links to relevant docs:
https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.integers
https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.lists
"""


@given(st.just([1, 2, 3]))  # update this search strategy to be more-general
def test_sum_of_list_greater_than_max(lst):
    # TODO: *without* changing the test body, write the most general
    #       argument to @given that will pass for lists of integers.
    assert max(lst) < sum(lst)


"""
Takeaway
--------
Hypothesis' search strategies are designed to provide users with fine control
over the values that are being generated. Ultimately, we can custom-tailor
search strategies which obey rich properties in order to serve our tests.
"""

##############################################################################

"""
Testing a Padding Function
--------------------------
Write a test that finds the bugs in the function `leftpad`, and then fix
the bugs.

1) Improve the hypothesis search strategy for `test_leftpad` so that
   widths other than zero are tested (up to e.g. 1000 - capped for
   performance).

2) Improve `test_leftpad`. Add assertions that certain properties are
   satisfied by the output of `leftpad`. I.e.:
   - The padded result has the correct length:
     either `width` or `len(string)`, whichever is larger.
   - The padded result ends with the input string.
   - The padded result begins with the correct padding characters.

3) Fix the `leftpad` function, using your test to guide your implementation.
"""


def leftpad(string, width, fillchar):
    """This is a *bad* function. Update the test to catch the bugs,
    and then come back to fix this.

    Parameters
    ----------
    string : str
        The input string

    width : int
        A non-negative integer specifying the minimum guaranteed
        width of the left-padded output string.

    fillchar : str
        The character (length-1 string) used to pad the string.

    Examples
    --------
    The following is the *intended* behaviour of this function:

    >>> leftpad('cat', width=5, fillchar="Z")
    'ZZcat'

    >>> leftpad('Dog', width=2, fillchar="Z")
    'Dog'
    """
    assert isinstance(width, int) and width >= 0, width
    assert isinstance(fillchar, type(u"")) and len(fillchar) == 1, fillchar
    return string  # Uh oh, we haven't padded this at all!


@given(string=st.text(), width=st.just(0), fillchar=st.characters())
def test_leftpad(string, width, fillchar):
    # TODO: allow any `width` from zero up to e.g. 1000 (capped for performance)
    padded = leftpad(string, width, fillchar)
    assert isinstance(padded, type(u"")), padded
    # TODO: Add assertions about the properties described above.
    #       Avoid using redundant code/logic between your test
    #       and the function that you are writing - they may have
    #       the same bugs!


"""
Takeaway
--------
This exercise gives us a sense for how well-written, property-based tests
can gracefully drive the process for writing code.

The combination of:
 - Using expressive hypothesis search strategies to generate
   inputs to your function.
 - Identifying and testing properties of your function that are
   incisive and discriminating.

makes for a great road-map for writing your function!
"""

##############################################################################

"""
Testing a Roundtrip Relationship
--------------------------------
In this problem we want to ensure that an instance of our custom
`Record` class can be encoded as JSON-string, and then later be
decoded without having its value changed.

Here, we behold the power of Hypothesis' recursive strategies, which
will permit us to generate examples of such records, including the
lists-of-lists-of-items, dicts-of-lists-of items, etc.


Our record can store the following values, just like JSON:
  - `None`
  - Booleans
  - finite numbers (i.e. all integers and most floats)
  - strings
  - lists of any of the aforementioned items
    - this includes, recursively, lists and dictionaries of these items
  - dictionaries that map string -> any of the aformentioned items
    - this includes, recursively, lists and dictionaries of these items

Follow these steps:
1) Add an assertion to `test_record_json_roundtrip` that checks
   if `to_json` -> `from_json` 'round-trips' properly.
   Note that this should fail because `from_json` is bad.

2) Fix the implementation of `Record.from_json`.

3) You will find that not all records are equal to themselves, because our
   input strategy allows some things that it should ban.  Skipping the test
   for non-self-equal records using `hypothesis.assume(record == record)`
   will reveal an interesting fact about list equalities!  To fix this,
   you'll therefore need to restrict the recursive strategy a little.
"""


class Record(object):
    # If you don't like writing out the special __methods__, this class
    # would be a great fit for the `attrs` package or `dataclasses`!

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Record(value={!r})".format(self.value)

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    def to_json(self):
        """Encodes `self.value` as a JSON-string"""
        return json.dumps(self.value, indent=4)

    @classmethod
    def from_json(cls, string):
        """Decodes a JSON-string back into a `Record` instance

        This is a *bad* method. This needs to be fixed
        """
        value = string
        return cls(value)


# We can define recursive strategies like so:
json_strat = st.recursive(
    st.none() | st.booleans() | st.integers() | st.floats() | st.text(),
    lambda substrat: st.lists(substrat) | st.dictionaries(st.text(), substrat),
)


# `builds` draws an example from `json_strat`, then calls `Record(value=...)`
# In this one-argument case, we could also use `json_strat.map(Record)`.
@given(st.builds(Record, value=json_strat))
def test_record_json_roundtrip(record):
    string = record.to_json()
    new = Record.from_json(string)
    # TODO: assert that the new and old records match


# Extension option: imagine that we are sending serialised records to an
# expensive network service, and would like to cache the results for records
# that we've seen before.
#    1. Write a test that for any record, calling .to_json() twice gives
#       you the same string each time.
#    2. Write a test that takes a record, converts it to json (string #1),
#       back to a new record, and finally to json again.  Are these strings
#       equal?  Would this have the same problem as test_record_json_roundtrip?


"""
Takeaway
--------
There are a few things to note here. First, a roundtrip-relationship
is a simple but powerful property to test. That being said, such a test
is useful only if it tests a sufficiently-broad and diverse set of inputs.

Constructing such inputs by-hand in this scenario would be
impermissibly-gruelling and would inevitably make for a narrow test.

Leveraging Hypothesis' recursive strategy in conjunction with a single
assertion about the roundtrip relationship makes for a very powerful test
indeed. However, this is contingent on our ability to compose strategies
to generate values that suit our needs. It pays off to develop experience
towards this end.
"""
##############################################################################
# Done early?  Check out the run-length encoding excercise at
# https://github.com/DRMacIver/hypothesis-training as a bonus!
