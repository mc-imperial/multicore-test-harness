#!/usr/bin/env bash
perf stat -eLLC-loads -eLLC-stores -eLLC-load-misses -eLLC-store-misses -econtext-switches -epage-faults "${@:1}"
