#!/bin/bash

set -o errexit
set -o nounset

# faust -A main:faust worker -l info
python -m faust_tools worker -l info 