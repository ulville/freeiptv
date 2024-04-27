#!/bin/bash

cecho () {
    YLW='\033[0;33m'
    RST='\033[0m'
    echo -e "${YLW}$1${RST}"
}

cecho "Parsing for Kodi..."
"$(which python3)" parse-for-kodi.py || exit 1

cecho "Taking backup of unedited tr.m3u..."
cp tr.m3u tr-unedited.m3u

cecho "Replacing with liveproxy links"
"$(which python3)" add_liveproxy_links.py || exit 1

cecho "Removing failing channels..."
"$(which python3)" testlinks.py --override || exit 1

cecho "Removing github workflows..."
rm -r .github/workflows

cecho "Adding parsing results..."
git add . || exit 1
cecho "Commiting parsing results..."
git commit -m "parsed for kodi $(date -I)" || exit 1
cecho "Pushing to remote..."
git push
