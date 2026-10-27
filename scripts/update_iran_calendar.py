#!/usr/bin/env python3
"""Record the official Hijri month start for Iran in calendar/iran.json.

Source: time.ir, which publishes the official calendar of Iran (Calendar Center, Institute of
Geophysics, University of Tehran). Its home page carries today's Gregorian and Hijri dates; the
Hijri day number gives the first day of the current month. prayer.aviny.com's public web service
is read as a second opinion: a disagreement is reported, never written.

A month's start is recorded the first time it is seen and changes only if time.ir changes it.
Usage: python3 -I scripts/update_iran_calendar.py [--page saved-time-ir.html]
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import sys
import urllib.request

OUT = pathlib.Path(__file__).resolve().parents[1] / "calendar/iran.json"
TIME_IR = "https://www.time.ir/"
AVINY = "http://prayer.aviny.com/api/prayertimes/1"  # its HTTPS certificate had expired
AGENT = {"User-Agent": "angel-data calendar check (https://github.com/mohsen-khalili/angel-data)"}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=AGENT), timeout=60).read().decode("utf-8")


def time_ir_today(page):
    page = page.replace('\\"', '"')
    g = re.search(r'"gregorian":\{"year":(\d+),"month":(\d+),"day":(\d+)', page)
    h = re.search(r'"hijri":\{"year":(\d+),"month":(\d+),"day":(\d+)', page)
    if not g or not h:
        sys.exit("time.ir page layout changed: today's dates not found")
    return dt.date(*map(int, g.groups())), tuple(map(int, h.groups()))


def aviny_hijri():
    try:
        y, m, d = map(int, json.loads(get(AVINY))["TodayQamari"].split("/"))
        return y, m, d
    except Exception as e:  # a second opinion only
        print(f"::warning::aviny unavailable: {e}")
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", help="read a saved copy of the time.ir home page instead of fetching it")
    args = ap.parse_args()
    page = pathlib.Path(args.page).read_text(encoding="utf-8") if args.page else get(TIME_IR)
    today, (hy, hm, hd) = time_ir_today(page)
    if not args.page:
        other = aviny_hijri()
        if other and other != (hy, hm, hd):
            print(f"::warning::time.ir says {hd}/{hm}/{hy}, aviny says {other[2]}/{other[1]}/{other[0]}")

    first = today - dt.timedelta(days=hd - 1)
    data = json.loads(OUT.read_text(encoding="utf-8"))
    starts = {(s["year"], s["month"]): s for s in data["starts"]}
    old = starts.get((hy, hm))
    if old and old["first"] != first.isoformat():
        print(f"::warning::{hy}/{hm} moved from {old['first']} to {first}")
    if not old or old["first"] != first.isoformat():
        starts[(hy, hm)] = {"year": hy, "month": hm, "first": first.isoformat(), "seen": today.isoformat()}
    data["starts"] = [starts[k] for k in sorted(starts)]
    data["checked"] = today.isoformat()
    tmp = OUT.with_suffix(".part")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(OUT)
    print(f"{today}: {hd}/{hm}/{hy}, month started {first}")


if __name__ == "__main__":
    main()
