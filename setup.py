#!/usr/bin/env python

from setuptools import find_packages, setup

import codecs


with codecs.open("README.rst", "r", "utf-8") as f:
    readme = f.read()
with codecs.open("HISTORY.rst", "r", "utf-8") as f:
    history = f.read()

setup(
    name="circonus",
    version="0.0.22",
    description="Interact with the Circonus REST API.",
    long_description=readme + "\n\n" + history,
    author="Monetate Inc.",
    author_email="kmolendyke@monetate.com",
    url="https://github.com/monetate/circonus",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7"
    ],
    keywords="circonus monitoring analytics",
    packages=find_packages(),
    install_requires=["colour", "requests"]
)
