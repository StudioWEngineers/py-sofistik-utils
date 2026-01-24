import os
import sys

# -- Path setup ------------------------------------------------------------
sys.path.insert(0, os.path.abspath("../src"))

# -- Project information ---------------------------------------------------
project = "py-sofistik-utils"
author = "StudioWEngineers"
copyright = "2026, StudioWEngineers"
version = "0.0.2-dev1"

# -- General configuration -------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",           # core autodoc
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",       # links to Python, numpy, pandas
    "sphinx_copybutton"
]

# Hide full module names in docs
add_module_names = False

# Autodoc options
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "inherited-members": True,
   # "no-signatures": True  # <-- THIS removes constructor args
}


# Default role for `text`
default_role = "any"
templates_path = ["_templates"]

# Exclude patterns
#exclude_patterns = [".build", "release.rst", "**/_internal/**", "**/tests/**"]

# Primary language
primary_domain = "py"
highlight_language = "python"

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

# -- Options for HTML output ----------------------------------------------
html_theme = "furo"
html_title = f"{project} v{version} documentation"

# -- Options for LaTeX output ---------------------------------------------
latex_engine = "pdflatex"
latex_use_latex_multicolumn = True
