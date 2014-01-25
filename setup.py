# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Extension
from sixel import __version__, __license__, __author__
import inspect, os

filename = inspect.getfile(inspect.currentframe())
dirpath = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
long_description = open(os.path.join(dirpath, "README.rst")).read()


setup(name                  = 'PySixel',
      version               = __version__,
      description           = ('Make SIXEL color graphics supported by some '
                               'terminal emulators(DECTerm/RLogin/mlterm/tanasinn/xterm)'),
      long_description      = long_description,
      py_modules            = ['sixel'],
      ext_modules           = [Extension('sixel_cimpl', sources = ['sixel/sixel_cimpl.c'])],
      eager_resources       = [],
      classifiers           = ['Development Status :: 4 - Beta',
                               'Topic :: Terminals',
                               'Environment :: Console',
                               'Intended Audience :: End Users/Desktop',
                               'License :: OSI Approved :: GNU General Public License (GPL)',
                               'Programming Language :: Python'
                               ],
      keywords              = 'sixel terminal image',
      author                = __author__,
      author_email          = 'user@zuse.jp',
      url                   = 'https://github.com/saitoha/PySixel',
      license               = __license__,
      packages              = find_packages(exclude=[]),
      zip_safe              = False,
      include_package_data  = False,
      install_requires      = ['imageloader', 'Pillow'],
      entry_points          = """
                              [console_scripts]
                              sixelconv = sixel:main
                              """
      )

