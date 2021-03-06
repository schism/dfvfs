# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) file entry object interface.

The file entry can be various file system elements like a regular file,
a directory or file system metadata.
"""

import abc

from dfvfs.resolver import resolver


class Directory(object):
  """Class that implements the VFS directory object interface."""

  def __init__(self, file_system, path_spec):
    """Initializes the directory object.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification object (instance of path.PathSpec).
    """
    super(Directory, self).__init__()
    self._entries = None
    self._file_system = file_system
    self.path_spec = path_spec

  @abc.abstractmethod
  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of path.PathSpec).
    """

  @property
  def entries(self):
    """The entries (generator of instance of path.OSPathSpec)."""
    for entry in self._EntriesGenerator():
      yield entry


class FileEntry(object):
  """Class that implements the VFS file entry object interface."""

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification object (instance of path.PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
               The default is False.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system. The default is False.
    """
    super(FileEntry, self).__init__()
    self._directory = None
    self._file_system = file_system
    self._is_root = is_root
    self._is_virtual = is_virtual
    self._resolver_context = resolver_context
    self._stat_object = None
    self.path_spec = path_spec

    self._file_system.Open(path_spec=path_spec)

  def __del__(self):
    """Cleans up the file entry object."""
    self._file_system.Close()

  @abc.abstractmethod
  def _GetDirectory(self):
    """Retrieves the directory object (instance of vfs.Directory)."""

  @abc.abstractmethod
  def _GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""

  @property
  def link(self):
    """The full path of the linked file entry."""
    return u''

  @abc.abstractproperty
  def name(self):
    """The name of the file entry, which does not include the full path."""

  @property
  def number_of_sub_file_entries(self):
    """The number of sub file entries."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory is None:
      return 0

    # We cannot use len(self._directory.entries) since entries is a generator.
    return sum(1 for path_spec in self._directory.entries)

  @abc.abstractproperty
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""

  @property
  def type_indicator(self):
    """The type indicator."""
    type_indicator = getattr(self, u'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          u'Invalid file system missing type indicator.')
    return type_indicator

  def GetFileObject(self):
    """Retrieves the file-like object (instance of file_io.FileIO)."""
    return resolver.Resolver.OpenFileObject(
        self.path_spec, resolver_context=self._resolver_context)

  def GetFileSystem(self):
    """Retrieves the file system (instance of vfs.FileSystem)."""
    return self._file_system

  def GetLinkedFileEntry(self):
    """Retrieves the linked file entry, e.g. for a symbolic link."""
    return

  @abc.abstractmethod
  def GetParentFileEntry(self):
    """Retrieves the parent file entry."""

  def GetSubFileEntryByName(self, name, case_sensitive=True):
    """Retrieves a sub file entry by name."""
    name_lower = name.lower()
    matching_sub_file_entry = None

    for sub_file_entry in self.sub_file_entries:
      if sub_file_entry.name == name:
        return sub_file_entry

      if not case_sensitive and sub_file_entry.name.lower() == name_lower:
        if not matching_sub_file_entry:
          matching_sub_file_entry = sub_file_entry

    return matching_sub_file_entry

  def GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()
    return self._stat_object

  def IsAllocated(self):
    """Determines if the file entry is allocated."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()
    return self._stat_object.is_allocated

  def IsDevice(self):
    """Determines if the file entry is a device."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()
    return self._stat_object.type == self._stat_object.TYPE_DEVICE

  def IsDirectory(self):
    """Determines if the file entry is a directory."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()
    return self._stat_object.type == self._stat_object.TYPE_DIRECTORY

  def IsFile(self):
    """Determines if the file entry is a file."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()
    return self._stat_object.type == self._stat_object.TYPE_FILE

  def IsLink(self):
    """Determines if the file entry is a link."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()
    return self._stat_object.type == self._stat_object.TYPE_LINK

  def IsPipe(self):
    """Determines if the file entry is a pipe."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()
    return self._stat_object.type == self._stat_object.TYPE_PIPE

  def IsRoot(self):
    """Determines if the file entry is the root file entry."""
    return self._is_root

  def IsSocket(self):
    """Determines if the file entry is a socket."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()
    return self._stat_object.type == self._stat_object.TYPE_SOCKET

  def IsVirtual(self):
    """Determines if the file entry is virtual (emulated by dfVFS)."""
    return self._is_virtual
