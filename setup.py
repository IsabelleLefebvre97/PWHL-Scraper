#!/usr/bin/env python
"""
Setup script for the pwhl-scraper package.
"""
from setuptools import setup, find_packages
import os
import re


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


def get_version():
    """Extract version from __init__.py"""
    init_py = read('pwhl_scraper/__init__.py')
    return re.search(r"__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_requirements():
    """Get requirements from requirements.txt"""
    try:
        with open('requirements.txt') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []


setup(
    name="PWHL-Scraper",
    version=get_version(),
    description="Data scraper and API for PWHL (Professional Women's Hockey League) statistics",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    author="Isabelle Lefebvre",
    author_email="ilefe071@gmail.com",
    url="https://github.com/IsabelleLefebvre97/pwhl-scraper",
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_requirements(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        'console_scripts': [
            'pwhl-scraper=pwhl_scraper.cli:main',
        ],
    },
    python_requires=">=3.6",
)
