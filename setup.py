#!/usr/bin/env python

from setuptools import setup

setup(
    name = 'amazonbookquery',
    version = '1.0',
    url = 'https://github.com/Eagle19243/amazon-book-query',
    author = 'Eagle19243',
    license = 'BSD',
    packages = ['amazonbookquery'],
    scripts=['amazonbookquery/utils.py'],
    description = 'Provide Amazon Book Query search result as a tsv file format',
    install_requires=['requests'],
    entry_points = {
        'console_scripts': [
            'amazon-book-query=amazonbookquery.utils:main'
        ]
    },
    setup_requires = ['pytest-runner'],
    tests_require = ['pytest', 'lxml'],
    classifiers = [
        'Development Status :: 1 - Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)