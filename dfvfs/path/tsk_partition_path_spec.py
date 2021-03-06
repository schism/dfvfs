# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) partition path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class TSKPartitionPathSpec(path_spec.PathSpec):
  """Class that implements the SleuthKit (TSK) partition path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK_PARTITION

  def __init__(
      self, location=None, part_index=None, start_offset=None, parent=None,
      **kwargs):
    """Initializes the path specification object.

       Note that the TSK partition path specification must have a parent.

    Args:
      location: optional location string. The default is None.
      part_index: optional part index. The default is None.
      start_offset: optional start offset. The default is None.
      parent: optional parent path specification (instance of PathSpec).
              The default is None.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(TSKPartitionPathSpec, self).__init__(parent=parent, **kwargs)
    self.location = location
    self.part_index = part_index
    self.start_offset = start_offset

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    string_parts = []

    if self.location is not None:
      string_parts.append(u'location: {0:s}'.format(self.location))
    if self.part_index is not None:
      string_parts.append(u'part index: {0:d}'.format(self.part_index))
    if self.start_offset is not None:
      string_parts.append(u'start offset: 0x{0:08x}'.format(self.start_offset))

    return self._GetComparable(sub_comparable_string=u', '.join(string_parts))


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(TSKPartitionPathSpec)
