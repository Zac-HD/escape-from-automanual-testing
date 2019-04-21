""" (this file is problem set three of three)


This file contains most of the code for three problems:

- Solving the "water jug problem" from *Die Harder* with stateful testing
- Solving the "Towers of Hanoi" puzzle with stateful testing
- Validating a K-means clustering implementation with metamorphic testing

If you're more interested in metamorphic testing, I'd skip down to the K-means
problem and then come back to the water jug problem if you finish early.
"""

from hypothesis import note, settings
from hypothesis.stateful import RuleBasedStateMachine, invariant, precondition, rule

##############################################################################
# The Water Jug problem.  Thanks to Nicholas Chammas for the idea and demo!
# Spoilers at http://nchammas.com/writing/how-not-to-die-hard-with-hypothesis


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


class HanoiPuzzle(object):
    """A model for https://en.wikipedia.org/wiki/Tower_of_Hanoi

    You can make a move by calling `self.a2b()`, `self.b2c()`,
    and so on - but better check that it's a valid move first!
    """

    def __init__(self, num_rings=3):
        assert 1 <= num_rings <= 10
        self.num_rings = num_rings
        self.A = list(reversed(range(0, num_rings)))
        self.B = []
        self.C = []

    def __repr__(self):
        return "<HanoiPuzzle with A={self.A}, B={self.B}, C={self.C}>".format(self=self)

    def check_valid(self):
        assert set(self.A + self.B + self.C) == set(range(self.num_rings))
        for peg in (self.A, self.B, self.C):
            assert peg == sorted(peg, reverse=True)

    @property
    def is_solved(self):
        return self.A == [] and self.B == [] and self.C == list(range(self.num_rings))

    def move(self, source, dest):
        note("Moving disk from {} to {}".format(source, dest))
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

