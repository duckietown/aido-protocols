from setuptools import setup


def get_version(filename):
    import ast
    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError('No version found in %r.' % filename)
    if version is None:
        raise ValueError(filename)
    return version


version = get_version(filename='src/aido_nodes/__init__.py')

setup(
        name='aido-protocols',
        version=version,
        keywords='',
        package_dir={'': 'src'},
        packages=['aido_nodes'],
        install_requires=[

        ],
        entry_points={
            'console_scripts': [
                'aido_node_wrap=aido_nodes:aido_node_wrap_main',
            ],
        },
)
