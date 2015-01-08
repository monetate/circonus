#!/usr/bin/env python

from setuptools import find_packages, setup

import circonus


packages = ["circonus"]

setup(
    name="circonus",
    version=circonus.__version__,
    description="Interact with the Circonus REST API.",
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
    install_requires=["requests"]
)
