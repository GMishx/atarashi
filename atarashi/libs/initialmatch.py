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

__author__ = "Aman Jain"
__email__ = "amanjain5221@gmail.com"

from functools import partial
import itertools
from multiprocessing import Pool as ThreadPool
import os


threads = os.cpu_count() * 2

def HeadersNgramSim(header, processedData):
  '''
  Creates array of ngrams
  Check with the processed data how much are matching
  sim_score = matches/ count of ngrams

  :param header: License Header
  :param processedData: Input file extracted and processed data
  :return: Array of JSON with scanning results
  '''
  header = header.split(" ")
  ngrams = []
  for i in range(3, 8):
    ngrams += [header[j:j + i] for j in range(len(header) - i + 1)]
  count = 0
  for ngram in ngrams:
    if ' '.join(ngram) in processedData:
      count += 1
  sim = 0
  if len(ngrams) > 0:
    sim = float(count) / float(len(ngrams))
  return sim


def spdx_identifer(data, shortnames):
  '''
  Identify SPDX-License-Identifier
  Make sure the identifier must be present in Fossology merged license list

  :param data: Input File data
  :param shortnames: Array of shortnames (SPDX-ID)
  :return: Array of JSON with scanning results
  '''
  data = data.lower()  # preprocessing of data
  shortnamesLow = [shortname.lower() for shortname in shortnames]
  tokenized_data = data.split('\n')
  possible_spdx = []
  with ThreadPool(threads) as pool:
    for match in pool.imap(__spdx_token_identifier,
                           tokenized_data,
                           int(len(tokenized_data)/threads)):
      if match is not None:
        possible_spdx.append(match)

  spdx_identifiers = []
  if len(possible_spdx) > 0:
    with ThreadPool(threads) as pool:
      func = partial(__token_license_identifier, shortnamesLow)
      for shortnameIndex in pool.imap(func,
                             possible_spdx,
                             int(len(possible_spdx)/threads)):
        if shortnameIndex is not -1:
          spdx_identifiers.append({
            'shortname': shortnames[shortnameIndex],
            'sim_type': 'SPDXIdentifier',
            'sim_score': 1.0,
            'description': ''
          })

  return spdx_identifiers

def __spdx_token_identifier(raw_data):
  '''
  Helper function to check if a token contains SPDX identifier data.
  :param raw_data: Token to be inspected
  :return: Token if identifier found, None otherwise
  '''
  if "spdx-license-identifier:" in raw_data or "license:" in raw_data:
    return raw_data
  else:
    return None

def __token_license_identifier(shortnames, token):
  '''
  Helper function to check if a token is a license shortname.
  :param shortnames: List of known shortnames (lowercase).
  :param token: Token which has to match.
  :return: Index of shortname in shortnames list if found, -1 otherwise.
  '''
  for x in token.split(" "):
    if x in shortnames:
      return shortnames.index(x)
    else:
      return -1

def initial_match(filePath, processedData, licenses):
  '''
  :param inputFile: Input file path
  :param licenseList: Processed License List path
  :return: Array of JSON with scanning results from spdx_identifer and HeadersNgramSim
  '''

  with open(filePath) as file:
    raw_data = file.read()

  # Match SPDX identifiers
  spdx_identifiers = spdx_identifer(raw_data, [x['shortname'] for x in licenses])

  # match with headers
  # similarity with headers
  exact_match_header = []
  header_sim_match = []
  with ThreadPool(threads) as pool:
    func = partial(__header_similarity, processedData)
    for matches in pool.imap(func,
                           licenses,
                           int(len(licenses)/threads)):
      if 'exact_match_header' in matches:
        exact_match_header.append(matches['exact_match_header'])
      if 'header_sim_match' in matches:
        header_sim_match.append(matches['header_sim_match'])

  # match with full text
  exact_match_fulltext = []
  with ThreadPool(threads) as pool:
    func = partial(__full_text_match, processedData)
    for match in pool.imap(func,
                           licenses,
                           int(len(licenses)/threads)):
      if match is not None:
        exact_match_fulltext.append(match)

  matches = list(itertools.chain(spdx_identifiers, exact_match_header, exact_match_fulltext, header_sim_match[:5]))
  return matches

def __header_similarity(processedData, licenseList):
  '''
  Helper function to match header similarity using text match and N-grams.
  :param processedData: Processed file data.
  :param licenseList: License dict with `processed_header` and `shortname`.
  :return: Dictionary with `exact_match_header` and `header_sim_match` if found.
  '''
  retVal = {}
  if len(licenseList['processed_header']) > 0:
    if licenseList['processed_header'] in processedData:
      retVal['exact_match_header'] = {
        'shortname': licenseList['shortname'],
        'sim_type': 'ExactHeader',
        'sim_score': 1.0,
        'description': ''
      }
    ngram_sim = HeadersNgramSim(licenseList['processed_header'], processedData)
    if ngram_sim >= 0.7:
      retVal['header_sim_match'] = {
        'shortname': licenseList['shortname'],
        'sim_type': 'HeaderNgramSimilarity',
        'sim_score': ngram_sim,
        'description': ''
      }
  return retVal

def __full_text_match(processedData, licenseList):
  '''
  Helper function for full license text match.
  :param processedData: Processed file data.
  :param licenseList: License dict with `processed_text` and `shortname`.
  :return: Dictionary with match result.
  '''
  retVal = None
  if licenseList['processed_text'] in processedData:
    retVal = {
      'shortname': licenseList['shortname'],
      'sim_type': 'ExactFullText',
      'sim_score': 1.0,
      'description': ''
    }
  return retVal
