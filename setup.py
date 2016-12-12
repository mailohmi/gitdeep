#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import gitdeep

setup(
        name             = 'gitdeep',
        version          = gitdeep.__version__,
        description      = gitdeep.__doc__.strip(),
        license          = gitdeep.__license__,
        author           = gitdeep.__author__,
        author_email     = 'mailohmi@gmail.com',
        url              = 'https://github.com/mailohmi/gitdeep.git',
        keywords         = 'git',
        packages         = find_packages(),
        install_requires = ['six'],
        scripts=['gitdeep/__main__.py'],
    )
