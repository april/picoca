#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = [
    "cryptography",
]
setup_requirements = ["pytest-runner"]
test_requirements = [
    "flake8",
    "pytest",
]
extras = {
    "test": test_requirements,
}

setup(
    name="picoca",
    description="PicoCA is a simple CA intended for use for education and self-hosting purposes",
    author="April King",
    author_email="april@pokeinthe.io",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Security :: Cryptography",
    ],
    entry_points={"console_scripts": ["picoca=picoca.main:main"]},
    include_package_data=True,
    install_requires=requirements,
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords="picoca PicoCA certificate authority",
    packages=find_packages(include=["picoca"]),
    test_suite="tests",
    tests_require=test_requirements,
    extras_require=extras,
    url="https://github.com/april/picoca",
    version="1.0.0",
    zip_safe=False,
)
