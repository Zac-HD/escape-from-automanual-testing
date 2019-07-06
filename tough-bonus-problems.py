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


# Simplified json-schema inference

# One really useful pattern for complex data is to infer a strategy from an
# existing schema of some kind.  For example, Hypothesis ships with functions
# for inference from types, regular expressions, Numpy dtypes, etc.
#
# This exercise is to write a function that, given a simple "json-schema",
# returns a strategy for objects that will match that schema (details below).
# The goal is to show you the trade-offs involved in building customised
# inference and helpers on top of Hypothesis - they're fantastic once finished!
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


##############################################################################
# Metamorphic testing with pathfinding problems

from collections import deque
from string import ascii_uppercase

"""How to demonstrate metamorphic testing, without any dependencies?
The technique really shines for larger and more complex systems -
my current favorite example is general tests for RESTful APIs
(http://www.lsi.us.es/~segura/files/papers/segura17-tse.pdf).

So this will be somewhat artificial, sorry.
Hopefully I've convinced you that it's worth trying on real problems though!


Let's do some puzzles with graphs: they're a nice but non-trivial data
structure, and have enough variants that we can solve a problem, make it more
complicated, and then solve it again.

We'll represent graphs as a dict of `{node: {set of (node, cost) tuples}}`.
This representation is a *directed* graph, and allows self-links, but we can
generate examples with neither if that's easier.

I've provided a basic but working implementation of a graphs() strategy,
breadth-first search, and a test that there is a path between any two nodes
(which should pass thanks to the force_path=True argument).
You can expand that test, and then implement one or more of the metamorphic
tests suggested at the bottom of the file.

If you want to keep going with this one, implement edge costs - and good luck!
"""


@st.composite
def graphs(
    draw,
    keys=ascii_uppercase,
    allow_self_links=True,
    directed=True,
    force_path=True,
    edge_cost=False,
):
    result = {c: set() for c in keys}
    for i, c in enumerate(keys):
        # The inner strategy for keys (node identifiers) is a sampled_from,
        # rejecting the current node iff allow_self_links is False.
        # Cost will always be 1, or 1-10 inclusive if edge_cost is True.
        # Then we choose a set of neighbors for node c, and update the graph:
        key_strat = st.sampled_from(keys).filter(lambda k: allow_self_links or k != c)
        cost_strat = st.integers(1, 10) if edge_cost else st.just(1)
        neighbors = draw(
            st.sets(st.tuples(key_strat, cost_strat), min_size=1, max_size=4)
        )

        result[c].update(neighbors)
        if not directed:
            for k in neighbors:
                result[k].add((c, 1))
        if force_path:
            # Ensure that there *is* always a path between any pair of nodes,
            # by linking each node to the next in order.  We therefore have a
            # directed ring, plus some number of cross-links.
            result[c].add((keys[i - 1], 1))
            if not directed:
                result[keys[i - 1]].add((c, 1))
    return result


def breadth_first_search(graph, start, end):
    """Return the lowest-cost path from start to end, as a list of nodes to visit.

    If start and end are not connected None will be returned.  If start == end
    and there is a self-link, [end] will be returned.  For example, with:

        A --- B --- C >
        |     |
        D --- E     F

    bfs(A, C) -> [B, C]
    bfs(A, E) -> [D, E]  # [B, E] also valid - see below
    bfs(C, C) -> [C]
    bfs(A, F) -> None

    If there are multiple paths of equal cost, ties are broken by the number
    of nodes, then comparison of differing nodes with lesser winning.
    """
    assert start in graph and end in graph
    if start == end:
        return (start,)
    # TODO: implemented cost-aware search if you want an harder problem!
    seen = set()
    paths = deque()
    paths.append((start,))
    while paths:
        path_so_far = paths.popleft()
        current_node = path_so_far[-1]
        for node, _cost in sorted(graph[current_node]):
            if node in seen:
                continue
            seen.add(node)
            paths.append(path_so_far + (node,))
            if node == end:
                return paths[-1][1:]
    return None


@given(graphs(), st.sampled_from(ascii_uppercase), st.sampled_from(ascii_uppercase))
def test_bfs_connected(graph, start, end):
    path = breadth_first_search(graph, start, end)
    assert path[-1] == end
    assert len(path) == len(set(path)), "path={} has loops!".format(path)
    # TODO: make any relevant assertions about appearance of start node
    # TODO: check that there is a connection between each node in the path
    # TODO: try `graphs(force_path=False)`.  What do you expect to happen?


# Re-implementing graph search in twenty minutes is a bit much (this isn't
# an interview!), so we'll use metamorphic testing instead.  Even with an
# untrusted searcher, we know that certain properties should hold:
#
# 1. For any bfs(graph, start, end) -> a path [start, ..., mid, ... end]
#    the path from start to mid and mid to end should be the original path.
#    This is the "trust but verify" perspective.
#
# 2. Similarly, forcing the path to go via any point *not* included in
#    the original must lead to a path at least that long.
#    This is a "suspicious" approach to verification.
#
# 3. Irrelevant additions: adding disconnected nodes or components to the
#    graph should not change the result at all.  Nor should linking the
#    midpoint to any new node such that the path from new to end is longer
#    than from midpoint to end (or, symmetrically, for start).
#
# 4. Relevant changes: linking two nodes in the shortest path should drop
#    the nodes between the two newly-linked nodes, but not otherwise change
#    the path.
#
# 5. For undirected graphs, the path from end to start should be the
#    reverse of the path from start to end (accounting for implicit start)
#
# These tests are reasonably quick even for very large graphs,
# where a brute-force search would be infeasible.
#
# So: why not write a test for each based on the stub below?


@given(graphs(), st.data())
def test_bfs_finds_shortest_path(graph, data):
    # Using label=... is easier to follow than the default "Draw #1" style!
    start = data.draw(st.sampled_from(sorted(graph)), label="start")
    end = data.draw(st.sampled_from(sorted(graph)), label="end")
    path = breadth_first_search(graph, start, end)
    midpoint = data.draw(st.sampled_from(path), label="midpoint")
    # TODO: your code here!
