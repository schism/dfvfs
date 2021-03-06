# -*- coding: utf-8 -*-
"""Functionality to check for the availability and version of dependencies."""

import re
import urllib2


# The dictionary values are:
# module_name: minimum_version
LIBYAL_DEPENDENCIES = {
    u'pybde': 20140531,
    u'pyewf': 20131210,
    u'pyqcow': 20131204,
    u'pysigscan': 20150114,
    u'pysmdev': 20140428,
    u'pysmraw': 20140612,
    u'pyvhdi': 20131210,
    u'pyvmdk': 20140421,
    u'pyvshadow': 20131209}

# The tuple values are:
# module_name, version_attribute_name, minimum_version, maximum_version
PYTHON_DEPENDENCIES = [
    (u'construct', u'__version__', u'2.5.2', None),
    (u'google.protobuf', u'', u'', None),
    (u'six', u'__version__', u'1.1.0', None),
    (u'sqlite3', u'sqlite_version', u'3.7.8', None)]


def DownloadPageContent(download_url):
  """Downloads the page content.

  Args:
    download_url: the URL where to download the page content.

  Returns:
    The page content if successful, None otherwise.
  """
  if not download_url:
    return

  url_object = urllib2.urlopen(download_url)

  if url_object.code != 200:
    return

  return url_object.read()


def GetLibyalGithubReleasesLatestVersion(library_name):
  """Retrieves the latest version number of a libyal library on GitHub releases.

  Args:
    library_name: the name of the libyal library.

  Returns:
    The latest version for a given libyal library on GitHub releases
    or 0 on error.
  """
  download_url = (
      u'https://github.com/libyal/{0:s}/releases').format(library_name)

  page_content = DownloadPageContent(download_url)
  if not page_content:
    return 0

  # The format of the project download URL is:
  # /libyal/{project name}/releases/download/{git tag}/
  # {project name}{status-}{version}.tar.gz
  # Note that the status is optional and will be: beta, alpha or experimental.
  expression_string = (
      u'/libyal/{0:s}/releases/download/[^/]*/{0:s}-[a-z-]*([0-9]+)'
      u'[.]tar[.]gz').format(library_name)
  matches = re.findall(expression_string, page_content)

  if not matches:
    return 0

  return int(max(matches))


# TODO: Remove when Google Drive support is no longer needed.
def GetLibyalGoogleDriveLatestVersion(library_name):
  """Retrieves the latest version number of a libyal library on Google Drive.

  Args:
    library_name: the name of the libyal library.

  Returns:
    The latest version for a given libyal library on Google Drive
    or 0 on error.
  """
  download_url = u'https://code.google.com/p/{0:s}/'.format(library_name)

  page_content = DownloadPageContent(download_url)
  if not page_content:
    return 0

  # The format of the library downloads URL is:
  # https://googledrive.com/host/{random string}/
  expression_string = (
      b'<a href="(https://googledrive.com/host/[^/]*/)"[^>]*>Downloads</a>')
  matches = re.findall(expression_string, page_content)

  if not matches or len(matches) != 1:
    return 0

  page_content = DownloadPageContent(matches[0])
  if not page_content:
    return 0

  # The format of the library download URL is:
  # /host/{random string}/{library name}-{status-}{version}.tar.gz
  # Note that the status is optional and will be: beta, alpha or experimental.
  expression_string = b'/host/[^/]*/{0:s}-[a-z-]*([0-9]+)[.]tar[.]gz'.format(
      library_name)
  matches = re.findall(expression_string, page_content)

  if not matches:
    return 0

  return int(max(matches))


def CheckLibyal(libyal_python_modules, latest_version_check=False):
  """Checks the availability of libyal libraries.

  Args:
    libyal_python_modules: a dictionary of libyal python module name as
                           the key and version as the value.
    latest_version_check: optional boolean value to indicate if the project
                          site should be checked for the latest version.
                          The default is False.

  Returns:
    True if the libyal libraries are available, False otherwise.
  """
  connection_error = False
  result = True
  for module_name, module_version in sorted(libyal_python_modules.items()):
    try:
      module_object = map(__import__, [module_name])[0]
    except ImportError:
      print u'[FAILURE]\tmissing: {0:s}.'.format(module_name)
      result = False
      continue

    libyal_name = u'lib{0:s}'.format(module_name[2:])

    installed_version = int(module_object.get_version())

    latest_version = None
    if latest_version_check:
      try:
        latest_version = GetLibyalGithubReleasesLatestVersion(libyal_name)
      except urllib2.URLError:
        latest_version = None

      if not latest_version:
        try:
          latest_version = GetLibyalGoogleDriveLatestVersion(libyal_name)
        except urllib2.URLError:
          latest_version = None

      if not latest_version:
        print (
            u'Unable to determine latest version of {0:s} ({1:s}).\n').format(
                libyal_name, module_name)
        latest_version = None
        connection_error = True

    if module_version is not None and installed_version < module_version:
      print (
          u'[FAILURE]\t{0:s} ({1:s}) version: {2:d} is too old, {3:d} or '
          u'later required.').format(
              libyal_name, module_name, installed_version, module_version)
      result = False

    elif latest_version and installed_version != latest_version:
      print (
          u'[INFO]\t\t{0:s} ({1:s}) version: {2:d} installed, '
          u'version: {3:d} available.').format(
              libyal_name, module_name, installed_version, latest_version)

    else:
      print u'[OK]\t\t{0:s} ({1:s}) version: {2:d}'.format(
          libyal_name, module_name, installed_version)

  if connection_error:
    print (
        u'[INFO] to check for the latest versions this script needs Internet '
        u'access.')

  return result


def CheckPythonModule(
    module_name, version_attribute_name, minimum_version,
    maximum_version=None):
  """Checks the availability of a Python module.

  Args:
    module_name: the name of the module.
    version_attribute_name: the name of the attribute that contains the module
                            version.
    minimum_version: the minimum required version.
    maximum_version: the maximum required version. This attribute is optional
                     and should only be used if there is a recent API change
                     that prevents the tool from running if a later version
                     is used.

  Returns:
    True if the Python module is available and conforms to the minimum required
    version. False otherwise.
  """
  try:
    module_object = map(__import__, [module_name])[0]
  except ImportError:
    print u'[FAILURE]\tmissing: {0:s}.'.format(module_name)
    return False

  if version_attribute_name and minimum_version:
    module_version = getattr(module_object, version_attribute_name, None)

    if not module_version:
      return False

    # Split the version string and convert every digit into an integer.
    # A string compare of both version strings will yield an incorrect result.
    split_regex = re.compile(r'\.|\-')
    module_version_map = map(int, split_regex.split(module_version))
    minimum_version_map = map(int, split_regex.split(minimum_version))

    if module_version_map < minimum_version_map:
      print (
          u'[FAILURE]\t{0:s} version: {1:s} is too old, {2:s} or later '
          u'required.').format(module_name, module_version, minimum_version)
      return False

    if maximum_version:
      maximum_version_map = map(int, split_regex.split(maximum_version))
      if module_version_map > maximum_version_map:
        print (
            u'[FAILURE]\t{0:s} version: {1:s} is too recent, {2:s} or earlier '
            u'required.').format(module_name, module_version, maximum_version)
        return False

    print u'[OK]\t\t{0:s} version: {1:s}'.format(module_name, module_version)
  else:
    print u'[OK]\t\t{0:s}'.format(module_name)

  return True


def CheckPytsk(module_name, minimum_version_libtsk, minimum_version_pytsk):
  """Checks the availability of pytsk.

  Args:
    module_name: the name of the module.
    minimum_version_libtsk: the minimum required version of libtsk.
    minimum_version_pytsk: the minimum required version of pytsk.

  Returns:
    True if the pytsk Python module is available, False otherwise.
  """
  try:
    module_object = map(__import__, [module_name])[0]
  except ImportError:
    print u'[FAILURE]\tmissing: {0:s}.'.format(module_name)
    return False

  module_version = module_object.TSK_VERSION_STR

  # Split the version string and convert every digit into an integer.
  # A string compare of both version strings will yield an incorrect result.
  module_version_map = map(int, module_version.split(u'.'))
  minimum_version_map = map(int, minimum_version_libtsk.split(u'.'))
  if module_version_map < minimum_version_map:
    print (
        u'[FAILURE]\tSleuthKit (libtsk) version: {0:s} is too old, {1:s} or '
        u'later required.').format(module_version, minimum_version_libtsk)
    return False

  print u'[OK]\t\tSleuthKit version: {0:s}'.format(module_version)

  if not hasattr(module_object, u'get_version'):
    print u'[FAILURE]\t{0:s} is too old, {1:s} or later required.'.format(
        module_name, minimum_version_pytsk)
    return False

  module_version = module_object.get_version()
  if module_version < minimum_version_pytsk:
    print (
        u'[FAILURE]\t{0:s} version: {1:s} is too old, {2:s} or later '
        u'required.').format(
            module_name, module_version, minimum_version_pytsk)
    return False

  print u'[OK]\t\t{0:s} version: {1:s}'.format(module_name, module_version)

  return True


def CheckDependencies(latest_version_check=False):
  """Checks the availability of the dependencies.

  Args:
    latest_version_check: Optional boolean value to indicate if the project
                          site should be checked for the latest version.
                          The default is False.

  Returns:
    True if the dependencies are available, False otherwise.
  """
  print u'Checking availability and versions of dfvfs dependencies.'
  check_result = True

  for values in PYTHON_DEPENDENCIES:
    if not CheckPythonModule(
        values[0], values[1], values[2], maximum_version=values[3]):
      check_result = False

  if not CheckPytsk(u'pytsk3', u'4.1.2', u'20140506'):
    check_result = False

  libyal_check_result = CheckLibyal(
      LIBYAL_DEPENDENCIES, latest_version_check=latest_version_check)

  if not libyal_check_result:
    check_result = False

  print u''
  return check_result


def GetInstallRequires():
  """Returns the install_requires for setup.py"""
  install_requires = []
  for values in PYTHON_DEPENDENCIES:
    module_name = values[0]
    module_version = values[2]

    # Map the import name to the pypi name.
    if module_name == u'sqlite3':
      # Override the pysqlite version since it does not match
      # the sqlite3 version.
      module_name = u'pysqlite'
      module_version = None

    if not module_version:
      install_requires.append(module_name)
    else:
      install_requires.append(u'{0:s} >= {1:s}'.format(
          module_name, module_version))

  install_requires.append(u'pytsk3 >= 4.1.2')

  for module_name, module_version in sorted(LIBYAL_DEPENDENCIES.items()):
    if not module_version:
      install_requires.append(module_name)
    else:
      install_requires.append(u'{0:s} >= {1:d}'.format(
          module_name, module_version))

  return sorted(install_requires)
