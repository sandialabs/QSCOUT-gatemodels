"""QSCOUT Gate Pulse File"""

import sys
from setuptools import setup

try:
    from sphinx.setup_command import BuildDoc
except ImportError:
    print("Warning: document cannot be built without sphinx")
    BuildDoc = None

name = "qscout-gpf"
description = "QSCOUT Gate Pulse File"
version = "1.0"

setup(
    name=name,
    description=description,
    version=version,
    author="Benjamin C. A. Morrison, Jay Wesley Van Der Wall, Lobser, Daniel, Antonio Russo, Kenneth Rudinger, Peter Maunz",
    author_email="qscout@sandia.gov",
    packages=["qscout", "qscout.gate_pulse",],
    package_dir={"": "."},
    install_requires=["JaqalPaq", "numpy"],
    extras_require={"tests": ["pytest"], "docs": ["sphinx"]},
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
    cmdclass={"build_sphinx": BuildDoc},
)
