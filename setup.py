#! /usr/bin/env python

from setuptools import setup

setup(
    name='cloudforge',
    version='0.0.1',
    packages=['cloudforge'],
    url='http://github.com/TronPaul/cloudforge',
    license='Apache-2.0',
    author='Mark McGuire',
    author_email='mark.b.mcg@gmail.com',
    description='',
    install_requires=['boto', 'jinja2', 'PyYAML', 'mock'],
    entry_points={
        'console_scripts': ['cloudforge=cloudforge.cli:cloudforge']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Environment :: Console'
    ]
)
