"""Test package initialization that ensures the import hook is active."""

# Importing the package installs the meta_path hook at import time.
import future_async_yield_from.importhook  # noqa: F401
