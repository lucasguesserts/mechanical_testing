import sys, os
sys.path.insert(0, os.path.abspath('../'))

# --- Project information
project = 'mechanical_testing'
copyright = '2019, Lucas Guesser Targino da Silva'
author = 'Lucas Guesser Targino da Silva'
version = '0.0.0'
release = '0.0.0' # full version, including 'rc', 'beta'

# --- General optins ---
master_doc = 'index'
source_suffix = ['.rst', '.md']
templates_path = ['_templates']
extensions = [
	'sphinx.ext.autodoc',
	'sphinx.ext.autosummary',
	'sphinx.ext.napoleon']
napoleon_numpy_docstring = True
napoleon_use_rtype = False
language = 'en'
exclude_patterns = [] # patters to ignore files
pygments_style = 'sphinx'
todo_include_todos = False

# --- HTML options ---
html_theme = 'sphinx_rtd_theme'
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
        'donate.html',
    ]
}
htmlhelp_basename = 'mechanical_testingdoc'

# --- LaTeX options ---
latex_elements = {
}
latex_documents = [
    (master_doc, 'mechanical_testing.tex', 'experiment\\_interface Documentation',
     'Lucas Guesser Targino da Silva', 'manual'),
]
man_pages = [
    (master_doc, 'mechanical_testing', 'mechanical_testing Documentation',
     [author], 1)
]
texinfo_documents = [
    (master_doc, 'mechanical_testing', 'mechanical_testing Documentation',
     author, 'mechanical_testing', 'One line description of project.',
     'Miscellaneous'),
]