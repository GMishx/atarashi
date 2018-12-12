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
from enum import Enum
from functools import partial
import itertools
from multiprocessing import Pool as ThreadPool
from numpy import unique, sum, dot
import time

from sklearn.feature_extraction.text import TfidfVectorizer

from atarashi.agents.atarashiAgent import AtarashiAgent
from atarashi.libs.initialmatch import initial_match
from atarashi.libs.utils import l2_norm


__author__ = "Aman Jain"
__email__ = "amanjain5221@gmail.com"


def tokenize(data): return data.split(" ")


class TFIDF(AtarashiAgent):

  class TfidfAlgo(Enum):
    scoreSim = 1
    cosineSim = 2

  def __init__(self, licenseList, verbose=0, algo=TfidfAlgo.cosineSim):
    super(TFIDF, self).__init__(licenseList, verbose)
    self.algo = algo

  @staticmethod
  def __cosine_similarity(a, b):
    '''
    https://blog.nishtahir.com/2015/09/19/fuzzy-string-matching-using-cosine-similarity/

    :return: Cosine similarity value of two word frequency arrays
    '''
    dot_product = dot(a, b)
    temp = l2_norm(a) * l2_norm(b)
    if temp == 0:
      return 0
    else:
      return dot_product / temp

  def _sumscore_helper(self, tfresult):
    '''
    Helper function to get sum score for TFIDF.
    :param tfresult: Single result from `fit_transform` with index.
    :return: Index, sum score.
    '''
    return tfresult[0], sum(tfresult[1])

  def _cosinescore_helper(self, tfarray, tfresult):
    '''
    Helper function to get cosine sim score for TFIDF.
    :param tfarray: All result array from `fit_transform`.
    :param tfresult: Single result from `fit_transform` with index.
    :return: Index, cosine sim score.
    '''
    return tfresult[0], TFIDF.__cosine_similarity(tfresult[1], tfarray[-1])

  def __tfidfsumscore(self, inputFile):
    '''
    TF-IDF Sum Score Algorithm. Used TfidfVectorizer to implement it.

    :param inputFile: Input file path
    :return: Sorted array of JSON of scanner results with sim_type as __tfidfsumscore
    '''
    processedData1 = super().loadFile(inputFile)
    matches = initial_match(self.commentFile, processedData1, self.processedTextList)

    startTime = time.time()

    # unique words from tokenized input file
    processedData = unique(processedData1.split(" "))

    all_documents = self.licenseList['processed_text'].tolist()
    all_documents.append(processedData1)
    sklearn_tfidf = TfidfVectorizer(min_df=0, use_idf=True, smooth_idf=True,
                                    sublinear_tf=True, tokenizer=tokenize,
                                    vocabulary=processedData)

    sklearn_representation = sklearn_tfidf.fit_transform(all_documents)

    score_arr = []
    with ThreadPool(self.threads) as pool:
      tfarray = sklearn_representation.toarray()
      for index, score in pool.imap(self._sumscore_helper,
                                    enumerate(tfarray[:-1], start=0),
                                    int((len(tfarray) - 1)/self.threads)):
        score_arr.append({
          'shortname': self.licenseList.iloc[index]['shortname'],
          'sim_type': "Sum of TF-IDF score",
          'sim_score': score,
          'desc': "Score can be greater than 1 also"
        })
    score_arr.sort(key=lambda x: x['sim_score'], reverse=True)
    matches = list(itertools.chain(matches, score_arr[:5]))
    matches.sort(key=lambda x: x['sim_score'], reverse=True)
    if self.verbose > 0:
      print("time taken is " + str(time.time() - startTime) + " sec")
    return matches

  def __tfidfcosinesim(self, inputFile):
    '''
    TF-IDF Cosine Similarity Algorithm. Used TfidfVectorizer to implement it.

    :param inputFile: Input file path
    :return: Sorted array of JSON of scanner results with sim_type as __tfidfcosinesim
    '''
    processedData1 = super().loadFile(inputFile)
    matches = initial_match(self.commentFile, processedData1, self.processedTextList)

    startTime = time.time()

    all_documents = self.licenseList['processed_text'].tolist()
    all_documents.append(processedData1)
    sklearn_tfidf = TfidfVectorizer(min_df=0, use_idf=True, smooth_idf=True,
                                    sublinear_tf=True, tokenizer=tokenize)

    sklearn_representation = sklearn_tfidf.fit_transform(all_documents)

    with ThreadPool(self.threads) as pool:
      tfarray = sklearn_representation.toarray()
      func = partial(self._cosinescore_helper, tfarray)
      for index, score in pool.imap(func,
                                    enumerate(tfarray[:-1], start=0),
                                    int((len(tfarray) - 1)/self.threads)):
        if score >= 0.8:
          matches.append({
            'shortname': self.licenseList.iloc[index]['shortname'],
            'sim_type': "TF-IDF Cosine Sim",
            'sim_score': score,
            'desc': ''
          })
    matches.sort(key=lambda x: x['sim_score'], reverse=True)
    if self.verbose > 0:
      print("time taken is " + str(time.time() - startTime) + " sec")
    return matches

  def scan(self, filePath):
    if self.algo == self.TfidfAlgo.cosineSim:
      return self.__tfidfcosinesim(filePath)
    elif self.algo == self.TfidfAlgo.scoreSim:
      return self.__tfidfsumscore(filePath)
    else:
      return -1

  def getSimAlgo(self):
    return self.algo

  def setSimAlgo(self, newAlgo):
    if isinstance(newAlgo, self.TfidfAlgo):
      self.algo = newAlgo


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--tfidf_similarity", required=False,
                      default="ScoreSim",
                      choices=["CosineSim", "ScoreSim"],
                      help="Specify the similarity algorithm that you want")
  parser.add_argument("inputFile", help="Specify the input file which needs to be scanned")
  parser.add_argument("processedLicenseList",
                      help="Specify the processed license list file which contains licenses")
  parser.add_argument("-v", "--verbose", help="increase output verbosity",
                      action="count", default=0)
  args = parser.parse_args()

  tfidf_similarity = args.tfidf_similarity
  filename = args.inputFile
  licenseList = args.processedLicenseList
  verbose = args.verbose

  scanner = TFIDF(licenseList, verbose=verbose)
  if tfidf_similarity == "CosineSim":
    scanner.setSimAlgo(TFIDF.TfidfAlgo.cosineSim)
    print("License Detected using TF-IDF algorithm + cosine similarity " + str(scanner.scan(filename)))
  else:
    scanner.setSimAlgo(TFIDF.TfidfAlgo.scoreSim)
    print("License Detected using TF-IDF algorithm + sum score " + str(scanner.scan(filename)))
