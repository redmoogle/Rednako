#!/bin/bash
kill $(pgrep -f 'python3 rednako.py')
dirname "$0"
cd $0
python3 rednako.py &