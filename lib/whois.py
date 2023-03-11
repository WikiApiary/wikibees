import sys
import string
import socket
import select
import errno

def queryWhois(query, server='whois.ripe.net'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while 1:
        try:
            s.connect((server, 43))
        except (socket.error, ecode, reason):
            if ecode==errno.EINPROGRESS: 
                continue
            elif ecode==errno.EALREADY:
                continue
            else:
                raise
            pass
        break

    ret = select.select ([s], [s], [], 30)

    if len(ret[1])== 0 and len(ret[0]) == 0:
        s.close()
        raise RuntimeException('timed out');

    s.setblocking(1)

    s.send(("%s\n" % query).encode())
    page = ""
    while 1:
        data = s.recv(8196)
        if not data: break
        page = page + data.decode()
        pass

    s.close()

    no_match_strings = [
        'IANA-BLK',
        'Allocated to LACNIC',
        'Not allocated by APNIC',
        'Allocated to APNIC',
        'Allocated to RIPE NCC',
        'Maintained by RIPE NCC',
        'Korea Network Information Center'
    ]

    for no_match in no_match_strings:
        if page.find(no_match) != -1:
            print("found %s in result" % no_match)
            raise RuntimeExeption('no match')
        
    return page
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: %s <IP address>" % sys.argv[0])
        sys.exit(1)
    ip = sys.argv[1]

    whois_servers = [
        'whois.arin.net',
        'whois.ripe.net',
        'whois.apnic.net',
        'whois.lacnic.net',
        'whois.afrinic.net',
        'whois.nic.or.kr'
    ]
    
    for server in whois_servers:
        print("trying %s" % server)
        try:
            res = queryWhois(ip, server)
            print('======', server)
            print(res)
            break # we only need the info once
        except:
            pass
