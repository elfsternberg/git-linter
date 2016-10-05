#!/usr/bin/env python
import re
import sys
import argparse
import os.path


def get_data_files(prefix):
    if prefix.startswith('/System/Library/Frameworks'):
        return []
    return [(os.path.join(prefix, 'share/man/man1'), ['docs/_build/man/git-lint.1'])]


parser = argparse.ArgumentParser()
parser.add_argument('--prefix', default='',
                    help='prefix to install data files')
opts, _ = parser.parse_known_args(sys.argv)
prefix = opts.prefix or sys.prefix or '/usr'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='git_linter',
    version='0.0.6',
    description="A git command to lint everything in your workspace (or stage) that was changed since the last commit.",
    long_description=readme + '\n\n' + history,
    author='Kenneth M. "Elf" Sternberg',
    author_email='elf.sternberg@gmail.com',
    url='https://github.com/elfsternberg/git_linter',
    packages=[
        'git_lint',
    ],
    package_dir={'git_lint':
                 'git_lint'},
    include_package_data=True,
    data_files=get_data_files(prefix),
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    scripts=['bin/git-lint-style'],
    keywords='git lint style syntaxt development',
    entry_points={
        'console_scripts': [
            'git-lint = git_lint.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
