# Escape from automanual testing with Hypothesis!

A three-hour workshop on property-based testing with [Hypothesis](https://hypothesis.works),
first delivered at [PyCon 2019](https://us.pycon.org/2019/schedule/presentation/91/).
The SciPy version adds exercises with Numpy and Pandas for a four-hour timeslot.

Hypothesis is a tool for writing more powerful tests.  In traditional "auto-manual"
testing, you choose some specific example data, perform an operation, and check
that you got the expected output.  With Hypothesis, you instead describe the range
of valid data, an operation that can be performed on any such data, and a property
that should always be true!

Properties can be as simple as "no exception is raised" or "values are always between
zero and one", or more complex - like "when I save and reload my data, the output is
equal to the input".  Either way, I find that these tests are easier to write, better
express what I *mean* to test, and they even find bugs that I didn't know were possible!

This tutorial is designed for intermediate Python users, with extension activities up to expert level.
Some minimal experience of unit testing and `pytest` are assumed - if you have ever used
`@pytest.mark.parametrize`, you are overqualified; but if you have never written and run
unit tests you may have trouble.


## How this workshop works

It's a crash-course in the important concepts, alternating between short talks and
hands-on exercises.  You'll get to know the architecture of the library, but not
every detail of the API - you can look up that documentation at any time.


#### Setting up

Clone this repository, and `pip install pytest hypothesis`.  That's it!

Hypothesis is also available on `conda-forge`, if you prefer to use `conda`.
For the SciPy edition of this workshop, there are optional exercises that
require Numpy and Pandas.

To test that everything is installed correctly, run `pytest pbt-101.py`.
You should see nine passing tests and no errors.

*Any recent version of `pytest`, and any `hypothesis>=4.0`.
Use whatever package manager and environment you prefer - if in doubt,
just `pip install` as above.  Hypothesis is compatible with every currently
supported version of Python, i.e. 2.7, 3.5, 3.6, and 3.7 - and a similarly
wide range of versions for it's optional dependencies.*


#### Property-based testing 101

Each block starts with a short talk (slides separated by a blank black slide),
followed by a hands-on exercise where you can apply what you've just learned.
In this first block we'll see
[a taxonomy of testing techniques](https://www.hillelwayne.com/post/a-bunch-of-tests/),
[define property-based testing](https://hypothesis.works/articles/what-is-property-based-testing/),
 and get an initial overview of Hypothesis.

After the talk:

1. Follow the "Setting up" instructions above
2. Run `pytest pbt-101.py`.  You should see several passing tests.
3. Open the file in your preferred editor and read the detailed instructions within!
   (in short: fix the test, check the test fails, fix the test, check that it passes)


#### Hypothesis `strategies` and property-based "tactics"

This block aims to get you comfortable and productive with Hypothesis, which means
covering two things: how to generate all kinds of data, and how to use it in your tests.

`strategies` are objects which tell `@given` what to pass to your test function.
Hypothesis [ships with dozens for standard library types](https://hypothesis.readthedocs.io/en/latest/data.html)
and optional dependencies such as pytz, Django, Numpy, and Pandas - to say nothing of
[third-party extensions](https://hypothesis.readthedocs.io/en/latest/strategies.html)!
We'll see what's available to explicitly describe your data or infer it from a schema
(e.g. strings from a regular expression), and how you can combine, compose and adjust
strategies to produce something quite different.

"Tactics" are design patterns for property based tests.  They range from
[common properties to test](https://fsharpforfunandprofit.com/posts/property-based-testing-2/),
through to [embedding assertions in your code](https://blog.regehr.org/archives/1091)
(not just tests) for [free integration tests](https://www.hillelwayne.com/post/pbt-contracts/),
and more.

After the talk, `pytest strategies-and-tactics.py`, and continue as above.


#### Testing the Untestable *or* Scientific Hypothesis

Nothing is ever really untestable - but sometimes you need better tools to make
testing worth the trouble.  We'll explore two approaches:

- [Stateful testing](https://hypothesis.works/articles/rule-based-stateful-testing/),
  where you define a finite automaton and Hypothesis uses it to generate whole test
  programs (by choosing actions as well as values).
- [Metamorphic testing](https://www.hillelwayne.com/post/metamorphic-testing/),
  where you don't know exactly what the code *should* do - but do know something
  about how changes in the input relate to changes in the output.

The exercises in `test-the-untestable.py` are deliberately challenging.  Choose
whichever one is the most interesting to you, and don't worry if it takes you the
whole block in class - you can always come back to the others later.

Alternatively, if you use the Numpy / Pandas stack, `scientific-hypothesis.py` is
full of exercises that demonstrate Hypothesis' support for generating arrays,
dataframes, and all the related things you might need to test data-centric scripts -
or libraries!


#### The bigger picture

We'll discuss Hypothesis' performance characteristics and configuration options,
get a sense of the community around it and the project roadmap, and look at how
Hypothesis fits into the wider testing and correctness landscape in Python.

For this final block, you have a few options:

- Continue working on any unfinished exercises from previous blocks
- Start testing your own code with Hypothesis
- Join a group discussion - what to you plan to test?  What 'killer feature'
  is missing?


## Useful links

As well as the links above, you may be interested in:

- [Hypothesis' official documentation](https://hypothesis.readthedocs.io/)
- [Hypothesis' technical blog](https://hypothesis.works/articles/technical/)
- [More practice exercises](https://github.com/DRmacIver/hypothesis-training) -
  if you finish early, these are a good challenge.
- [Choosing properties for property-based testing](https://fsharpforfunandprofit.com/posts/property-based-testing-2/)
  is written for F#, but the ideas are useful in any language.
- [PBT with oracle functions](https://www.hillelwayne.com/post/hypothesis-oracles/)
  and [Finding property tests](https://www.hillelwayne.com/post/contract-examples/).
  Hillel Wayne has written several other posts on testing with Hypothesis.
- [*AFL + QuickCheck = ?*](https://danluu.com/testing/) - a hardware engineer's
  perspective on software testing.  (Hypothesis did use coverage information for
  a while, but took it out as the overhead made it net-negative test power)
- [How SQLite is Tested](https://www.sqlite.org/testing.html)
