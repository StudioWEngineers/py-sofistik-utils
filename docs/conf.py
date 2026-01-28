import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

# -- Project information --
project = "py-sofistik-utils"
author = "StudioWEngineers"
copyright = "2026, StudioWEngineers"

# -- General configuration --
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx.ext.napoleon"
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "inherited-members": True,
}

default_role = "any"
templates_path = ["_templates"]

primary_domain = "py"
highlight_language = "python"

add_module_names = False
autosummary_generate = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None)
}

html_theme = "furo"
html_title = f"{project} documentation"
