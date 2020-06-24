"""QSCOUT Gate Models"""

import sys
from setuptools import setup

name = "QSCOUT-gatemodels"
description = "QSCOUT Gate Models"
version = "1.0"

setup(
    name=name,
    description=description,
    version=version,
    author="Benjamin C. A. Morrison, Jay Wesley Van Der Wall, Daniel Lobser, Antonio Russo, Kenneth Rudinger, Peter Maunz",
    author_email="qscout@sandia.gov",
    packages=["qscout", "qscout.v1",],
    package_dir={"": "."},
    install_requires=["JaqalPaq", "numpy"],
    extras_require={"tests": ["pytest"],},
    python_requires=">=3.6",
    platforms=["any"],
    url="https://qscout.sandia.gov",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Physics",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Unix",
    ],
)
