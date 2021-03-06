#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the encoded stream path specification implementation."""

import unittest

from dfvfs.path import encoded_stream_path_spec
from tests.path import test_lib


class EncodedStreamPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the encoded stream path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = encoded_stream_path_spec.EncodedStreamPathSpec(
        encoding_method=u'test', parent=self._path_spec)

    self.assertNotEqual(path_spec, None)

    with self.assertRaises(ValueError):
      _ = encoded_stream_path_spec.EncodedStreamPathSpec(
          encoding_method=u'test', parent=None)

    with self.assertRaises(ValueError):
      _ = encoded_stream_path_spec.EncodedStreamPathSpec(
          encoding_method=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      _ = encoded_stream_path_spec.EncodedStreamPathSpec(
          encoding_method=u'test', parent=self._path_spec, bogus=u'BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = encoded_stream_path_spec.EncodedStreamPathSpec(
        encoding_method=u'test', parent=self._path_spec)

    self.assertNotEqual(path_spec, None)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: ENCODED_STREAM, encoding_method: test',
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
