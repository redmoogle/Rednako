#!/bin/bash
pkill rednako.py
dirname "$0"
cd ..
dirname "$0"
git pull
python3 rednako.py &