# file: setup.py
from setuptools import setup

setup(
    name='fastask',
    packages=['fastask'],
    version='0.2',
    py_modules=['ask'],
    include_package_data=True,
    package_data={'fastask': ['Modelfile']},
    install_requires=[
        'openai',
        'configparser',
        'inquirer',
    ],
    entry_points={
        'console_scripts': [
            'ask = ask:main',
        ],
    },
)