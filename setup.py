#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name="patroniser",
    version="0.3",
    description="Patreon Syncer",
    author="Thomas Lant",
    author_email="lampholder@gmail.com",
    packages=find_packages()
    # package_data={'': ['*.json', '*.csv', '*.yaml']},
    # scripts=['bin/report.py', 'bin/metrics.py']
)
