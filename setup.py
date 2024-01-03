# file: setup.py
from setuptools import setup

setup(
    name='fastask',
    version='0.2',
    py_modules=['ask'],
    package_data={'': ['Modelfile']},
    include_package_data=True,
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