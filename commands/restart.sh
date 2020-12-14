#!/bin/bash
pkill rednako.py
dirname "$0"
cd ..
git pull
python3 rednako.py &