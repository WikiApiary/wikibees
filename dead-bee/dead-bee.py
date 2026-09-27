#!/usr/bin/env python3
"""Dead Bee - identify and mark defunct WikiApiary websites.

Probes the API URL of active websites and marks them defunct in the wiki
after a configurable number of consecutive probe failures.
"""

import argparse
import json
import os
import re
import socket
import sys
import time
import traceback
import urllib.error
import urllib.parse
import gzip
import urllib.request

sys.path.append('../lib')
from apiary import ApiaryBot


class DeadBee(ApiaryBot):
    def __init__(self):
        self.stats = {}
        self.args = None
        self.config = None
        self.apiary_wiki = None
        self.apiary_db = None
        self.get_args()
        self.get_config(self.args.config)
        self.connectdb()

    def get_args(self):
        parser = argparse.ArgumentParser(
            prog="Dead Bee",
            description="identifies unreachable or non-MediaWiki sites and marks them defunct"
        )
        parser.add_argument("--site", type=int, help="only check this specific site id")
        parser.add_argument("--limit", type=int, default=0, help="max sites to check (0 = unlimited)")
        parser.add_argument("--offset", type=int, default=0, help="skip the first N sites returned by WikiApiary")
        parser.add_argument("--threshold", type=int, default=3,
                            help="consecutive failures before marking defunct (default 3)")
        parser.add_argument("--timeout", type=int, default=30, help="probe timeout in seconds")
        parser.add_argument("-d", "--debug", action="store_true",
                            help="do not write any changes to wiki or database")
        parser.add_argument("--config", default="../bumble-bee/apiary.cfg",
                            help="path to apiary.cfg (default ../bumble-bee/apiary.cfg)")
        parser.add_argument("--state", default="dead-bee-state.json",
                            help="path to JSON state file tracking failure counts")
        parser.add_argument("-v", "--verbose", action="count", default=0,
                            help="increase output verbosity")
        self.args = parser.parse_args()

    def load_state(self):
        if os.path.exists(self.args.state):
            try:
                with open(self.args.state) as f:
                    return json.load(f)
            except Exception as e:
                print("WARNING: could not load state file %s: %s" % (self.args.state, e))
        return {}

    def save_state(self, state):
        if self.args.debug:
            return
        try:
            tmp = self.args.state + ".tmp"
            with open(tmp, "w") as f:
                json.dump(state, f, indent=2, sort_keys=True)
            os.replace(tmp, self.args.state)
        except Exception as e:
            print("WARNING: could not save state file %s: %s" % (self.args.state, e))

    def get_sites(self):
        """Fetch active, non-defunct websites from WikiApiary."""
        if self.args.site is not None:
            filter_string = "[[Has ID::%d]]" % self.args.site
        else:
            filter_string = ""

        my_query = ''.join([
            '[[Category:Website]]',
            '[[Is defunct::False]]',
            '[[Is active::True]]',
            filter_string,
            '|?Has API URL',
            '|?Has ID',
            '|sort=Creation date',
            '|order=asc',
            '|limit=5000'
        ])

        if self.args.verbose >= 2:
            print("Query: %s" % my_query)

        try:
            sites = self.apiary_wiki.call({'action': 'ask', 'query': my_query})
        except Exception as e:
            print("ERROR: failed to query WikiApiary: %s" % e, file=sys.stderr)
            return None

        my_sites = []
        for pagename, site in sites.get('query', {}).get('results', {}).items():
            try:
                api_urls = site['printouts'].get('Has API URL', [])
                has_ids = site['printouts'].get('Has ID', [])
                if not api_urls or not has_ids:
                    if self.args.verbose >= 2:
                        print("SKIPPING: %s (missing API URL or ID)" % pagename)
                    continue
                api_url = api_urls[0]
                has_id = int(has_ids[0])
                if api_url:
                    my_sites.append({
                        'pagename': pagename,
                        'Has API URL': api_url,
                        'Has ID': has_id,
                    })
            except Exception as e:
                if self.args.verbose >= 1:
                    print("WARNING: failed to parse %s: %s" % (pagename, e))

        if self.args.offset:
            my_sites = my_sites[self.args.offset:]
        if self.args.limit:
            my_sites = my_sites[:self.args.limit]

        return my_sites

    def resolve_hostname(self, url):
        """Return (True, '') if hostname resolves, (False, reason) otherwise."""
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.hostname:
                return (False, 'no hostname in URL')
            socket.setdefaulttimeout(5)
            socket.getaddrinfo(parsed.hostname, None)
            return (True, '')
        except socket.gaierror as e:
            return (False, 'DNS failure: %s' % e.strerror if e.strerror else 'DNS failure')
        except Exception as e:
            return (False, 'DNS check error: %s' % e)

    def probe_site(self, site):
        """Return (status, detail) where status is one of: ok, unreachable, http_error, not_mediawiki, timeout, error."""
        url = site['Has API URL']
        if not url:
            return ('unreachable', 'no API URL')

        ok, reason = self.resolve_hostname(url)
        if not ok:
            return ('unreachable', reason)

        if '?' in url:
            probe_url = url + '&action=query&meta=siteinfo&format=json'
        else:
            probe_url = url + '?action=query&meta=siteinfo&format=json'

        req = urllib.request.Request(probe_url)
        req.add_header('User-Agent', self.config.get('Bumble Bee', 'user-agent'))
        req.add_header('Accept-Encoding', 'gzip')
        opener = urllib.request.build_opener()

        try:
            socket.setdefaulttimeout(self.args.timeout)
            with opener.open(req) as response:
                if response.info().get('Content-Encoding') == 'gzip':
                    raw = gzip.GzipFile(fileobj=response).read().decode('utf-8')
                else:
                    raw = response.read().decode('utf-8')

                json_match = re.search(r"({.*})", raw, flags=re.MULTILINE)
                if json_match is None:
                    return ('not_mediawiki', 'response is not JSON')

                try:
                    json_data = json.loads(json_match.group(1))
                except ValueError as e:
                    return ('not_mediawiki', 'JSON parse error: %s' % e)

                if 'query' in json_data and 'general' in json_data['query']:
                    return ('ok', json_data['query']['general'].get('generator', 'MediaWiki'))
                if 'error' in json_data:
                    code = json_data['error'].get('code', 'unknown')
                    if code in ('readapidenied', 'unsupportednamespace', 'unknown_action'):
                        return ('ok', 'api error %s but MediaWiki present' % code)
                    return ('http_error', 'api error %s' % code)
                return ('not_mediawiki', 'JSON missing expected MediaWiki structure')
        except urllib.error.HTTPError as e:
            # An API endpoint should return JSON even on errors. If it returns
            # HTML or plain text, the site is probably not MediaWiki anymore.
            try:
                if e.info().get('Content-Encoding') == 'gzip':
                    body = gzip.GzipFile(fileobj=e).read().decode('utf-8')
                else:
                    body = e.read().decode('utf-8')
                json_match = re.search(r"({.*})", body, flags=re.MULTILINE)
                if json_match is None:
                    return ('not_mediawiki', 'HTTP %d returned non-JSON body' % e.code)
                json_data = json.loads(json_match.group(1))
                if 'error' in json_data:
                    code = json_data['error'].get('code', 'unknown')
                    if code in ('readapidenied', 'unsupportednamespace', 'unknown_action'):
                        return ('ok', 'api error %s but MediaWiki present' % code)
                    return ('http_error', 'HTTP %d api error %s' % (e.code, code))
                return ('not_mediawiki', 'HTTP %d JSON missing MediaWiki structure' % e.code)
            except Exception:
                return ('not_mediawiki', 'HTTP %d %s (non-JSON body)' % (e.code, e.reason))
        except urllib.error.URLError as e:
            reason = str(e.reason)
            if 'timed out' in reason.lower() or 'timeout' in reason.lower():
                return ('timeout', reason)
            if 'no entries found' in reason.lower() or 'name or service not known' in reason.lower():
                return ('unreachable', 'DNS failure: %s' % reason)
            if 'connection refused' in reason.lower() or 'network is unreachable' in reason.lower():
                return ('unreachable', reason)
            return ('unreachable', reason)
        except socket.timeout:
            return ('timeout', 'socket timeout')
        except Exception as e:
            return ('error', '%s: %s' % (type(e).__name__, e))

    def set_flag(self, pagename, name, value, comment):
        if self.args.debug:
            print("DEBUG: would set %s %s = %s (%s)" % (pagename, name, value, comment))
            return True
        if self.args.verbose >= 2:
            print("%s setting %s to %s (%s)" % (pagename, name, value, comment))

        property_name = "Website[%s]" % name
        socket.setdefaulttimeout(30)
        try:
            c = self.apiary_wiki.call({
                'action': 'pfautoedit',
                'form': 'Website',
                'target': pagename,
                property_name: value,
                'bot': '',
                'wpSummary': comment
            })
            if self.args.verbose >= 3:
                print(c)
            return True
        except Exception as e:
            print("ERROR: failed to set %s %s = %s: %s" % (pagename, name, value, e), file=sys.stderr)
            return False

    def mark_defunct(self, site, reason):
        comment = "Marking defunct: %s" % reason
        ok1 = self.set_flag(site['pagename'], 'Defunct', 'Yes', comment)
        ok2 = self.set_flag(site['pagename'], 'Active', 'No', comment)
        return ok1 and ok2

    def main(self):
        thisBot = 'Dead Bee'
        start_message = "Starting Dead Bee."
        print(start_message)

        try:
            self.connectwiki('Bumble Bee')
        except Exception as e:
            print("ERROR: failed to connect to WikiApiary: %s" % e, file=sys.stderr)
            return

        sites = self.get_sites()
        if sites is None:
            print("ERROR: could not retrieve site list", file=sys.stderr)
            return

        print("Found %d sites to check." % len(sites))

        state = self.load_state()
        checked = 0
        marked = 0
        failed = 0

        for site in sites:
            checked += 1
            sid = str(site['Has ID'])
            status, detail = self.probe_site(site)

            if status == 'ok':
                if sid in state:
                    del state[sid]
                if self.args.verbose >= 1:
                    print("OK: %s (%s): %s" % (site['pagename'], site['Has API URL'], detail))
            else:
                count = state.get(sid, 0) + 1
                state[sid] = count
                print("FAIL: %s (%s): %s (consecutive failures: %d)" % (
                    site['pagename'], site['Has API URL'], detail, count))

                if count >= self.args.threshold:
                    if self.mark_defunct(site, detail):
                        marked += 1
                        del state[sid]
                    else:
                        failed += 1

        self.save_state(state)

        finish_message = ("Completed Dead Bee. Checked %d sites, marked %d defunct, %d mark failures, "
                          "%d tracked failures.") % (checked, marked, failed, len(state))
        print(finish_message)


if __name__ == "__main__":
    bee = DeadBee()
    bee.main()
