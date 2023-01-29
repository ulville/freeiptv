#!/bin/bash

git fetch upstream &&
git merge upstream/master --no-edit &&
git commit -m "Merge changes from upstream $(date -I)" &&
/usr/bin/python3 parse-for-kodi.py &&
git commit -m "parsed for kodi $(date -I)"
