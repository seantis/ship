# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ship',
    version='0.1',
    author='Denis Krienbühl',
    author_email='denis.krienbuehl@gmail.com',
    packages=['ship', 'ship.tests'],
    url='http://pypi.python.org/pypi/ship/',
    license='LICENSE.txt',
    description='Swiss Health Insurance Premiums',
    test_suite='ship.tests.get_suite',
    install_requires=[
        'sqlalchemy',
        'zope.proxy',
    ]
)