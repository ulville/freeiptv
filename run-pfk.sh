#!/bin/bash

echo "Fetching Origin"
git fetch || exit 1
echo "Pulling from Origin"
git pull || exit 1
echo "Fetching Upstream..."
git fetch upstream || exit 1
echo "Merging Upstream..."
git merge upstream/master --no-edit || exit 1
echo "Commiting merged changes..."
git commit -m "Merge changes from upstream $(date -I)"

echo "Parsing for Kodi..."
"$(which python3)" parse-for-kodi.py || exit 1

echo "Taking backup of unedited tr.m3u..."
cp tr.m3u tr-unedited.m3u

echo "Replacing with liveproxy links"
"$(which python3)" add_liveproxy_links.py || exit 1

echo "Removing failing channels..."
"$(which python3)" testlinks.py --override || exit 1

echo "Removing github workflows..."
rm -r .github/workflows

echo "Adding parsing results..."
git add . || exit 1
echo "Commiting parsing results..."
git commit -m "parsed for kodi $(date -I)" || exit 1
echo "Pushing to remote..."
git push
