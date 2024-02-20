# file: setup.py
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='fastask',
    packages=['fastask'],
    version='0.3.6',
    py_modules=['fastask.ask'],
    include_package_data=True,
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'ask = fastask.ask:main',
        ],
    },
    description='A fast and easy tool for getting answers in the command line',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
