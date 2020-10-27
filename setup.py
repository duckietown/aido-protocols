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
    "compmake-z6",
    "pyparsing",
    "PyContracts3",
    "networkx>=2,<3",
    "termcolor",
    "pydot",
    "zuper-ipce-z6>=6.0.34",
    "zuper-nodes-z6>=6.0.33",
]

setup(
    name=f"aido-protocols-{line}",
    version=version,
    keywords="",
    package_dir={"": "src"},
    packages=["aido_schemas", "aido_schemas_tests",],
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "aido-log-draw=aido_schemas.utils_drawing:aido_log_draw_main",
            "aido-log-video=aido_schemas.utils_video:aido_log_video_main",
            "aido-log-video-ui-image=aido_schemas.utils_video:aido_log_video_ui_image_main",
        ],
    },
)
