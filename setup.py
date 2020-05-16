#!/usr/bin/env python
from setuptools import setup

__version__ = '0.1'

setup(name = 'mealta',
      version = __version__,
      python_requires='>3.5.2',
      description = 'metabolic rate estimator',
      install_requires = ['numpy', 'matplotlib', 'h5py', 'pandas'],
      provides = ['mealta'],
      packages = ['mealta'],
      include_package_data=True, 
      package_data={'mealta': ['dat/*']}
      )
