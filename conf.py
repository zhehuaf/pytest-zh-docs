"""
pytest 中文文档 Sphinx 配置文件
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import sphinx.application


PROJECT_ROOT_DIR = Path(__file__).parent.resolve()

# -- Project information -------------------------------------------------------------
project = "pytest"
copyright = "2015, holger krekel and pytest-dev team"
version = "8.x"
release = "8.0"
language = "zh_CN"

# -- General configuration -------------------------------------------------------------
root_doc = "index"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_sitemap",
    "sphinx_removed_in",
    "sphinx_inline_tabs",
    "sphinxcontrib_trio",
    "pygments_pytest",
    "sphinx_issues",
]

exclude_patterns = [
    "_build",
    "naming20.rst",
    "test/*",
    "old_*",
    "*attic*",
    "*/attic*",
    "funcargs.rst",
    "setup.rst",
    "example/remoteinterp.rst",
]

add_module_names = False

# -- Options for Autodoc --------------------------------------------------------------
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# -- Options for intersphinx ----------------------------------------------------------
intersphinx_mapping = {
    "pluggy": ("https://pluggy.readthedocs.io/en/stable", None),
    "python": ("https://docs.python.org/zh-cn/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "pip": ("https://pip.pypa.io/en/stable", None),
    "tox": ("https://tox.wiki/en/stable", None),
    "virtualenv": ("https://virtualenv.pypa.io/en/stable", None),
    "setuptools": ("https://setuptools.pypa.io/en/stable", None),
    "packaging": ("https://packaging.python.org/en/latest", None),
}

# -- Options for todo -----------------------------------------------------------------
todo_include_todos = True

# -- Options for linkcheck builder ----------------------------------------------------
linkcheck_ignore = [
    "https://blogs.msdn.microsoft.com/bharry/2017/06/28/testing-in-a-cloud-delivery-cadence/",
    "http://pythontesting.net/framework/pytest-introduction/",
    r"https://github.com/pytest-dev/pytest/issues/\d+",
    r"https://github.com/pytest-dev/pytest/pull/\d+",
]
linkcheck_workers = 5

# -- Options for HTML output ----------------------------------------------------------
html_theme = "furo"
html_theme_options = {"sidebar_hide_name": True}

html_static_path = ["_static"]
html_css_files = [
    "pytest-custom.css",
]

html_title = "pytest 中文文档"
html_short_title = f"pytest-{release}"

html_logo = "_static/pytest1.png"
html_favicon = "img/favicon.png"

html_use_index = False
html_show_sourcelink = False

html_baseurl = "https://pytest-doc-zh.netlify.app/"

sitemap_url_scheme = "{link}"

htmlhelp_basename = "pytestdoc"

# -- Options for manual page output ---------------------------------------------------
man_pages = [
    ("how-to/usage", "pytest", "pytest usage", ["holger krekel at merlinux eu"], 1)
]

# -- Options for epub output ----------------------------------------------------------
epub_title = "pytest"
epub_author = "holger krekel at merlinux eu"
epub_publisher = "holger krekel at merlinux eu"
epub_copyright = "2013, holger krekel et alii"

# -- Options for sphinx_issues extension -----------------------------------------------
issues_github_path = "pytest-dev/pytest"

# -- Custom documentation plugin ------------------------------------------------------
def setup(app: sphinx.application.Sphinx) -> None:
    app.add_crossref_type(
        "fixture",
        "fixture",
        objname="built-in fixture",
        indextemplate="pair: %s; fixture",
    )

    app.add_object_type(
        "globalvar",
        "globalvar",
        objname="global variable interpreted by pytest",
        indextemplate="pair: %s; global variable interpreted by pytest",
    )

    app.add_crossref_type(
        directivename="hook",
        rolename="hook",
        objname="pytest hook",
        indextemplate="pair: %s; hook",
    )
