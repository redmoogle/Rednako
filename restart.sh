#!/bin/bash
kill $(pgrep -f 'python3 rednako.py')
python3 rednako.py &