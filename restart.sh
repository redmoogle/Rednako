#!/bin/bash
kill $(pgrep -f 'python3 rednako.py')
cd ..
python3 rednako.py &