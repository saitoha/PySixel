# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from sixel import __version__, __license__, __author__

setup(name                  = 'PySixel',
      version               = __version__,
      description           = 'Make SIXEL color graphics supported by some terminal emulators(RLogin/mlterm/tanasinn)',
      long_description      = open("README.rst").read(),
      py_modules            = ['sixel'],
      eager_resources       = [],
      classifiers           = ['Development Status :: 4 - Beta',
                               'Topic :: Terminals',
                               'Environment :: Console',
                               'Intended Audience :: End Users/Desktop',
                               'License :: OSI Approved :: GNU General Public License (GPL)',
                               'Programming Language :: Python'
                               ],
      keywords              = 'sixel terminal',
      author                = __author__,
      author_email          = 'user@zuse.jp',
      url                   = 'https://github.com/saitoha/PySixel',
      license               = __license__,
      packages              = find_packages(exclude=[]),
      zip_safe              = True,
      include_package_data  = False,
      install_requires      = ['PIL'],
      entry_points          = """
                              [console_scripts]
                              sixelconv = sixel:main
                              """
      )

