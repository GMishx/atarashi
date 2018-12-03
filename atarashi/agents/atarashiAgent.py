#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2018 Gaurav Mishra <gmishx@gmail.com>

SPDX-License-Identifier: GPL-2.0

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
version 2 as published by the Free Software Foundation.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

__author__ = "Gaurav Mishra"
__email__ = "gmishx@gmail.com"

from abc import ABCMeta, abstractmethod
from functools import partial
from multiprocessing import Pool as ThreadPool
import os

from atarashi.libs.commentPreprocessor import CommentPreprocessor
from atarashi.license.licenseLoader import LicenseLoader


class AtarashiAgent(object):
  __metaclass__ = ABCMeta

  def __init__(self, licenseList, verbose=0):
    if isinstance(licenseList, str):
      self.licenseList = LicenseLoader.fetch_licenses(licenseList)
    else:
      self.licenseList = licenseList
    if 'processed_text' not in self.licenseList.columns:
      raise ValueError('The license list does not contain processed_text column.')
    self.verbose = verbose
    self.threads = os.cpu_count() * 2
    self.exactMatchData = [[x.shortname, x.processed_text] for x in self.licenseList.itertuples(False)]

  def loadFile(self, filePath):
    self.commentFile = CommentPreprocessor.extract(filePath)
    with open(self.commentFile) as file:
      data = file.read().replace('\n', ' ')
    return CommentPreprocessor.preprocess(data)

  def getVerbose(self):
    return self.verbose

  def setVerbose(self, verbose):
    self.verbose = int(verbose)

  @abstractmethod
  def scan(self, filePath):
    pass

  def exactMatcher(self, licenseText):
    '''
    :param licenseText: Processed and extracted input text
    :return: License short name if exact match is found else -1 if no match
    '''
    output = []

    with ThreadPool(self.threads) as pool:
      func = partial(self.__matchExactLicenseText, licenseText)
      for match in pool.imap(func,
                             self.exactMatchData,
                             int(len(self.exactMatchData)/self.threads)):
        if match is not None:
          output.append(match)

    if not output:
      return -1
    return output

  def __matchExactLicenseText(self, licenseText, licenseRow):
    '''
    Helper function for exactMatcher to check if licenseText exists in
    processed_text of given licenseRow.
    :param licenseText: Text to check
    :param licenseRow: List of [shortname, processed_text]
    :return: License shortname if found, None otherwise
    '''
    if licenseRow[0] !=  'Void' and licenseRow[1] in licenseText:
      return licenseRow[0]
    else:
      return None
