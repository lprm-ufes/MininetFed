#!/usr/bin/env python

"Setuptools params"

from setuptools import setup, find_packages

setup(
    name='mininetfed',
    version='1.0.0',
    description='(INSERIR DESCRIÇÃO)',
    author='jjakob10',
    author_email='johann.bastos@edu.ufes.br',
    url='https://github.com/lprm-ufes/MininetFed',
    packages=['federated'],
    include_package_data=True,
    package_data={
        'mininetfed.scripts': ['clean.sh'],
    },
    entry_points={
        'console_scripts': [
            'mnf_clean=scripts.clean:main',
        ],
    }
)
