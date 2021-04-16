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
    # "pyparsing",
    # "networkx>=2,<3",
    "termcolor",
    # "pydot",
    # "zuper-ipce-z6>=6.0.34",
    "zuper-nodes-z6>=6.0.37",
]

setup(
    name=f"aido-protocols-{line}",
    version=version,
    keywords="",
    package_dir={"": "src"},
    packages=["aido_schemas"],
    install_requires=install_requires,
    entry_points={"console_scripts": [],},
)
