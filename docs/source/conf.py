# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from __future__ import annotations
import os
import sys

# Make project root importable for autodoc (docs/source -> project root).
sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'AVIR'
copyright = '2026, AVIR authors'
author = 'AVIR authors'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
]

autosummary_generate = True
add_module_names = False

# Avoid hard import failures for optional/runtime-only dependencies when building docs.
autodoc_mock_imports = [
    "docker",
]

templates_path = ['_templates']
exclude_patterns = []
# Copy docs/source/figs directly into build/html/figs for raw HTML img tags.
html_extra_path = ['figs']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

try:
    import sphinx_rtd_theme  # noqa: F401

    html_theme = "sphinx_rtd_theme"
except Exception:
    # Fallback to a built-in theme if dependency isn't installed in the runtime env.
    html_theme = "alabaster"
html_static_path = [#'_static'
]
