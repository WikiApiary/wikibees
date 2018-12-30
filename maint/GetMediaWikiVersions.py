#!/usr/bin/python
"""
"""

import os
import sys
import time
import datetime
import pytz
import ConfigParser
import argparse
import socket
import MySQLdb as mdb
import json as simplejson
import urllib2
import string
from urllib2 import Request, urlopen, URLError, HTTPError
from simplemediawiki import MediaWiki
import re
sys.path.append('../lib')
from apiary import ApiaryBot


class GetMediaWikiVersions(ApiaryBot):
    mwVersions = {}

    def __init__(self):
        ApiaryBot.__init__(self)

    def build_list(self, start, limit):
        my_query = ''.join([
            "[[Category:Website]]",
            "[[Is active::True]]",
            "[[Has MediaWiki version::+]]",
            "|?Has MediaWiki version",
            "|sort=Creation date",
            "|order=asc",
            "|offset=%d" % start,
            "|limit=%d" % limit])

        if self.args.verbose >= 3:
            print "Query: %s" % my_query

        socket.setdefaulttimeout(30)
        sites = self.apiary_wiki.call({'action': 'ask', 'query': my_query})

        if len(sites['query']['results']) > 0:
            return len(sites['query']['results']), sites['query']['results'].items()
        else:
            return 0, None

    def main(self):
        # Setup our connection to the wiki too
        self.connectwiki('Bumble Bee')

        start = 0
        limit = 500
        site_total = 0
        site_total_ext = 0

        while True:
            print "Requesting %d sites starting at %d." % (limit, start)
            (site_count, sites) = self.build_list(start, limit)
            if site_count > 0:
                print "Received %d sites." % site_count
                for site in sites:
                    site_total += 1
                    verString = site[1]['printouts']['Has MediaWiki version'][0]
                    if verString not in self.mwVersions:
                        self.mwVersions[verString] = 0
                    self.mwVersions[verString] += 1
                start += limit
            else:
                break
        print self.mwVersions

# Run
if __name__ == '__main__':
    bot = GetMediaWikiVersions()
    bot.main()
