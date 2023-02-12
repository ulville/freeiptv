#!/bin/bash

echo "Fetching Upstream..."
git fetch upstream &&
echo "Merging Upstream..."
git merge upstream/master --no-edit &&
echo "Commiting merged changes..."
git commit -m "Merge changes from upstream $(date -I)" &&
echo "Parsing for Kodi..."
"$(which python3)" parse-for-kodi.py &&
echo "Adding parsing results..."
git add . &&
echo "Commiting parsing results..."
git commit -m "parsed for kodi $(date -I)" &&
echo "Pushing to remote..."
git push