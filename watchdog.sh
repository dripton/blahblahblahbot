#!/bin/bash

until python3 src/blahblahblahbot/bot.py; do
   echo "bot crashed with exit code $?.  Respawning" >&2
   sleep 5
done
