import os
import sys

from setuptools import setup, find_packages, Command
from commands import *

tests_require=['pytest-cov', 'pytest', 'testfixtures']

setup(
    name=name,
    version=read_version(),
    description='Lazily evaluated function arguments',
    long_description=open(os.path.join(base_dir, 'description.txt')).read().strip(),
    license='MPL',
    url='https://github.com/chriscz/lazyargs',

    author='Chris Coetzee',
    author_email='chriscz93@gmail.com',
    license='Mozilla Public License 2.0 (MPL 2.0)',

    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=tests_require,

    include_package_data=True,
    zip_safe=False,

    cmdclass={
        'test': PyTestCommand,
        'coverage': CoverageCommand,
        'bump': BumpVersionCommand,
    },

    extras_require=dict(
        build=['twine', 'wheel', 'setuptools-git'],
        test=['pytest', 'testfixtures', 'pytest-cov'],
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Topic :: Utilities",
    ]
)
