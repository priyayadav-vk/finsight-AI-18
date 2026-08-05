"""Root shim package for frontend pages."""

# The actual page modules have been moved into the frontend package.
# This package preserves compatibility with imports like `from pages import dashboard`.
# Add lightweight compatibility shims so legacy page modules that still pass
# unsupported Streamlit keyword arguments (e.g., width="stretch") do not crash
# when deployed on environments with different Streamlit versions.

import streamlit as st

def _wrap_ignore_width(func):
    if not callable(func):
        return func
    def _inner(*args, **kwargs):
        # Silently drop 'width' if provided (compatibility with older/newer st API)
        if 'width' in kwargs:
            kwargs.pop('width')
        return func(*args, **kwargs)
    return _inner

# Patch common Streamlit display functions used in the app
for name in ('button', 'dataframe', 'plotly_chart', 'metric'):
    if hasattr(st, name):
        try:
            setattr(st, name, _wrap_ignore_width(getattr(st, name)))
        except Exception:
            # Best-effort: don't fail package import if patching isn't possible
            pass

