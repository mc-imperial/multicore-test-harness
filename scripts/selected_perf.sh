#!/usr/bin/env bash
perf stat -ecycles -ecache-misses -ebus-cycles -eL1-dcache-load-misses -eL1-dcache-store-misses -eL1-icache-load-misses  -eLLC-load-misses -eLLC-store-misses  -edTLB-load-misses -edTLB-store-misses -eiTLB-load-misses "${@:1}"
