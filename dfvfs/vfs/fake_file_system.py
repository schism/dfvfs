# -*- coding: utf-8 -*-
"""The fake file system implementation."""

from dfvfs.lib import date_time
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import fake_path_spec
from dfvfs.vfs import file_system
from dfvfs.vfs import fake_file_entry
from dfvfs.vfs import vfs_stat


class FakeFileSystem(file_system.FileSystem):
  """Class that implements a fake file system object."""

  LOCATION_ROOT = u'/'

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAKE

  def __init__(self, resolver_context):
    """Initializes the file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(FakeFileSystem, self).__init__(resolver_context)
    self._paths = {}

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    return

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification with parent.')

  def AddFileEntry(
      self, path, file_entry_type=definitions.FILE_ENTRY_TYPE_FILE,
      file_data=None, link_data=None):
    """Adds a fake file entry.

    Args:
      path: the path of the file entry.
      file_entry_type: optional type of the file entry object.
                       The default is file (definitions.FILE_ENTRY_TYPE_FILE).
      file_data: optional data of the fake file-like object.
                 The default is None.
      link_data: optional link data of the fake file entry object.
                 The default is None.

    Raises:
      KeyError: if the path already exists.
      ValueError: if the file data is set but the file entry type is not a file
                  or if the link data is set but the file entry type is not
                  a link.
    """
    if path in self._paths:
      raise KeyError(u'File entry already set for path: {0:s}.'.format(path))

    if file_data and file_entry_type != definitions.FILE_ENTRY_TYPE_FILE:
      raise ValueError(u'File data set for non-file file entry type.')

    if link_data and file_entry_type != definitions.FILE_ENTRY_TYPE_LINK:
      raise ValueError(u'Link data set for non-link file entry type.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    if file_data is not None:
      stat_object.size = len(file_data)

    # Date and time stat information.
    timestamp = date_time.PosixTimestamp.GetNow()

    stat_object.atime = timestamp
    stat_object.ctime = timestamp
    stat_object.mtime = timestamp

    # Ownership and permissions stat information.

    # File entry type stat information.
    stat_object.type = file_entry_type

    # Other stat information.

    if file_data:
      path_data = file_data
    elif link_data:
      path_data = link_data
    else:
      path_data = None

    self._paths[path] = (stat_object, path_data)

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    location = getattr(path_spec, 'location', None)

    if location is None or location not in self._paths:
      return False
    return True

  def GetDataByPath(self, path):
    """Retrieves the data associated to a path.

    Args:
      path: a path.

    Returns:
      Binary string containing the data or None if not available.
    """
    _, path_data = self._paths.get(path, (None, None))
    return path_data

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    location = getattr(path_spec, 'location', None)
    if location is None:
      return

    if (location != self.LOCATION_ROOT and
        not self.FileEntryExistsByPathSpec(path_spec)):
      return

    return fake_file_entry.FakeFileEntry(
        self._resolver_context, self, path_spec)

  def GetPaths(self):
    """Retrieves the paths dictionary.

    Returns:
      Dictionary containing the paths and the file-like objects.
    """
    return self._paths

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    path_spec = fake_path_spec.FakePathSpec(location=self.LOCATION_ROOT)
    return self.GetFileEntryByPathSpec(path_spec)

  def GetStatObjectByPath(self, path):
    """Retrieves the stat object for a path.

    Args:
      path: a path.

    Returns:
      The stat object (instance of vfs_stat.VFSStat).
    """
    stat_object, _ = self._paths.get(path, (None, None))
    return stat_object
