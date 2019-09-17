#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst

import sys

import glob
import os

import ah_bootstrap  # noqa
from setuptools import setup

import builtins
builtins._ASTROPY_SETUP_ = True

from astropy_helpers.setup_helpers import register_commands, get_package_info
from astropy_helpers.git_helpers import get_git_devstr
from astropy_helpers.version_helpers import generate_version_py

# Get some values from the setup.cfg
from configparser import ConfigParser

conf = ConfigParser()

conf.read(['setup.cfg'])
metadata = dict(conf.items('metadata'))

PACKAGENAME = metadata.get('name', 'ginga')

# Get the long description from the package's docstring
__import__(PACKAGENAME)
package = sys.modules[PACKAGENAME]
LONG_DESCRIPTION = package.__doc__

# Store the package name in a built-in variable so it's easy
# to get from other parts of the setup infrastructure
builtins._ASTROPY_PACKAGE_NAME_ = PACKAGENAME

# VERSION should be PEP386 compatible (http://www.python.org/dev/peps/pep-0386)
VERSION = metadata.get('version', '0.0.dev')

# Indicates if this version is a release version
RELEASE = 'dev' not in VERSION

if not RELEASE:
    VERSION += get_git_devstr(False)

# Populate the dict of setup command overrides; this should be done before
# invoking any other functionality from distutils since it can potentially
# modify distutils' behavior.
cmdclassd = register_commands()

# Freeze build information in version.py
generate_version_py()

# Treat everything in scripts except README.rst and fits2pdf.py
# as a script to be installed
scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
           if (os.path.basename(fname) != 'README.rst' and
               os.path.basename(fname) != 'fits2pdf.py')]

# Get configuration information from all of the various subpackages.
# See the docstring for setup_helpers.update_package_files for more
# details.
package_info = get_package_info()

# Add the project-global data
package_info['package_data'].setdefault(PACKAGENAME, [])
package_info['package_data'][PACKAGENAME].append('examples/*/*')
package_info['package_data'][PACKAGENAME].append('web/pgw/js/*.js')
package_info['package_data'][PACKAGENAME].append('web/pgw/js/*.css')

# Define entry points for command-line scripts
entry_points = {'console_scripts': []}

entry_point_list = conf.items('entry_points')
for entry_point in entry_point_list:
    entry_points['console_scripts'].append('{0} = {1}'.format(entry_point[0],
                                                              entry_point[1]))

# Include all .c files, recursively, including those generated by
# Cython, since we can not do this in MANIFEST.in with a "dynamic"
# directory name.
c_files = []
for root, dirs, files in os.walk(PACKAGENAME):
    for filename in files:
        if filename.endswith('.c'):
            c_files.append(
                os.path.join(
                    os.path.relpath(root, PACKAGENAME), filename))
package_info['package_data'][PACKAGENAME].extend(c_files)

setup(version=VERSION,
      scripts=scripts,
      long_description=LONG_DESCRIPTION,
      cmdclass=cmdclassd,
      entry_points=entry_points,
      **package_info)
