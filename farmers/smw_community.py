#!/usr/bin/python
"""
Pull sites from the SMW Community wiki
"""

import requests
from BeautifulSoup import BeautifulSoup
import ConfigParser
import urlparse
import time
from simplemediawiki import MediaWiki


class smw_community:
    sites = []
    # Blank reference to store mediawiki object in
    wikiapiary = {}
    smwreferata = {}
    # Edit token
    my_token = ""
    # Counter
    create_counter = 0

    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read('../apiary.cfg')

        # Connect to SMW Community Wiki
        self.smwreferata = MediaWiki('http://smw.referata.com/w/api.php')

        # Connect to WikiApiary
        self.wikiapiary = MediaWiki(config.get('WikiApiary', 'api'))
        self.wikiapiary.login(config.get('wikkiibot', 'Username'), config.get('wikkiibot', 'Password'))

        # We need an edit token
        c = self.wikiapiary.call({
            'action': 'query',
            'titles': 'Foo',
            'prop': 'info',
            'intoken': 'edit'
        })
        self.my_token = c['query']['pages']['-1']['edittoken']

    def load_from_smwreferata(self):
        # Build query for sites
        my_query = ''.join([
            '[[Category:Sites]]',
            '[[Has status::Active]]',
            '|?Has URL',
            '|?Has data type'
            '|limit=1000'])
        print "Query: %s" % my_query
        sites = self.smwreferata.call({'action': 'ask', 'query': my_query})

        # We could just return the raw JSON object from the API, however instead we are going to clean it up into an
        # easier to deal with array of dictionary objects.
        # To keep things sensible, we'll use the same name as the properties
        if len(sites['query']['results']) > 0:
            for pagename, site in sites['query']['results'].items():
                print "Adding %s." % pagename

                self.sites.append({
                    'Name': pagename,
                    'URL': site['printouts']['Has URL'][0],
                    'Tag': ','.join(site['printouts']['Has data type'])
                })

    def add_api_to_sites(self):
        # Loop through the sites and find API urls
        for i in range(0, len(self.sites)):
            print "Investigating %s (%s)..." % (self.sites[i]['Name'], self.sites[i]['URL'])
            try:
                req = requests.get(self.sites[i]['URL'])
                if req.status_code == 200:
                    soup = BeautifulSoup(req.text)
                    api_url = soup.findAll('link', {'rel': 'EditURI'})[0]['href']
                    print "  Found %s" % api_url
                    new_api_url = urlparse.urlunparse(urlparse.urlparse(api_url)[0:3] + ('', '', ''))
                    print "  Resolved %s" % new_api_url
                    self.sites[i]['API URL'] = new_api_url
                else:
                    print "  Returned %s" % req.status_code
            except Exception as e:
                print "Exception: %s" % e

    def main(self):
        # Get the list of tokens from the config file
        self.load_from_smwreferata()

        for site in self.sites:
            print site

        self.add_api_to_sites()

        for site in self.sites:
            print site

# Run
if __name__ == '__main__':
    myClass = smw_community()
    myClass.main()
