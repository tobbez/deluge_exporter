#!/usr/bin/env python3
"""
Script to generate a markdown table of all exposed metrics for README.md.
"""

import argparse
import io
import prometheus_client.parser
import requests

from collections import defaultdict
from functools import reduce
from operator import methodcaller


def get_metrics(text):
    res = defaultdict(dict)
    for ln in text.strip().splitlines():
        p = ln.split(" ", 3)
        if ln.split()[1] in ("HELP", "TYPE") and p[2].startswith("deluge_"):
            res[p[2]][p[1].lower()] = p[3]
    return dict(res)


def get_labels(text):
    res = defaultdict(lambda: defaultdict(set))
    metrics = prometheus_client.parser.text_fd_to_metric_families(io.StringIO(text))
    for m in metrics:
        if not m.name.startswith("deluge_"):
            continue
        for s in m.samples:
            for ln, lv in s[1].items():
                res[s.name][ln].add(lv)
    res["deluge_torrents_by_label"]["label"] = set("")
    res["deluge_info"]["version"] = set("")
    res["deluge_info"]["libtorrent_version"] = set("")
    for key in res:
        if key.startswith("deluge_torrent_"):
            res[key]["name"] = set()
            res[key]["hash"] = set()
            # 'state' label for per-torrent metrics
            res[key]["state"] = {"downloading", "seeding", "paused", "checking", "queued", "error", "active", "moving", "allocating"}
    return res


def compose(f, g):
    return lambda *a, **kwa: f(g(*a, **kwa))


def format_labels(labels):
    return "{" + ", ".join(["{}={}".format(k, "|".join(sorted(v))) for k, v in labels.items()]) + "}"


ap = argparse.ArgumentParser(allow_abbrev=False)
ap.add_argument("metrics_url", help="URL to running instance to use")
args = ap.parse_args()

r = requests.get(args.metrics_url)

metrics = get_metrics(r.text)
for m, labels in get_labels(r.text).items():
    metrics[m]["help"] += " (labels: {})".format(format_labels(labels))
mws = list(reduce(lambda x, y: map(max, zip(x, y)), map(lambda x: map(compose(len, compose(methodcaller("replace", "|", r"\|"), methodcaller("replace", "_", r"\_"))), [x[0], x[1]["type"], x[1]["help"]]), metrics.items())))

print(f"| {'Name':{mws[0]}} | {'Type':{mws[1]}} | {'Description':{mws[2]}} |")
print(f"| {'-'*mws[0]} | {'-'*mws[1]} | {'-'*mws[2]} |")
for metric, info in metrics.items():
    m = metric.replace("_", r"\_")
    t = info["type"].replace("_", r"\_")
    h = info["help"].replace("_", r"\_").replace("|", r"\|")
    print(f"| {m:{mws[0]}} | {t:{mws[1]}} | {h:{mws[2]}} |")
