from pathlib import Path

import toml

import canarytokens


def test_version():
    """
    Checks if the pyproject.toml and canarytokens.__init__.py::__version__ are in sync.
    TODO/DESIGN: is there a better way bump? poetry something?
    This is a manual version bump in pyproject.toml and __init__.py and just checks
    we consistent.
    """
    path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    with open(path) as fp:
        pyproject = toml.load(fp)
    pyproject_version = pyproject["tool"]["poetry"]["version"]

    package_init_version = canarytokens.__version__

    assert package_init_version == pyproject_version
