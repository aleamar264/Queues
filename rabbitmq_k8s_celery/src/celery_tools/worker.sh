#!/bin/bash

set -o errexit
set -o nounset

celery -A main.celery worker --loglevel=info -Q Test_Query