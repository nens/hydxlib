from setuptools import setup

import pathlib


def get_version():
    # Edited from https://packaging.python.org/guides/single-sourcing-package-version/
    init_path = pathlib.Path(__file__).parent / "hydxlib/__init__.py"
    for line in init_path.open("r").readlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


version = get_version()
long_description = "\n\n".join([open("README.rst").read(), open("CHANGES.rst").read()])
install_requires = [
    "sqlalchemy",
    "threedi-modelchecker>=0.34",
    "pyproj>=3",
]
tests_require = ["pytest"]

setup(
    name="hydxlib",
    version=version,
    description="Importer and Exporter for GWSW",
    long_description=long_description,
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
    ],
    keywords=[],
    author="Nelen & Schuurmans",
    author_email="info@nelen-schuurmans.nl",
    url="",
    license="MIT",
    packages=["hydxlib"],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={"test": tests_require},
    entry_points={"console_scripts": ["run-hydxlib = hydxlib.scripts:main"]},
)
