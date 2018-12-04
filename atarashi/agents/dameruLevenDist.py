#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2018 Aman Jain (amanjain5221@gmail.com)

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

import argparse
from functools import partial
from multiprocessing import Pool as ThreadPool
from pyxdameraulevenshtein import damerau_levenshtein_distance
import sys

from atarashi.agents.atarashiAgent import AtarashiAgent


__author__ = "Aman Jain"
__email__ = "amanjain5221@gmail.com"


class DameruLevenDist(AtarashiAgent):

  def scan(self, filePath):
    '''
    Read the content content of filename, extract the comments and preprocess them.
    Find the Damerau Levenshtein distance between the preprocessed file content
    and the license text.

    :param filePath: Path of the file to scan
    :return: Returns the license's short name with least damerau levenshtien distance
    '''
    processedData = super().loadFile(filePath)

    temp = self.exactMatcher(processedData)
    if temp == -1:
      # Classify the license with minimum distance with scanned file
      distances = []
      result = None
      with ThreadPool(self.threads) as pool:
        func = partial(self.__dldDistance, processedData.split(" "))
        for shortname, distance in pool.imap(func,
                                 self.processedTextList,
                                 int(len(self.processedTextList)/self.threads)):
          if self.verbose > 0:
            print("%s %s" %(shortname,str(distance)))
          distances.append({'shortname':shortname, 'distance':distance})
      result = min(distances, key=lambda x:x['distance'])

      return result['shortname']
    else:
      return temp[0]

  def __dldDistance(self, textList, licenseData):
    '''
    Helper function to call damerau_levenshtein_distance.

    :param textList: Processed file data already splitted with spaces.
    :param licenseData: Dictionary of {shortname, processed_text}
    :return: The shortname of the license processed and DLD value.
    '''
    distance = damerau_levenshtein_distance(textList,
                                            licenseData['processed_text'].split(" "))
    shortname = licenseData['shortname']
    return (shortname, distance)


if __name__ == "__main__":
  print("The file has been run directly")
  parser = argparse.ArgumentParser()
  parser.add_argument("inputFile", help="Specify the input file which needs to be scanned")
  parser.add_argument("processedLicenseList",
                      help="Specify the processed license list file which contains licenses")
  parser.add_argument("-v", "--verbose", help="increase output verbosity",
                      action="count", default=0)
  args = parser.parse_args()
  filename = args.inputFile
  licenseList = args.processedLicenseList
  verbose = args.verbose

  scanner = DameruLevenDist(licenseList, verbose=verbose)
  print("License Detected using Dameru Leven Distance: " + str(scanner.scan(filename)))
