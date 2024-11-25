#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

fastapi dev main.py --port 8001 --host "0.0.0.0";