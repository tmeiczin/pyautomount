#!/usr/bin/env python

from setuptools import setup, find_packages
from subprocess import Popen, PIPE

setup(
    name='pyautomount',
    version='1.0.0',
    author=['Terrence Meiczinger'],
    author_email='terrence72@gmail.com',
    license='LICENSE',
    url='https://github.com/tmeiczin/pyautomount',
    download_url='https://github.com/tmeiczin/pydhcp',
    description='Python Auto Mounter',
    long_description=open('README.md').read(),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=False,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    install_requires=[
        'pyudev',
    ],
    entry_points={
        'console_scripts': [
            'pyautomounter = pyautomount.__main__:main'
        ],
    },
)
