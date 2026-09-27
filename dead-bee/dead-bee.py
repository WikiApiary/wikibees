#!/usr/bin/env python3
"""Dead Bee - identify and mark defunct WikiApiary websites.

Probes the API URL of active websites and marks them defunct in the wiki
after a configurable number of consecutive probe failures. Failure counts
are stored in the apiary.dead_bee_failures DB table so they persist
immediately and across runs.
"""

import argparse
import gzip
import json
import os
import re
import socket
import sys
import time
import traceback
import urllib.error
import urllib.parse
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
        parser.add_argument("-v", "--verbose", action="count", default=0,
                            help="increase output verbosity")
        self.args = parser.parse_args()

    def get_failure_count(self, website_id):
        """Return current consecutive failure count from DB."""
        try:
            cur = self.apiary_db.cursor()
            cur.execute(
                "SELECT consecutive_failures FROM dead_bee_failures WHERE website_id = %s",
                (website_id,)
            )
            row = cur.fetchone()
            cur.close()
            return row[0] if row else 0
        except Exception as e:
            print("WARNING: could not read failure count for %s: %s" % (website_id, e), file=sys.stderr)
            return 0

    def record_failure(self, site, reason):
        """Increment consecutive failure count in DB and return new count."""
        website_id = site['Has ID']
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        if self.args.debug:
            return self.get_failure_count(website_id) + 1
        try:
            cur = self.apiary_db.cursor()
            cur.execute('SET NAMES utf8mb4')
            sql = (
                "INSERT INTO dead_bee_failures "
                "(website_id, consecutive_failures, last_failure_date, last_failure_reason, last_check_date) "
                "VALUES (%s, 1, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE "
                "consecutive_failures = consecutive_failures + 1, "
                "last_failure_date = %s, "
                "last_failure_reason = %s, "
                "last_check_date = %s"
            )
            cur.execute(sql, (website_id, now, reason, now, now, reason, now))
            self.apiary_db.commit()
            cur.execute(
                "SELECT consecutive_failures FROM dead_bee_failures WHERE website_id = %s",
                (website_id,)
            )
            count = cur.fetchone()[0]
            cur.close()
            return count
        except Exception as e:
            print("WARNING: could not record failure for %s: %s" % (website_id, e), file=sys.stderr)
            return self.get_failure_count(website_id) + 1

    def record_success(self, site):
        """Clear failure count for a site that responded successfully."""
        website_id = site['Has ID']
        if self.args.debug:
            return
        try:
            cur = self.apiary_db.cursor()
            cur.execute('SET NAMES utf8mb4')
            cur.execute(
                "DELETE FROM dead_bee_failures WHERE website_id = %s",
                (website_id,)
            )
            self.apiary_db.commit()
            cur.close()
        except Exception as e:
            print("WARNING: could not clear failures for %s: %s" % (website_id, e), file=sys.stderr)

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

    def is_protected(self, response, body):
        """Detect CDN/WAF protection that blocks bots (Cloudflare, Alibaba ESA, etc.)."""
        headers = {}
        try:
            headers = dict(response.info())
        except Exception:
            pass
        server = headers.get('Server', '').lower()
        via = headers.get('Via', '').lower()
        cf_ray = headers.get('CF-RAY') or headers.get('Cf-Ray')
        if 'cloudflare' in server or cf_ray or 'cloudflare' in via:
            return True
        if 'esa' in server or 'ens-cache' in via:
            return True
        # Common challenge markers in body
        lowered = body.lower()
        if any(x in lowered for x in ['checking your browser', 'ddos-guard', 'under attack', 'attention required']):
            return True
        return False

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
            return (False, 'DNS failure: %s' % (e.strerror if e.strerror else 'unknown'))
        except Exception as e:
            return (False, 'DNS check error: %s' % e)

    def probe_site(self, site):
        """Return (status, detail)."""
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

        def decode_response(response):
            if response.info().get('Content-Encoding') == 'gzip':
                raw = gzip.GzipFile(fileobj=response).read().decode('utf-8')
            else:
                raw = response.read().decode('utf-8')
            if self.is_protected(response, raw):
                return None, 'protected by CDN/WAF'
            json_match = re.search(r"({.*})", raw, flags=re.MULTILINE)
            if json_match is None:
                return None, 'non-JSON body'
            try:
                return json.loads(json_match.group(1)), None
            except ValueError as e:
                return None, 'JSON parse error: %s' % e

        try:
            socket.setdefaulttimeout(self.args.timeout)
            with opener.open(req) as response:
                json_data, err = decode_response(response)
                if json_data is None:
                    return ('not_mediawiki', err)
                if 'query' in json_data and 'general' in json_data['query']:
                    return ('ok', json_data['query']['general'].get('generator', 'MediaWiki'))
                if 'error' in json_data:
                    code = json_data['error'].get('code', 'unknown')
                    if code in ('readapidenied', 'unsupportednamespace', 'unknown_action'):
                        return ('ok', 'api error %s but MediaWiki present' % code)
                    return ('http_error', 'api error %s' % code)
                return ('not_mediawiki', 'JSON missing expected MediaWiki structure')
        except urllib.error.HTTPError as e:
            try:
                json_data, err = decode_response(e)
                if json_data is None:
                    return ('not_mediawiki', 'HTTP %d %s' % (e.code, e.reason))
                if 'error' in json_data:
                    code = json_data['error'].get('code', 'unknown')
                    if code in ('readapidenied', 'unsupportednamespace', 'unknown_action'):
                        return ('ok', 'api error %s but MediaWiki present' % code)
                    return ('http_error', 'HTTP %d api error %s' % (e.code, code))
                return ('not_mediawiki', 'HTTP %d JSON missing MediaWiki structure' % e.code)
            except Exception:
                return ('not_mediawiki', 'HTTP %d %s' % (e.code, e.reason))
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

        checked = 0
        marked = 0
        failed = 0
        tracked = 0

        for site in sites:
            checked += 1
            status, detail = self.probe_site(site)

            if status == 'ok':
                self.record_success(site)
                if self.args.verbose >= 1:
                    print("OK: %s (%s): %s" % (site['pagename'], site['Has API URL'], detail))
            else:
                if status == 'protected':
                    print("PROTECTED: %s (%s): %s" % (site['pagename'], site['Has API URL'], detail))
                else:
                    count = self.record_failure(site, detail)
                    tracked += 1
                    print("FAIL: %s (%s): %s (consecutive failures: %d)" % (
                        site['pagename'], site['Has API URL'], detail, count))

                    if count >= self.args.threshold:
                        if self.mark_defunct(site, detail):
                            marked += 1
                            self.record_success(site)
                        else:
                            failed += 1

        finish_message = ("Completed Dead Bee. Checked %d sites, marked %d defunct, %d mark failures, "
                          "%d failures tracked in DB.") % (checked, marked, failed, tracked)
        print(finish_message)


if __name__ == "__main__":
    bee = DeadBee()
    bee.main()
