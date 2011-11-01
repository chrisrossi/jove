##############################################################################
#
# Copyright (c) 2008-2011 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os
import platform
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires=[
    'argparse',
    'colander',
    'mock',
    'pyramid_tm',
    'pyramid_zodbconn',
    'repoze.retry',
    ]

tests_require = install_requires + ['WebTest']
if sys.version_info[:2] < (2, 7):
    tests_require.append('unittest2')

setup(name='jove',
      version='0.1a1',
      description=('A site manager for ZODB based Pyramid applications.'),
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: Repoze Public License",
        ],
      keywords='web wsgi pylons pyramid zodb',
      author="Chris Rossi, Archimedean Company",
      author_email="pylons-devel@googlegroups.com",
      url="http://pylonsproject.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = install_requires,
      tests_require = tests_require,
      test_suite="jove.tests",
      entry_points = """\
          [paste.app_factory]
          main = jove.application:make_app

          [console_scripts]
          jove = jove.scripts.main:main

          [jove.application]
          test_app = jove.tests.test_functional:TestApplication

          [jove.local_service]
          test_local_service = jove.tests.test_functional:TestLocalService
          evolution = jove.services.evolution:EvolutionService

          [jove.script]
          debug = jove.scripts.debug:config_parser
          serve = jove.scripts.serve:config_parser
          settings = jove.scripts.settings:config_parser
      """
      )

