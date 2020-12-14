#!/bin/bash
kill $(pgrep -f 'python3 rednako.py')
dirname "$0"
cd ..
python3 rednako.py &