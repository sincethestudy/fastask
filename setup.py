# file: setup.py
from setuptools import setup

setup(
    name='fastask',
    version='0.2',
    py_modules=['ask'],
    entry_points={
        'console_scripts': [
            'ask = ask:main',
        ],
    },
)