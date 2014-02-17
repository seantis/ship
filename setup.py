# -*- coding: utf-8 -*-

name = "ship"
description = "Swiss Health Insurance Premiums."
version = '0.3'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_long_description():
    readme = open('README.rst').read()
    history = open('HISTORY.rst').read()

    return '\n'.join((readme, history))


setup(
    name=name,
    version=version,
    author='Denis Krienbühl',
    author_email='denis.krienbuehl@gmail.com',
    packages=['ship', 'ship.tests'],
    url='http://pypi.python.org/pypi/ship/',
    license='LICENSE.txt',
    description=description,
    long_description=get_long_description(),
    test_suite='ship.tests.get_suite',
    install_requires=[
        'sqlalchemy',
        'zope.proxy',
    ]
)