"""Bounded public page check; does not print response bodies or URL query strings."""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

def clean_url(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, '', ''))

def validate_url(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
        raise ValueError('Use an HTTP(S) URL without embedded credentials')

def check(url, contains=None, timeout=15, opener=None):
    validate_url(url)
    result = {'url': clean_url(url), 'ok': False}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'web-dev-pilot-check/1.0'})
        open_request = opener.open if opener else urllib.request.urlopen
        with open_request(request, timeout=timeout) as response:
            body = response.read(2_000_001)
            text = body.decode(response.headers.get_content_charset() or 'utf-8', errors='replace')
            result.update(status=response.status, final_url=clean_url(response.url), truncated=len(body) > 2_000_000, text_match=contains in text if contains else None)
            result['ok'] = 200 <= response.status < 300 and (contains is None or result['text_match'])
    except urllib.error.HTTPError as error:
        result.update(status=error.code, error='HTTP error')
    except (urllib.error.URLError, TimeoutError, OSError):
        result['error'] = 'Network or TLS error; no response verified'
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('--contains')
    args = parser.parse_args()
    try:
        result = check(args.url, args.contains)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result['ok'] else 1)
