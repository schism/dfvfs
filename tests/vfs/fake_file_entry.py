#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the fake file entry implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_entry
from dfvfs.vfs import fake_file_system


class FakeFileEntryTest(unittest.TestCase):
  """The unit test for the fake file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    self._file_system = fake_file_system.FakeFileSystem(self._resolver_context)

    self._file_system.AddFileEntry(
        u'/test_data/testdir_fake',
        file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)
    self._file_system.AddFileEntry(
        u'/test_data/testdir_fake/file1.txt', file_data='FILE1')
    self._file_system.AddFileEntry(
        u'/test_data/testdir_fake/file2.txt', file_data='FILE2')
    self._file_system.AddFileEntry(
        u'/test_data/testdir_fake/file3.txt', file_data='FILE3')
    self._file_system.AddFileEntry(
        u'/test_data/testdir_fake/file4.txt', file_data='FILE4')
    self._file_system.AddFileEntry(
        u'/test_data/testdir_fake/file5.txt', file_data='FILE5')

    self._file_system.AddFileEntry(
        u'/test_data/testdir_fake/link1.txt',
        file_entry_type=definitions.FILE_ENTRY_TYPE_LINK,
        link_data=u'/test_data/testdir_fake/file1.txt')

    self._test_file = u'/test_data/testdir_fake'

    self._fake_path_spec = fake_path_spec.FakePathSpec(location=u'/')
    self._file_system.Open(path_spec=self._fake_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testIntialize(self):
    """Test the initialize functionality."""
    path_spec = fake_path_spec.FakePathSpec(location=self._test_file)
    file_entry = fake_file_entry.FakeFileEntry(
        self._resolver_context, self._file_system, path_spec)

    self.assertNotEqual(file_entry, None)

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    path_spec = fake_path_spec.FakePathSpec(location=self._test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEqual(file_entry, None)

  def testGetFileObject(self):
    """Test the get file object functionality."""
    test_file = u'/test_data/testdir_fake/file1.txt'
    path_spec = fake_path_spec.FakePathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    file_object = file_entry.GetFileObject()

    self.assertNotEqual(file_object, None)

    file_data = file_object.read()
    self.assertEqual(file_data, 'FILE1')

    file_object.close()

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    test_file = u'/test_data/testdir_fake/file1.txt'
    path_spec = fake_path_spec.FakePathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEqual(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertNotEqual(parent_file_entry, None)

    self.assertEqual(parent_file_entry.name, u'testdir_fake')

  def testGetStat(self):
    """Test the get stat functionality."""
    test_file = u'/test_data/testdir_fake/file1.txt'
    path_spec = fake_path_spec.FakePathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    stat_object = file_entry.GetStat()

    self.assertNotEqual(stat_object, None)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)

  def testIsFunctions(self):
    """Test the Is? functionality."""
    test_file = u'/test_data/testdir_fake/file1.txt'
    path_spec = fake_path_spec.FakePathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertFalse(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

    test_file = u'/test_data/testdir_fake'
    path_spec = fake_path_spec.FakePathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertFalse(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertTrue(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

    test_file = u'/test_data/testdir_fake/link1.txt'
    path_spec = fake_path_spec.FakePathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertFalse(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertTrue(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testLink(self):
    """Test the link property functionality."""
    test_file = u'/test_data/testdir_fake/link1.txt'
    path_spec = fake_path_spec.FakePathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertEqual(file_entry.link, u'/test_data/testdir_fake/file1.txt')

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    path_spec = fake_path_spec.FakePathSpec(location=self._test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEqual(file_entry, None)

    self.assertEqual(file_entry.number_of_sub_file_entries, 6)

    expected_sub_file_entry_names = [
        u'file1.txt', u'file2.txt', u'file3.txt', u'file4.txt', u'file5.txt',
        u'link1.txt']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), expected_sub_file_entry_names)


if __name__ == '__main__':
  unittest.main()
