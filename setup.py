# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='access1581',
    version='0.0.1',
    description='Sample package for Python-Guide.org',
    long_description=readme,
    author='Henning Pingel',
    author_email='henning@henningpingel.de',
    url='https://github.com/hpingel/pyaccess1581',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
