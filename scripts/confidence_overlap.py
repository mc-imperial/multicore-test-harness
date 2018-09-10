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

from scipy.stats.mstats import mquantiles
from scipy.stats import binom
import sys
import json
from pprint import pprint
import itertools

QUANTILE = .9
CONF_INTERVAL = .9


class Confidence:
    def __init__(self, argv):

        self._input_data = list()
        for i in range(1, len(argv)):
            with open(argv[i]) as data_file:
                self._input_data.append(json.load(data_file))

    def _confidence_interval(self, x, quantile, desired_confidence=CONF_INTERVAL):

        assert isinstance(x, list)
        x.sort()
        q = mquantiles(x, quantile)[0]
        n = len(x)

        confidence = 0

        middle = round(quantile * n)
        ui = middle
        li = middle
        while confidence < desired_confidence:
            if ui < n-1:
                ui = ui + 1
            if li > 0:
                li = li-1
            confidence = binom.cdf(ui-1, n, quantile) - binom.cdf(li-1, n, quantile)

            if ui >= n-1 and li <= 0:
                li = 0
                ui = n-1
                break

        lower_range = x[li]
        upper_range = x[ui]

        return lower_range, upper_range

    @staticmethod
    def _get_overlap(a, b):
        return a[1]>b[0] and b[1]>a[0]

    def run(self):

        comparison = dict()
        for experiment in self._input_data[0]:
            comparison[experiment] = dict()

        for experiment in self._input_data[0]:
            time_enemy = dict()
            for i, data in enumerate(self._input_data):
                # I do not really care whee you the baseline from
                time_baseline = data[experiment]["time_list_baseline"]
                # Time enemy
                time_enemy[data[experiment]['stress']] = data[experiment]["time_list_enemy"]


            baseline_q = mquantiles(time_baseline, .9)[0]

            for comb in itertools.combinations(time_enemy, 2):

                confidence_interval1 = self._confidence_interval(time_enemy[comb[0]], QUANTILE)
                confidence_interval2 = self._confidence_interval(time_enemy[comb[1]], QUANTILE)

                confidence_overlap = self._get_overlap(confidence_interval1, confidence_interval2)

                first_q = mquantiles(time_enemy[comb[0]], QUANTILE)[0]
                second_q = mquantiles(time_enemy[comb[1]], QUANTILE)[0]

                comparison[experiment]["baseline_quantile"] = baseline_q
                comparison[experiment][comb[0] + "_quantile"] = first_q / baseline_q
                comparison[experiment][comb[1] + "_quantile"] = second_q / baseline_q

                comparison[experiment][comb[0] + "_range"] = [x / baseline_q for x in confidence_interval1]
                comparison[experiment][comb[1] + "_range"] = [x / baseline_q for x in confidence_interval2]

                comparison[experiment][comb[0] + "\n" + comb[1] + "_overlap"] = confidence_overlap

        with open("overlaps.json", 'w') as outfile:
            json.dump(comparison, outfile, sort_keys=True, indent=4)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: " + sys.argv[0] + " <list_data1>.json <list_data2>.json\n")
        exit(1)

    rank = Confidence(sys.argv)
    rank.run()
