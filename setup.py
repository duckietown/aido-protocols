from setuptools import setup


def get_version(filename: str):
    import ast

    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith("__version__"):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError("No version found in %r." % filename)
    if version is None:
        raise ValueError(filename)
    return version


version = get_version(filename="src/aido_schemas/__init__.py")

line = "daffy"
install_requires = [
    "termcolor",
    "zuper-nodes-z6>=6.2.8",
    "zuper-typing-z6",
    "zuper-commons-z6",
    "numpy",
]
tests_require = ["pydot"]

setup(
    name=f"aido-protocols-{line}",
    version=version,
    keywords="",
    package_dir={"": "src"},
    packages=["aido_schemas"],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        "test": tests_require,
    },
    entry_points={
        "console_scripts": [],
    },
)
