# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='patroniser',
    version='0.3',
    description='Patreon Syncer',
    author='Thomas Lant',
    author_email='lampholder@gmail.com',
    packages=find_packages()
    #package_data={'': ['*.json', '*.csv', '*.yaml']},
    #scripts=['bin/report.py', 'bin/metrics.py']
)
