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


def confidence_interval(x, quantile, desired_confidence=.9):

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


def getOverlap(a, b):
    return a[1]>b[0] and b[1]>a[0]

with open("final_joule3.json") as data_file:
    auto_object = json.load(data_file)

with open("assembly_stress_joule_small.json") as data_file:
    small_object = json.load(data_file)

with open("assembly_stress_joule_larger.json") as data_file:
    large_object = json.load(data_file)

comparison = dict()
for experiment in auto_object:
    comparison[experiment] = dict()

for experiment in auto_object:
    time_baseline = auto_object[experiment]["time_list_baseline"]
    time_auto = auto_object[experiment]["time_list_enemy"]
    time_small = small_object[experiment]["time_list_enemy"]
    time_large = large_object[experiment]["time_list_enemy"]

    baseline = confidence_interval(time_baseline, .9)
    auto = confidence_interval(time_auto,.9)
    small = confidence_interval(time_small, .9)
    large= confidence_interval(time_large, .9)

    overlap_auto_small = getOverlap(auto, small)
    overlap_auto_large = getOverlap(auto, large)
    overlap_small_large = getOverlap(small, large)

    baseline_q = mquantiles(time_baseline, .9)[0]
    auto_q = mquantiles(time_auto, .9)[0]
    small_q = mquantiles(time_small, .9)[0]
    large_q = mquantiles(time_large, .9)[0]

    comparison[experiment]["baseline_quantile"] = baseline_q
    comparison[experiment]["auto_quantile"] = auto_q / baseline_q
    comparison[experiment]["small_quantile"] = small_q / baseline_q
    comparison[experiment]["large_quantile"] = large_q / baseline_q

    comparison[experiment]["auto"] = [x/baseline_q for x in auto]
    comparison[experiment]["small"] = [x/baseline_q for x in small]
    comparison[experiment]["large"] = [x/baseline_q for x in large]
    comparison[experiment]["overlap_auto_small"] = overlap_auto_small
    comparison[experiment]["overlap_auto_large"] = overlap_auto_large
    comparison[experiment]["overlap_small_large"] = overlap_small_large

with open("overlaps.json", 'w') as outfile:
    json.dump(comparison, outfile, sort_keys=True, indent=4)

