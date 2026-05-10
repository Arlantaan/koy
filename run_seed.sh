#!/bin/bash
set -e
cd /var/www/koya/backend
../.venv/bin/python seed.py 2>&1
