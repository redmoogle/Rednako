#!/bin/bash
pkill -9 Lavalink
pkill -9 rednako
java -jar Lavalink.jar &
python3 rednako.py