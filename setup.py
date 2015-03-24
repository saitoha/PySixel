# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Extension
from sixel import __version__, __license__, __author__
import inspect, os

filename = inspect.getfile(inspect.currentframe())
dirpath = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
long_description = open(os.path.join(dirpath, "README.rst")).read()

extra_args = []

if os.uname()[0] == 'Darwin':
    # Clang no longer supports GCC arguments, and will fail in the future
    extra_args.append('-Wno-error=unused-command-line-argument-hard-error-in-future')

setup(name                  = 'PySixel',
      version               = __version__,
      description           = ('View full-pixel color graphics on SIXEL-supported terminals'
                               '(xterm/mlterm/DECterm/Reflection/RLogin/tanasinn/yaft)'),
      long_description      = long_description,
      py_modules            = ['sixel'],
      ext_modules           = [Extension('sixel_cimpl', sources = ['sixel/sixel_cimpl.c'], extra_compile_args = extra_args)],
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

