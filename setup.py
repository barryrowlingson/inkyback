from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name="InkyBack",
      version="0.92",
      description="Incremental backups in python",
      author="Barry Rowlingson",
      author_email="barry.rowlingson@gmail.com",
      packages=find_packages(exclude='tests'),
      install_requires=[],
      entry_points = {
    'console_scripts':[
    'inkyback=inkyback.backup:main',
    'inkyprune=inkyback.pruning:main',
    ]
    }
      )
    
    
