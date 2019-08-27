################################################################################
 # Copyright (c) 2017 Dan Iorga, Tyler Sorenson, Alastair Donaldson

 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documentation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to whom the Software is
 # furnished to do so, subject to the following conditions:

 # The above copyright notice and this permission notice shall be included in all
 #copies or substantial portions of the Software.

 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 # SOFTWARE.
################################################################################

import sys
import json
from pprint import pprint


class CalculateRank(object):
    def __init__(self, input_file):
        self._input_file = input_file

    def get_rank(self):
        # Read the configuration in the JSON file
        with open(self._input_file) as data_file:
            experiments_object = json.load(data_file)

        # Sort all the configurations in a list
        dict_list = list()
        for experiment in experiments_object:
            ranked_list = experiments_object[experiment]["it"]
            od = list(sorted(ranked_list.values(), key=lambda x:x['q_value'], reverse=True))
            dict_list.append(od)

        # for it in dict_list:
        #     print()
        #     print()
        #     for i in range(len(it)):
        #         print(it[i]['mapping'])
        #         print(it[i]['q_value'])

        # For each environment. get the rank in the other experiments and store in 'rank'
        for it in dict_list[0]:
            environment = it['mapping']
            rank_list = list()
            # Look it up for each victim(experiment)
            for it2 in dict_list:
                # Find its rank there
                for i in range(len(it2)):
                    env = it2[i]['mapping']
                    if environment == env:
                        rank_here = i
                        break
                rank_list.append(rank_here)
            it['rank'] = rank_list

        # Identify the ones that are not Pareto optimal
        rank_list_bad = list()
        for it1 in dict_list[0]:
            for it2 in dict_list[0]:
                if len([i for i, j in zip(it1['rank'], it2['rank']) if i > j]) == len(it1['rank']):
                    rank_list_bad.append(it1)

        # Put the Pareto Optimal in a list
        paretto_optimal = list()
        for it in dict_list[0]:
            if not (it in rank_list_bad):
                paretto_optimal.append(it)

        # If there are ties, try to break them at fewer comparisons
        if len(paretto_optimal) > 1:
            rank_list_bad = list()
            for it1 in paretto_optimal:
                for it2 in paretto_optimal:
                    if len([i for i, j in zip(it1['rank'], it2['rank']) if i > j]) == len(it1['rank']) - 1:
                        rank_list_bad.append(it1)

            # Put the tie broken ones in a list
            paretto_optimal_tie_break = list()
            for it in paretto_optimal:
                if not (it in rank_list_bad):
                    paretto_optimal_tie_break.append(it)

            for i in range(len(paretto_optimal_tie_break)):
                print(paretto_optimal_tie_break[i]['mapping'])
            print("I had to break ties")
        else:
            print(paretto_optimal[0]['mapping'])
            print("There was no tie breaking")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: " + sys.argv[0] + " <ranked_environments>.json\n")
        exit(1)

    rank = CalculateRank(sys.argv[1])

    rank.get_rank()
