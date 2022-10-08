from importlib.metadata import entry_points
from setuptools import setup, find_packages

setup(
    name='hyperspacesim',
    packages=find_packages(),
    py_modules=[
        'hyperspacesim'
    ],
    entry_points={
        'console_scripts': ['run-hyperspacesim=hyperspacesim.test_script:main']
    },
)
