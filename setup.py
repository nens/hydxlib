from setuptools import setup


version = "0.8.dev0"
long_description = "\n\n".join([open("README.rst").read(), open("CHANGES.rst").read()])
install_requires = ["sqlalchemy", "threedi-modelchecker"]
tests_require = ["pytest", "pytest-cov"]

setup(
    name="hydxlib",
    version=version,
    description="Importer and Exporter for GWSW",
    long_description=long_description,
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=["Programming Language :: Python"],
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
