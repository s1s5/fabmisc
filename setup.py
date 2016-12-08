# coding: utf-8
from setuptools import setup, find_packages

__author__ = 'Shogo Sawai'
__version__ = '0.0.3'
__license__ = 'MIT'

setup(
    name='fabmisc',
    version=__version__,
    description='fabric utilities',
    license=__license__,
    author=__author__,
    keywords='fabric',
    packages=find_packages(),
    install_requires=[x.strip() for x in open('requirements.txt').readlines()],
)
