#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
        name             = 'gitdeep',
        version          = "1.0.6",
        description      = "下位ディレクトリを含めてgitを実行します。",
        license          = "MIT",
        author           = "Kazuyuki OHMI",
        author_email     = 'mailohmi@gmail.com',
        url              = 'https://github.com/mailohmi/gitdeep.git',
        keywords         = 'git',
        packages         = find_packages(),
        install_requires = ['six'],
        entry_points={
            'console_scripts': [
                'gitdeep = gitdeep.gitdeep:main'
            ]
        }
    )
