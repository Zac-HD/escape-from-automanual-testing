""" (this file is an alternative set three of three)


This file contains most of the code for example tests that use Numpy
and/or Pandas.

If you're interested in testing numerical code or scientific software,
you're in the right place!
"""

from io import BytesIO

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO  # Please move off Python 2 VERY SOON!

import numpy as np
import pandas as pd

from hypothesis import given, settings
import hypothesis.strategies as st  # the usual, standard library, strategies
import hypothesis.extra.numpy as npst  # strategies for use with Numpy
import hypothesis.extra.pandas as pdst  # strategies for use with Pandas


##############################################################################
# Save and load an array
#
# This test is pretty simple: given a Numpy ndarray, save it to "disk"
# (we'll use an in-memory BytesIO stream for speed and easier cleanup),
# and read it back.  The test should pass if we get the same array back.
#
# TODO: feed in more complicated inputs.
# Does this fail for rarer shapes or datatypes?
#
# See https://hypothesis.readthedocs.io/en/latest/numpy.html - especially
# the `array_shapes()` and `nested_dtypes` strategies.


@given(npst.arrays(dtype=np.uint8, shape=(1,)))
def test_array_round_trip(arr):
    with BytesIO() as f:
        np.save(f, arr)
        contents = f.getvalue()
    with BytesIO(contents) as f:
        new = np.load(f)
    # Numpy ships some fantastic helper functions for testing!
    np.testing.assert_array_equal(arr, new)


##############################################################################
# Save and load a Pandas dataframe
#
# This test is pretty similar!  Three reasons: it's a good way to show you how
# the Hypothesis-for-Pandas API works, it should emphasise that round-trip tests
# are *shockingly* effective, and save/load is a simple example of functionalty
# that everyone uses no matter what domain they work in.
#
# TODO: Write tests that show one dtype that you can round-trp through CSV
# and/or JSON, and one that you can't.
#
# See https://hypothesis.readthedocs.io/en/latest/numpy.html#pandas for details,
# and remember that you can use Numpy arrays or even lists of tuples if it helps!


@given(
    pdst.data_frames(
        columns=pdst.columns(3, dtype="float64"),
        index=pdst.indexes(
            dtype="float64", elements=st.floats(allow_nan=False), unique=True
        ),
    )
)
def test_dataframe_round_trip(df):
    with BytesIO() as f:
        df.to_pickle(f, compression=None)
        contents = f.getvalue()
    with BytesIO(contents) as f:
        new = pd.read_pickle(f, compression=None)
    # Pandas ships testing helper functions too!
    pd.testing.assert_frame_equal(df, new)
