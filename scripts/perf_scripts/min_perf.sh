#!/usr/bin/env bash
perf stat -ebus-cycles -eLLC-loads -eLLC-stores -eLLC-load-misses -eLLC-store-misses  "${@:1}"