#!/usr/bin/env python3
"""Searches allowance for the shared Google Maps key used by Midway and Nearby Pair.

Google gives each billed item ("SKU") its own free allowance every month. Before a search on
the shared key, the page POSTs what it is about to do; this script works out the most it can
cost in each SKU, and refuses if that would take the month past a safe share of the free
allowance, or one day past a quarter of the month's share (so one busy evening can't use it all).

GET returns a one-line summary for the Settings tab.

Usage is kept in a JSON file outside the web root (see USAGE_FILE). The limits can be changed
in LIMITS below; costs are upper bounds taken from the page's search code.
"""
import datetime
import fcntl
import json
import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
# apps/midway-quota/quota.cgi -> ../../private/midway-usage.json
USAGE_FILE = os.path.join(HERE, '..', '..', 'private', 'midway-usage.json')

# Google's free monthly calls per SKU (Essentials 10,000, Pro 5,000, Enterprise 1,000).
FREE = {
    'routes': 10000,          # Compute Route Matrix Essentials, per element
    'routesPro': 5000,        # Compute Route Matrix Pro (traffic-aware driving), per element
    'placesPro': 5000,        # Nearby/Text Search Pro (no ratings)
    'placesEnterprise': 1000,  # Nearby/Text Search Enterprise (with ratings)
    'placesAtmosphere': 1000,  # Enterprise + Atmosphere (EV charger details)
}
SAFE_SHARE = 0.9   # stop at 90% of the free allowance
DAY_SHARE = 0.25   # no single day may use more than a quarter of the month's share
LIMITS = {k: int(v * SAFE_SHARE) for k, v in FREE.items()}

NAMES = {'meet': 'Midway', 'pair': 'Nearby Pair'}


def cost(req):
    """Most a search can use, per SKU. Mirrors findMiddle() and findPairs() in the page."""
    app = req.get('app')
    if app == 'meet':
        c = {'routesPro' if req.get('traffic') else 'routes': 78,  # 2 people x (15 probes + 24 venues)
             'placesEnterprise': 3}                                   # 3 venue searches with ratings
        if req.get('driving'):
            c['placesPro'] = 8                                        # parking near each of 8 results
        return c
    if app == 'pair':
        if req.get('mode') == 'anchor':
            return {'placesAtmosphere' if req.get('ev') else 'placesEnterprise': 1, 'routes': 20}
        c = {'placesAtmosphere' if req.get('mainEv') else 'placesEnterprise': 1, 'routes': 80}
        key = 'placesAtmosphere' if req.get('ev') else 'placesPro'
        c[key] = c.get(key, 0) + 8                                     # neighbours of 8 main places
        return c
    return None


def load(f):
    f.seek(0)
    try:
        data = json.load(f)
    except ValueError:
        data = {}
    return data


def periods():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime('%Y-%m'), now.strftime('%Y-%m-%d')


def headroom(data, month, day):
    """How many more of each kind of search fit this month and today."""
    m = data.get('month', {}) if data.get('monthKey') == month else {}
    d = data.get('day', {}) if data.get('dayKey') == day else {}
    out = {}
    for app, req in (('meet', {'app': 'meet'}), ('pair', {'app': 'pair', 'mode': 'both', 'ev': True})):
        n = None
        for sku, units in cost(req).items():
            left_m = (LIMITS[sku] - m.get(sku, 0)) // units
            left_d = (int(LIMITS[sku] * DAY_SHARE) - d.get(sku, 0)) // units
            n = min(x for x in (n, left_m, left_d) if x is not None)
        out[app] = max(0, n)
    return out


def reply(status, body):
    sys.stdout.write(f'Status: {status}\r\nContent-Type: application/json\r\nCache-Control: no-store\r\n\r\n')
    sys.stdout.write(json.dumps(body))


def main():
    method = os.environ.get('REQUEST_METHOD', 'GET')
    os.makedirs(os.path.dirname(USAGE_FILE), exist_ok=True)
    month, day = periods()
    fd = os.open(USAGE_FILE, os.O_RDWR | os.O_CREAT, 0o600)
    with os.fdopen(fd, 'r+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        data = load(f)
        if data.get('monthKey') != month:
            data['monthKey'], data['month'] = month, {}
        if data.get('dayKey') != day:
            data['dayKey'], data['day'] = day, {}

        if method == 'GET':
            h = headroom(data, month, day)
            return reply('200 OK', {
                'ok': True, 'left': h,
                'summary': f"Searches left on it today: about {h['meet']} in Midway and {h['pair']} in Nearby Pair.",
            })
        if method != 'POST':
            return reply('405 Method Not Allowed', {'ok': False})

        try:
            length = min(int(os.environ.get('CONTENT_LENGTH') or 0), 2000)
            req = json.loads(sys.stdin.read(length) or '{}')
        except ValueError:
            return reply('400 Bad Request', {'ok': False, 'message': 'Bad request.'})
        c = cost(req) if isinstance(req, dict) else None
        if not c:
            return reply('400 Bad Request', {'ok': False, 'message': 'Unknown search.'})

        for sku, units in c.items():
            over_month = data['month'].get(sku, 0) + units > LIMITS[sku]
            over_day = data['day'].get(sku, 0) + units > int(LIMITS[sku] * DAY_SHARE)
            if over_month or over_day:
                when = 'this month' if over_month else 'today'
                retry = 'next month' if over_month else 'tomorrow'
                return reply('200 OK', {'ok': False, 'message':
                    f"The shared key's free searches for {NAMES[req['app']]} are used up {when}. "
                    f"Try again {retry}, or add your own Google Maps key in Settings."})

        for sku, units in c.items():
            data['month'][sku] = data['month'].get(sku, 0) + units
            data['day'][sku] = data['day'].get(sku, 0) + units
        # Rewritten in place while locked, so a waiting request never reads a stale copy.
        f.seek(0)
        f.truncate()
        json.dump(data, f)
        f.flush()
        os.fsync(f.fileno())
        reply('200 OK', {'ok': True})


if __name__ == '__main__':
    main()
