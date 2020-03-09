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

line = "daffy-aido4"

setup(
    name=f"aido-protocols-{line}",
    version=version,
    keywords="",
    package_dir={"": "src"},
    packages=["aido_schemas", "aido_schemas_tests",],
    install_requires=[
        "compmake",
        "pyparsing",
        "PyContracts",
        "networkx<3",
        "termcolor",
        "pydot",
        "zuper-ipce-z6",
        "zuper-nodes-z6",
    ],
    entry_points={
        "console_scripts": [
            "aido-log-draw=aido_schemas.utils_drawing:aido_log_draw_main",
            "aido-log-video=aido_schemas.utils_video:aido_log_video_main",
        ],
    },
)
