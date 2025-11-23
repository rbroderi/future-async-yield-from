# STEP 4 — FULL SAFE IMPORT HOOK (NO RECURSION)

from __future__ import annotations

import importlib.abc
import importlib.machinery
import sys
from collections.abc import Sequence
from types import ModuleType
from typing import Any

import tokenize_rt  # type: ignore[import]

from .ast_encoding import rewrite_async_yield_from

PACKAGE_NAME = "future_async_yield_from"

SAFE_PREFIXES = (
    PACKAGE_NAME,  # our own package (never transform)
    "_",  # builtins: _frozen_importlib, _opcode, _lzma, etc
)

SAFE_LOADERS = (
    importlib.machinery.BuiltinImporter,
    importlib.machinery.ExtensionFileLoader,
    importlib.machinery.FrozenImporter,
    importlib.machinery.NamespaceLoader,
)


def rewrite(source: str) -> str:
    """Rewrite the provided source, expanding any async-yield-from blocks."""

    if "async" not in source:
        return source

    tokens = tokenize_rt.src_to_tokens(source)
    rewritten_tokens = rewrite_async_yield_from(tokens)
    if rewritten_tokens == tokens:
        return source
    return tokenize_rt.tokens_to_src(rewritten_tokens)


def should_ignore(fullname: str, loader: importlib.abc.Loader | None) -> bool:
    """
    Returns True for any module that must **never** be intercepted.
    """

    # Don't importhook ourselves or our submodules
    if fullname.startswith(PACKAGE_NAME):
        return True

    # Don't touch builtins, frozen modules, extensions
    if loader is not None and isinstance(loader, SAFE_LOADERS):
        return True

    # Never rewrite private/underscore-prefixed modules
    if fullname.startswith("_") and fullname != "__main__":
        return True

    return False


class FutureTransformLoader(importlib.machinery.SourceFileLoader):
    """A SourceFileLoader that rewrites async-yield-from *without* adding headers."""

    def source_to_code(self, data: Any, path: Any, *, _optimize: int = -1):  # type: ignore[override]
        text: str
        if isinstance(data, (bytes, bytearray)):
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                # not UTF-8, skip
                return super().source_to_code(data, path)
        elif isinstance(data, str):
            text = data
        else:
            return super().source_to_code(data, path)

        # Rewrite source code
        rewritten = rewrite(text)

        return super().source_to_code(rewritten.encode("utf-8"), path)


class FutureImportFinder(importlib.abc.MetaPathFinder):
    """Finder that rewrites modules unless ignored."""

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        try:
            # Always ask the NEXT finder, never ourselves → no recursion
            spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        except RecursionError:
            raise
        except Exception:
            return None

        if spec is None:
            return None

        # Must ignore?
        if should_ignore(fullname, spec.loader):
            return None

        # Only rewrite normal .py files
        if not isinstance(spec.loader, importlib.machinery.SourceFileLoader):
            return None

        if spec.origin is None:
            return spec

        # Replace loader with our wrapper
        spec.loader = FutureTransformLoader(fullname, spec.origin)
        return spec


def install_hook():
    # Prevent double-installation
    if any(isinstance(f, FutureImportFinder) for f in sys.meta_path):
        return

    # Insert BEFORE PathFinder
    for i, finder in enumerate(sys.meta_path):
        if finder is importlib.machinery.PathFinder:
            sys.meta_path.insert(i, FutureImportFinder())
            break
    else:
        sys.meta_path.append(FutureImportFinder())


# Install immediately when package is imported
install_hook()
