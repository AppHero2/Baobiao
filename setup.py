#!/usr/bin/env python

from setuptools import setup

setup(
    name = 'amazon-book-query',
    version = '0.1',
    url = 'https://github.com/internetarchive/amazonbookquery',
    author = 'Eagle19243',
    license = 'BSD',
    py_modules = ['bookquery'],
    scripts=['bookquery.py'],
    description = 'Provide Amazon Book Query search result as a tsv file format',
    install_requires=['requests>=2.18.1'],
    entry_points = {
        'console_scripts': [
            'amazon-book-query=bookquery:main'
        ]
    },
    setup_requires = ['pytest-runner'],
    tests_require = ['pytest'],
    classifiers = [
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)