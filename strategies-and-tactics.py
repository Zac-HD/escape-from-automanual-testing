""" (this file is problem set two of three)


This file contains problems that are designed to expose you to the
`hypothesis.strategies` API and a variety of techniques for composing
or adjusting strategies for your tests.

Key link:  https://hypothesis.readthedocs.io/en/latest/data.html


"""

import json

import pytest

import hypothesis
from hypothesis import given, settings, strategies as st


##############################################################################
# Practicing with the `.map(...)` method

# Remove the mark.xfail decorator,
# then add a .map(...) to the strategy that makes the test pass.
# You'll need to change the value, then the type.


@pytest.mark.xfail
@given(st.integers())
def test_map_even_numbers(x):
    assert x[-1] in "02468"


@pytest.mark.xfail
@given(st.integers())
def test_map_odd_numbers(x):
    assert x[-1] in "13579"


##############################################################################
# Practicing with the `.filter(...)` method
# Same tasks as above, without using map or transforming the value!


@pytest.mark.xfail
@given(st.integers())
def test_map_even_numbers(x):
    assert str(x)[-1] in "02468"


@pytest.mark.xfail
@given(st.integers())
def test_map_odd_numbers(x):
    assert str(x)[-1] in "13579"


##############################################################################
# Defining recursive data.

# There are a couple of ways to define recursive data with Hypothesis,
# leaning on the fact that strategies are lazily instantiated.
# In the last block of exercises, you saw the `st.recursive` function...
# if not, go finish that and then come back!
#
# `st.recursive` takes a base strategy, and a function that takes a strategy
# and returns an extended strategy.  All good if we want that structure!
# If you want mutual recursion though, or have a complicated kind of data
# (or just limited time in a tutorial), `st.deferred` is the way to go.
#
# The `Record` exercise in pbt-101.py defined JSON using `st.recursive`,
# if you want to compare them, and has some extension problems that you
# could write as tests here instead.

json_strat = st.deferred(
    lambda: st.one_of(
        # JSON values are defined as one of null, false, true, a finite number,
        # a string, an array of json values, or a dict of string to json values.
        st.none(),
        st.booleans(),
        # TODO: Write out the rest of this definition in Hypothesis strategies!
    )
)
# If in doubt, you can copy-paste the definition of json_strat to an interactive
# prompt, and use the `.example()` method of the strategy to see what kind of
# data it generates.  Be warned though!  The distribution of `.example()`s is
# skewed towards simple options, and it should only ever be used interactively.


# You can use `@settings(verbosity=hypothesis.Verbosity.verbose)` (or `debug`)
# to see what's going on, or get a summary with the `hypothesis.event(message)`
# function and `pytest --hypothesis-show-statistics ...`
@given(json_strat)
def test_json_dumps(value):
    """Checks that value is serialisable as JSON."""
    # We expect this test to always pass - the point of this excercise is
    # to define a recursive strategy, and then investigate the values it
    # generates for a *passing* test.
    hypothesis.note("value={}".format(value))
    hypothesis.event("type: {}".format(type(value)))
    json.dumps(value)


##############################################################################
# `@st.composite` exercise

# This goal of this exercise is to play with a contrived data dependency,
# using a composite strategy to generate inputs.  You can use the same tricks
# as above to check what's being generated, so try to keep the test passing!


@st.composite
def a_composite_strategy(draw):
    """Generates a (List[int], index) pair.  The index points to a random positive
    element (>= 1); if there are no positive elements index is None.
    """
    # TODO: draw a list, determine the allowed indices, and choose one to return
    lst = []  # TODO: draw a list of integers here
    index = None
    # TODO: determine the list of allowed indices, and choose one if non-empty
    return (lst, index)


@given(a_composite_strategy())
def test_a_composite_strategy(value):
    # Why generate a tuple with a `@composite` strategy instead of using two
    # separate strategies?  This way we can ensure certain relationships between
    # the `lst` and `index` values!  (You can get a similar effect with st.data(),
    # but the reporting and reproducibility isn't as nice.)
    lst, index = value
    assert all(isinstance(n, int) for n in lst)
    if index is None:
        assert all(n < 1 for n in lst)
    else:
        assert lst[index] >= 1


##############################################################################
# Simplified json-schema inference

# Note: you are not expected to finish this optional extension!

# One really useful pattern for complex data is to infer a strategy from an
# existing schema of some kind.  For example, Hypothesis ships with functions
# for inference from types, regular expressions, Numpy dtypes, etc.
#
# This exercise is to write a function that, given a simple "json-schema",
# returns a strategy for objects that will match that schema (details below).
#
# We'll use a simplified subset of the specification today, but there is a
# real-world version here:  https://pypi.org/project/hypothesis-jsonschema/
#
# Final tip: I suggest starting by adding any tests, then improving the
# schema_strategy and check_schema functions, *then* strengthening the
# validate and from_schema functions.  You might be surprised!


SCHEMA_TYPES = ("null", "bool", "number", "string", "array")


def check_schema(schema):
    """A helper function to check whether something is a valid schema."""
    # Much simpler than the real spec - every schema must have a type,
    # only one numeric type, and no objects.
    assert isinstance(schema, dict)
    type_ = schema.get("type")
    assert type_ in SCHEMA_TYPES, schema
    if type_ in ("null", "bool"):
        assert len(schema) == 1  # No other keys allowed
    # TODO: number: check maximum and minimum, no other keys
    elif type_ == "string":
        assert set(schema).issubset("type minLength maxLength".split())
        # TODO: check the values of maxLength and minLength are positive
        # and correctly ordered - *if* the keys are present at all!
    # TODO: array: check maxLength and minLength, items schema, no other keys
    #       (bonus round: support uniqueItems for arrays with JSON round-trip)


def validate(schema, instance):
    """Return True if `instance` matches `schema`, otherwise False."""
    check_schema(schema)
    if schema.get("type") == "null":
        return instance is None
    if schema.get("type") == "bool":
        return isinstance(instance, bool)
    if schema.get("type") == "number":
        return isinstance(instance, float) and schema.get(
            "minimum", float("-inf")
        ) <= instance <= schema.get("maximum", float("inf"))
    # TODO: complete length validation checks for string and array
    if schema.get("type") == "string":
        return isinstance(instance, type(u""))
    return isinstance(instance, list)


def from_schema(schema):
    """Returns a strategy for objects that match the given schema."""
    check_schema(schema)
    # TODO: actually handle constraints on number/string/array schemas
    return dict(
        null=st.none(),
        bool=st.booleans(),
        number=st.floats(allow_nan=False),
        string=st.text(),
        array=st.lists(st.nothing()),
    )[schema["type"]]


# `@st.composite` is one way to write this - another would be to define a
# bare function, and `return st.one_of(st.none(), st.booleans(), ...)` so
# each strategy can be defined individually.  Use whichever seems more
# natural to you - the important thing in tests is usually readability!
@st.composite
def schema_strategy(draw):
    schema = {"type": draw(st.sampled_from(SCHEMA_TYPES))}
    # TODO: generate constraints on number/string/array schemas
    # (hint: can you design this so they shrink to less constrained?)
    return schema


@settings(deadline=None)  # allow for slower tests with large data
@given(st.data(), schema_strategy())
def test_schema_inference(data, schema):
    # Test that we can always generate a valid instance
    instance = data.draw(from_schema(schema))
    assert validate(schema, instance)


# TODO: write a test that shows validate may return False (maybe a unit test!)

