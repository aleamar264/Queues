#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

fastapi dev main.py --port 8001 --host "0.0.0.0" ;
# uvicorn main:app --port 8001 --host 0.0.0.0 ;
# gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001 ;