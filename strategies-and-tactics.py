""" (this file is problem set two of three)


This file contains problems that are designed to expose you to the
`hypothesis.strategies` API and a variety of techniques for composing
or adjusting strategies for your tests.

Key link:  https://hypothesis.readthedocs.io/en/latest/data.html


"""

from hypothesis import given, settings, strategies as st


##############################################################################
#

# NOTE: filter


##############################################################################
#

# NOTE: map


##############################################################################
#

# NOTE: flatmap


##############################################################################
#

# NOTE: something about different ways to define recursive data?


##############################################################################
#

# NOTE: composite starting with return constant; force use of verbose mode to check filled out version


##############################################################################
# Simplified json-schema inference

# One really useful pattern for complex data is to infer a strategy from an
# existing schema of some kind.  For example, Hypothesis ships with functions
# for inference from types, regular expressions, Numpy dtypes, etc.
#
# This excercise is to write a function that, given a simple "json-schema",
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
    # TODO: string: check maxLength and minLength, no other keys
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
    # TODO: complete validation checks for string and array
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
# natural to you - the important thing in tests is usally readability!
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

