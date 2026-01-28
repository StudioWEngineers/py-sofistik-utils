import sys
print("=== SYS.PATH ===")
for p in sys.path:
    print(p)

try:
    import py_sofistik_utils
    print("py_sofistik_utils OK", py_sofistik_utils)
    import py_sofistik_utils.cdb_reader
    print("cdb_reader OK")
except Exception as e:
    print("IMPORT FAILED:", e)

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
