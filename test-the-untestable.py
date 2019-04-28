""" (this file is problem set three of three)


This file contains most of the code for four problems:

- Solving the "water jug problem" from *Die Harder* with stateful testing
- Solving the "Towers of Hanoi" puzzle with stateful testing
- Validating summary statistics for numeric types with metamorphic testing
- Checking graph search algorithms with metamorphic testing

If you're more interested in metamorphic testing, I'd skip down to the statistics
problem and then come back to the water jug problem if you finish early.
"""

from hypothesis import note, settings
from hypothesis.stateful import RuleBasedStateMachine, invariant, precondition, rule

##############################################################################
# The Water Jug problem.  Thanks to Nicholas Chammas for the idea and demo!
# Spoilers at http://nchammas.com/writing/how-not-to-die-hard-with-hypothesis

# In the movie Die Hard with a Vengeance (aka Die Hard 3), there is a famous
# scene where John McClane (Bruce Willis) and Zeus Carver (Samuel L. Jackson)
# have to solve a problem or be blown up: Given a 3 gallon jug and a 5 gallon jug,
# how do you measure out exactly 4 gallons of water?
# https://www.youtube.com/watch?v=6cAbgAaEOVE

# We don't have a bomb handy, but we *can* make Hypothesis solve this for us!
# We just need to set up the state and possible actions... then we can claim
# that making random moves never leads to the "solved" state, and let
# Hypothesis find a counter-example.  Fortunately, Hypothesis will also
# shrink what it finds to a minimal sequence of actions!

# This pattern, where all the state lives on the RuleBasedStateMachine,
# is the easiest way to get started with stateful testing.


# Volumes provided as constants so you can experiment with other sizes.
TARGET_VOLUME = 4
SMALL_JUG_CAPACITY = 3
LARGE_JUG_CAPACITY = 5


@settings(max_examples=2000)  # Try harder!
class DieHardProblem(RuleBasedStateMachine):
    small = 0
    large = 0

    @invariant()
    def small_jug_capacity(self):
        assert 0 <= self.small <= SMALL_JUG_CAPACITY

    @invariant()
    def large_jug_capacity(self):
        assert 0 <= self.large <= LARGE_JUG_CAPACITY

    @invariant()
    def die_hard_problem_not_solved(self):
        note("    small={}, large={}".format(self.small, self.large))
        assert self.large != 4

    # Fill out the methods for the six actions below to solve the puzzle!

    @rule()
    def fill_small(self):
        pass

    @rule()
    def fill_large(self):
        pass

    @rule()
    def empty_small(self):
        pass

    @rule()
    def empty_large(self):
        pass

    @rule()
    def pour_small_into_large(self):
        pass

    @rule()
    def pour_large_into_small(self):
        pass


# The `.TestCase` attribute of a StateMachine is an automatically created
# unittest.TestCase, so assigning to a global variable ending in "Test"
# ensure that it will be collected and run by our test runner.
DieHardTest = DieHardProblem.TestCase


##############################################################################
# Towers of Hanoi.  Thanks to Harry Stern for the idea and demo!
# Spoilers: https://github.com/HypothesisWorks/hypothesis/issues/1857

# As a kid, I remember playing with this puzzle and thinking that it was
# impossible.  Let's try to validate my frustration by testing that with
# Hypothesis!

# Note that for this example, we have two changes compared to the last:
# 1. The state is not managed by the RuleBasedStateMachine, but by a
#    "system under test" (HanoiPuzzle), and
# 2. You will need to decide what actions possible, and use preconditions
#    to tell Hypothesis which are *valid* from the current state.


class HanoiPuzzle(object):
    """A model for https://en.wikipedia.org/wiki/Tower_of_Hanoi

    Make a move by calling `self.move("A", "B")`, `self.move("B", "C")`,
    and so on - but you'd better check that it's a valid move first!
    """

    def __init__(self, num_rings=3):
        assert 1 <= num_rings <= 10
        self.rings = tuple(reversed(range(num_rings)))
        self.A = list(self.rings)
        self.B = []
        self.C = []

    def __repr__(self):
        return "<HanoiPuzzle with A={self.A}, B={self.B}, C={self.C}>".format(self=self)

    def check_valid(self):
        assert set(self.A + self.B + self.C) == set(self.rings)
        for peg in (self.A, self.B, self.C):
            assert peg == sorted(peg, reverse=True)

    @property
    def is_solved(self):
        return self.A == [] and self.B == [] and self.C == list(self.rings)

    def move(self, source, dest):
        note("Moving disk from {} to {}".format(source, dest))
        assert source in set("ABC") and dest in set("ABC")
        source, dest = getattr(self, source), getattr(self, dest)
        dest.append(source.pop())


class HanoiSolver(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.hanoi = HanoiPuzzle(3)

    @invariant()
    def puzzle_not_solved(self):
        assert not self.hanoi.is_solved

    @invariant()
    def no_invalid_moves(self):
        self.hanoi.check_valid()

    # Write an @rule() for each possible move, and fill in the precondition
    # to avoid making any invalid moves.  You may want to define a helper
    # function to make this less verbose!

    @precondition(lambda self: ...)
    @rule()
    def move_A_to_B(self):
        # TODO: Move A to B, not this no-op.
        self.hanoi.move("A", "A")


HanoiTest = HanoiSolver.TestCase


##############################################################################
# Metamorphic testing and statistics demo: how hard can mean() be anyway?

# If you've done much numerical programming, the simple "laws of mathematics"
# taught in high school might seem like a fond and faded dream.
# Integer rounding, overflow and underflow, NaN, and floating point generally
# laugh at the simple behaviour of rational numbers.  Fortunately for our
# sanity, `fractions.Fraction` is one standard-library import away.
#
# Let's see how this can help via some metamorphic mean() testing....


# from statistics import mean  # Can't wait for 2020 and the Python 2 EoL :p
import math
from fractions import Fraction

import pytest

from hypothesis import assume, given, strategies as st


def mean(data, as_type=Fraction):
    """Return the mean of the input list, as the given type."""
    assert as_type in (int, float, Fraction), as_type
    if as_type == int:
        return sum(int(n) for n in data) // len(data)  # integer division case
    return sum(as_type(n) for n in data) / len(data)  # float or Fraction case


# You can use parametrize and given together, but two tips for best results:
# 1. Put @parametrize *outside* @given -
# 2. Use named arguments to @given - avoids positional confusion or collisions
@pytest.mark.parametrize(
    "type_, strat",
    [
        (int, None),
        (float, st.floats(allow_nan=False, allow_infinity=False)),
        (Fraction, None),
    ],
)
@given(data=st.data())
def test_mean_properties(data, type_, strat):
    strat = strat or st.from_type(type_)
    values = data.draw(st.lists(strat, min_size=1))
    result = mean(values)  # already testing no exceptions!
    # TODO: property assertions, e.g. bounds on result, etc.
    if type_ is Fraction:
        assert min(values) <= result <= max(values)
    # What constraints make sense for an integer mean?

    # TODO: metamorphic test assertions.  For example, how should result
    # change if you add the mean to values?  a number above or below result?
    # Remove some elements from values?


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
