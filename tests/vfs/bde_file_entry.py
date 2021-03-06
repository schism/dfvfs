#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using pybde."""

import os
import unittest

from dfvfs.path import bde_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.resolver import resolver
from dfvfs.vfs import bde_file_entry
from dfvfs.vfs import bde_file_system


class BdeFileEntryTest(unittest.TestCase):
  """The unit test for the BDE file entry object."""

  _BDE_PASSWORD = u'bde-TEST'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'bdetogo.raw')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._bde_path_spec = bde_path_spec.BdePathSpec(parent=path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._bde_path_spec, u'password', self._BDE_PASSWORD)

    self._file_system = bde_file_system.BdeFileSystem(self._resolver_context)
    self._file_system.Open(path_spec=self._bde_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = bde_file_entry.BdeFileEntry(
        self._resolver_context, self._file_system, self._bde_path_spec)
    self.assertNotEqual(file_entry, None)

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._bde_path_spec)
    self.assertNotEqual(file_entry, None)

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._bde_path_spec)
    self.assertNotEqual(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertEqual(parent_file_entry, None)

  def testGetStat(self):
    """Test the get stat functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._bde_path_spec)
    self.assertNotEqual(file_entry, None)

    stat_object = file_entry.GetStat()
    self.assertNotEqual(stat_object, None)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)

  def testIsFunctions(self):
    """Test the Is? functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._bde_path_spec)
    self.assertNotEqual(file_entry, None)

    self.assertTrue(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._bde_path_spec)
    self.assertNotEqual(file_entry, None)

    self.assertEqual(file_entry.number_of_sub_file_entries, 0)

    expected_sub_file_entry_names = []

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), expected_sub_file_entry_names)


if __name__ == '__main__':
  unittest.main()
