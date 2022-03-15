#!/usr/bin/python

import os
import sys
import socket
import urllib2
import json as simplejson
import re
from simplemediawiki import MediaWiki
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin, urlparse
import time

template = """{{Website
|Name=%s
|URL=%s
|Image=%s
|API URL=%s
|Collect general data override=Auto
|Collect general data=Yes
|Collect extension data override=Auto
|Collect extension data=Yes
|Collect skin data override=Auto
|Collect skin data=Yes
|Collect statistics override=Auto
|Collect statistics via=API
|Collect logs override=Auto
|Collect logs=No
|Collect recent changes override=Auto
|Collect recent changes=No
|Collect semantic statistics override=Auto
|Collect semantic statistics=No
|Check every=240
|Audited=No
|Curated=No
|Active=No
|Demote=No
|Defunct=No
}}
[[Category:WikiTeam Import]]"""

logo_page_text = """This image was automatically uploaded by [[User:Audit Bee|Audit Bee]] while importing.
[[Category:Import logos]] """

# timeout in seconds
timeout = 10
socket.setdefaulttimeout(timeout)

wiki = MediaWiki('https://wikiapiary.com/w/api.php',
                cookie_file='cookie-jar', 
                user_agent='python-simplemediawiki/1.1.1 (WikiApiary; Bumble Bee; +http://wikiapiary.com/wiki/User:Bumble_Bee)')
wiki.login('Audit Bee', 'frYqj2AmPTqZDjn4TANE')

# We need an edit token
c = wiki.call({'action': 'query', 'titles': 'Foo', 'prop': 'info', 'intoken': 'edit'})
my_token = c['query']['pages']['-1']['edittoken']

i = 0
success = 0
fail = 0
logo_count = 0

with open('BHW-alive_wikis.txt', 'rU') as f:
    for line in f:
        url = line.rstrip('\n')

        i += 1

        print "(%d) Processing: %s" % (i, url)

        # First check if this API URL is already in WikiApiary
        my_query = ''.join([
            "[[Category:Website]]",
            "[[Has API URL::%s]]" % url
            ])

        c = wiki.call({'action': 'ask', 'query': my_query})
        if len(c['query']['results']) > 0:
            print "(%d) Detected %d existing site.\n\n" % (i, len(c['query']['results']))
            continue
        else:
            print "(%d) API URL is not in WikiApiary, proceeding to add it." % i

        # Get metadata from the API
        data_url = "%s%s" % (url, '?action=query&meta=siteinfo&siprop=general&format=json')

        print "(%d) API Call: %s" % (i, data_url)
        req = urllib2.Request(data_url, None)
        req.add_header('User-Agent', 'Bumble Bee/1.0 (WikiApiary; +http://wikiapiary.com/wiki/User:Bumble_Bee)')
        opener = urllib2.build_opener()

        try:
            f = opener.open(req)

            data = simplejson.load(f)

            if 'error' in data:
                print "(%d) API returned error: %s\n\n" % (i, data['error']['info'])
                continue

            sitename = data['query']['general']['sitename']
            base_url = data['query']['general']['base']

            # Make sure there isn't already a page in WikiApiary with the intended sitename
            my_query = ''.join([
                "[[%s]]" % sitename
                ])

            c = wiki.call({'action': 'ask', 'query': my_query})
            if len(c['query']['results']) > 0:
                print "(%d) There is already a site named %s, skipping this entry.\n\n" % (i, sitename)
                continue

            try:
                # Attempt to find the $wgLogo
                logo_full_url = ''
                body_req = urllib2.Request(base_url, None)
                body_page = opener.open(body_req)

                soup = BeautifulSoup(body_page)

                logo_div = soup.find("div", {"id": "p-logo"})
                if logo_div is not None:
                    print "(%d) Found logo div" % (i)
                    logo_search = re.search(r"url\((\S+)\)", str(logo_div))
                    logo_url = logo_search.group(1)

                    logo_full_url = urljoin(base_url, logo_url)
                    logo_count += 1

                    print "(%d) Logo URL: %s" % (i, logo_full_url)

                else:
                    print "(%d) Unable to find logo div" % i

            except Exception as e:
                print "(%d) EXCEPTION: %s" % (i, e)

            if logo_full_url != '':
                # we found a URL for a logo, now upload it to Apiary
                path = urlparse(logo_full_url).path
                ext = os.path.splitext(path)[1]
                logo_pagename = "%s Logo%s" % (sitename, ext)

                # Add the file to the wiki
                print "(%d) Adding logo %s for %s..." % (i, logo_full_url, sitename)
                c = wiki.call({'action': 'upload', 'filename': logo_pagename, 'url': logo_full_url, 'text': logo_page_text, 'token': my_token})
                # c = wiki.call({'action': 'upload', 'filename': logo_pagename, 'url': logo_full_url, 'text': logo_page_text, 'ignorewarnings': 'true', 'token': my_token})
                print c

            else:
                logo_pagename = ''

            page = template % (sitename, base_url, logo_pagename, url)

            print page

            # Write the data collected back to the wiki
            target = "%s" % (data['query']['general']['sitename'])
            print "(%d) Target: %s" % (i, target)

            c = wiki.call({'action': 'edit', 'title': target, 'text': page, 'token': my_token, 'bot': 'true'})
            print c

            success += 1

        except Exception as e:
            print "(%d) EXCEPTION: %s\n" % (i, e)
            fail += 1
            continue

        print "\n"

print "Processed: %d  Success: %d  Logos: %d  Fail: %d" % (i, success, logo_count, fail)
