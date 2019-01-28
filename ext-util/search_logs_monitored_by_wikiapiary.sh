#!/bin/zsh

echo "Searching /srv/www/mediawiki/logs/wikiapiary.com-access.log*"

zgrep "Monitored_by_WikiApiary.png" /srv/www/mediawiki/logs/wikiapiary.com-access.log* | \
        awk '{print $11}' | \
        grep --color=never -o -e "\/\/([^\/]+)\/" | \
        sort | \
        uniq

echo "Done."
