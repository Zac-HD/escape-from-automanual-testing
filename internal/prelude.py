# Configure ipytest for inline testing in Jupyter notebooks.
# Using the %run line magic means this isn't a dependency for local use.

import ipytest

ipytest.config(rewrite_asserts=True, magics=True, tempfile_fallback=True)
