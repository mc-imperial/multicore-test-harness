import sys
import json


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
            ranked_list = experiments_object[experiment]["ranked_list"]
            od = list(sorted(ranked_list.values(), key=lambda x:x['score'], reverse=True))
            dict_list.append(od)

        # For each environment. get the rank in the other experiments and store in 'rank'
        for it in dict_list[0]:
            environment = it['env']
            rank_list = list()
            # Look it up for each victim(experiment)
            for it2 in dict_list:
                # Find its rank there
                for i in range(len(it2)):
                    env = it2[i]['env']
                    if environment == env:
                        rank_here = i
                        break
                rank_list.append(rank_here)
            it['rank'] = rank_list

        # Identify the ones that are not Pareto optimal
        rank_list_bad = list()
        for it1 in dict_list[0]:
            for it2 in dict_list[0]:
                if len([i for i, j in zip(it1['rank'], it2['rank']) if i > j]) == len(it1):
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
                    if len([i for i, j in zip(it1['rank'], it2['rank']) if i > j]) == len(it1) - 1:
                        rank_list_bad.append(it1)

            # Put the tie broken ones in a list
            paretto_optimal_tie_break = list()
            for it in paretto_optimal:
                if not (it in rank_list_bad):
                    paretto_optimal_tie_break.append(it)

            print(paretto_optimal_tie_break)
        else:
            print(paretto_optimal)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: " + sys.argv[0] + " <ranked_environments>.json\n")
        exit(1)

    rank = CalculateRank(sys.argv[1])

    rank.get_rank()
