# STEP 4 — FULL SAFE IMPORT HOOK (NO RECURSION)

import importlib.machinery
import sys

from .encoding import rewrite

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


def should_ignore(fullname: str, loader) -> bool:
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
    if fullname.startswith("_"):
        return True

    return False


class FutureTransformLoader(importlib.machinery.SourceFileLoader):
    """A SourceFileLoader that rewrites async-yield-from *without* adding headers."""

    def source_to_code(self, data, path):
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            # not UTF-8, skip
            return super().source_to_code(data, path)

        # Rewrite source code
        rewritten = rewrite(text)

        return super().source_to_code(rewritten.encode("utf-8"), path)


class FutureImportFinder:
    """Finder that rewrites modules unless ignored."""

    def find_spec(self, fullname, path=None, target=None):
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
