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

    
class TestGit_lint(object):

    @classmethod
    def setup_class(cls):
        if os.path.exists('t'):
            shutil.rmtree('t')
        os.mkdir('t')
        shutil.copy('.git-lint', 't')
        os.chdir('t')
        subprocess.check_output('git init', shell=True, env=environment)


    def test_itruns(self):
        ret = subprocess.check_output('git lint -v', shell=True, env=environment)
        assert ret.startswith('git-lint')

    @classmethod
    def teardown_class(cls):
        os.chdir('..')
        shutil.rmtree('t')

