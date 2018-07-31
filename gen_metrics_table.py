#!/usr/bin/env python3
"""
Script to generate a markdown table of all exposed metrics for README.md.
"""

import argparse
import requests

from collections import defaultdict
from functools import reduce
from operator import methodcaller


def get_metrics(text):
  res = defaultdict(dict)
  for l in text.strip().splitlines():
    p = l.split(' ', 3)
    if l.split()[1] in ('HELP', 'TYPE') and p[2].startswith('deluge_'):
      res[p[2]][p[1].lower()] = p[3]
  return dict(res)


def compose(f, g):
  return lambda *a, **kwa: f(g(*a, **kwa))


ap = argparse.ArgumentParser(allow_abbrev=False)
ap.add_argument('metrics_url', help='URL to running instance to use')
args = ap.parse_args()

r = requests.get(args.metrics_url)

metrics = get_metrics(r.text)
mws = list(reduce(lambda x, y: map(max, zip(x, y)), map(lambda x: map(compose(len, methodcaller('replace', '_', r'\_')), [x[0], x[1]['type'], x[1]['help']]), metrics.items())))

print(f"| {'Name':{mws[0]}} | {'Type':{mws[1]}} | {'Description':{mws[2]}} |")
print(f"| {'-'*mws[0]} | {'-'*mws[1]} | {'-'*mws[2]} |")
for metric, info in metrics.items():
  m = metric.replace('_', r'\_')
  t = info['type'].replace('_', r'\_')
  h = info['help'].replace('_', r'\_')
  print(f'| {m:{mws[0]}} | {t:{mws[1]}} | {h:{mws[2]}} |')
