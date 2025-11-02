import os
import sys
from datetime import datetime

# Add project root to path for autodoc
sys.path.insert(0, os.path.abspath('..'))

project = 'ElectroSim'
author = 'Danny Luna'
copyright = f"{datetime.now():%Y}, {author}"
version = '1.0'
release = '1.0.0'

extensions = [
    'myst_parser',
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.mathjax',
    'sphinxcontrib.mermaid',
    'sphinxcontrib.bibtex',
    'sphinx.ext.autosectionlabel',
]

autosummary_generate = True
add_module_names = False
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_rtype = False
napoleon_use_param = True

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'inherited-members': True,
    'show-inheritance': True,
}

myst_enable_extensions = [
    'dollarmath',  # Enable $...$ and $$...$$ for inline and display math
    'amsmath',     # Enable advanced math environments
]

# Bibliography configuration
bibtex_bibfiles = ['references.bib']
bibtex_default_style = 'plain'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output options
html_theme = 'pydata_sphinx_theme'
html_static_path = []  # Custom static files directory (empty if not using custom CSS/JS)
html_title = 'ElectroSim Documentation'

# Theme options
html_theme_options = {
    "default_mode": "light",
    "show_toc_level": 2,
    "navigation_depth": 3,
    "show_nav_level": 2,
}

# Mermaid configuration
mermaid_version = "10.9.0"
mermaid_init_js = "mermaid.initialize({startOnLoad:false});"
