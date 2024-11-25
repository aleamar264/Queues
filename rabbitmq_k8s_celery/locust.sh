#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

locust -f complete_flow_load_test.py;