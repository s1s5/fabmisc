# coding: utf-8
from setuptools import setup, find_packages
from fabmisc import __author__, __version__, __license__

setup(
    name='fabmisc',
    version=__version__,
    description='fabric utilities',
    license=__license__,
    author=__author__,
    keywords='fabric',
    packages=find_packages(),
    install_requires=[x.strip() for x in open('requirements').readlines()],
)
