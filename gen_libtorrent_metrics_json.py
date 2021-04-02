#!/usr/bin/env python3

import json

from pathlib import Path

import libtorrent


def main():
    d = Path(__file__).parent

    metrics = dict(sorted([(x.name, x.type.name) for x in libtorrent.session_stats_metrics()]))

    j = {
        "version": libtorrent.__version__,
        "metrics": metrics,
    }

    with (d / "libtorrent_metrics.json").open("w") as f:
        json.dump(j, f, indent=2)


if __name__ == "__main__":
    main()
