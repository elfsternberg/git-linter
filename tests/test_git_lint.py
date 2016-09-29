#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

"""
test_git_lint
----------------------------------

Tests for `git_lint` module.
"""

import pytest
import copy
import os
import shutil
import subprocess
import pprint
import tempfile
from git_lint import git_lint

environment = copy.copy(os.environ)
environment.update({
    'LANG': 'C',
    'LC_ALL': 'C',
    'PAGER': 'cat',
    'TZ': 'UTC',
    'EDITOR': ':',
    'GIT_AUTHOR_EMAIL': 'author@example.com',
    'GIT_AUTHOR_NAME': '"A U Thor"',
    'GIT_COMMITTER_EMAIL': 'committer@example.com',
    'GIT_COMMITTER_NAME': '"C O Mitter"',
    'GIT_MERGE_VERBOSITY': '5',
    'GIT_MERGE_AUTOEDIT': 'no'
})

for key in ['XDF_CONFIG_HOME', 'GITPERLLIB', 'CDPATH', 
            'GREP_OPTIONS', 'UNZIP']:
    environment.pop(key, None)

    
git_lint_src = """
[pep8]
comment = PEP8 with some white space and line length checking turned off
output = Running pep8...
command = pep8 -r --ignore=E501,W293,W391
match = .py
print = False
condition = error
"""

# Basic TOX settings aren't good enough: we need to have something more or less guaranteed
# to not have a '.git' directory somewhere lurking in a parent folder.

class gittemp:
    def __enter__(self):
        self.cwd = os.getcwd()
        self.path = tempfile.mkdtemp()
        return self.path

    def __exit__(self, *args):
        os.chdir(self.cwd)
        shutil.rmtree(self.path)


def test_01_not_a_repository():
    with gittemp() as path:
        os.chdir(path)
        p = subprocess.Popen('git lint', shell=True, env=environment,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        assert stderr.startswith('A git repository was not found')


def test_02_empty_repository():
    with gittemp() as path:
        os.chdir(path)
        subprocess.check_call('git init', shell=True, env=environment)
        p = subprocess.Popen('git lint -l', shell=True, env=environment,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        assert stderr.startswith('No configuration file found,')


def test_03_simple_repository():
    with gittemp() as path:
        os.chdir(path)
        with open(".git-lint", "w") as f:
            f.write(git_lint_src)
        subprocess.check_call('git init', shell=True, env=environment)
        subprocess.check_call('git add .', shell=True, env=environment)
        subprocess.check_call('git commit -m "Test."', shell=True, env=environment)
        ret = subprocess.check_output('git lint -v', shell=True, env=environment)
        assert ret.index('Copyright') > 0

def test_04_linters_present():
    with gittemp() as path:
        os.chdir(path)
        with open(".git-lint", "w") as f:
            f.write(git_lint_src)
        subprocess.check_call('git init', shell=True, env=environment)
        subprocess.check_call('git add .', shell=True, env=environment)
        subprocess.check_call('git commit -m "Test."', shell=True, env=environment)
        ret = subprocess.check_output('git lint -l', shell=True, env=environment)
        assert len(ret.split("\n")) == 3
        assert ret.index('pep8') > 0

        
