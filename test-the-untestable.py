""" (this file is problem set three of three)


This file contains most of the code for four problems:

- Solving the "water jug problem" from *Die Harder* with stateful testing
- Solving the "Towers of Hanoi" puzzle with stateful testing
- Validating summary statistics for numeric types with metamorphic testing

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
        """Filling the small jug from the fountain sets its volume
        to SMALL_JUG_CAPACITY."""
        pass

    @rule()
    def fill_large(self):
        pass

    @rule()
    def empty_small(self):
        """Sets small jug volume to zero."""
        pass

    @rule()
    def empty_large(self):
        pass

    @rule()
    def pour_small_into_large(self):
        """Pours water from the small jug into the large jug UNTIL the
        large jug is full; any remaining water stays in the small jug.
        For example:
            small=3, large=0 -> small=0, large=3
            small=3, large=3 -> small=1, large=5
        """
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
        for name in "ABC":
            peg = getattr(self, name)
            msg = "self.{}={} is invalid".format(name, peg)
            assert peg == sorted(peg, reverse=True), msg

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
        RuleBasedStateMachine.__init__(self)
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

    @precondition(lambda self: True)  # TODO: tighten the precondition
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
#
# `test_mean_properties` is a template that you can use to explore
# metamorphic testing; for example checking that taking the mean, appending
# it to the input, and taking the mean again is equal to the first output.
# More suggestions below - and good luck with the floats() cases!


# from statistics import mean  # Can't wait for 2020 and the Python 2 EoL :p
import math
from fractions import Fraction

import pytest

from hypothesis import assume, given, strategies as st


def mean(data, as_type=Fraction):
    """Return the mean of the input list, as the given type."""
    # This function is a correct implementation of the arithmetic mean,
    # so that you can test it according to the metamorphic properties of
    # that mathematical equation for integers, floats, and fractions.
    assert as_type in (int, float, Fraction), as_type
    if as_type == int:
        return sum(int(n) for n in data) // len(data)  # integer division case
    return sum(as_type(n) for n in data) / len(data)  # float or Fraction case


# You can use parametrize and given together, but two tips for best results:
# 1. Put @parametrize *outside* @given - it doesn't work properly from the inside
# 2. Use named arguments to @given - avoids confusing or colliding positional arguments
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
