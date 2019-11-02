# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.2'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # format demo
#
# Lorem ipsum etc.

# %%
# Set up our testing magics
# %run internal/prelude.py

# %%
from hypothesis import given, strategies as st


# %%
# %%run_pytest[clean]


@given(st.integers(), st.integers())
def test_x(a, b):
    assert a - b < 100


# %%
