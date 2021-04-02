#!/usr/bin/env python3
import json
import os
import sys
import time

from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from deluge_client import DelugeRPCClient

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY


@lru_cache()
def get_libtorrent_metrics_meta():
    # https://www.libtorrent.org/manual-ref.html#session-statistics
    type_map = {
        "counter": CounterMetricFamily,
        "gauge": GaugeMetricFamily,
    }
    # Load from pre-generated file to avoid libtorrent dependency at runtime
    with (Path(__file__).parent / "libtorrent_metrics.json").open() as f:
        return {n: type_map[t] for n, t in json.load(f)["metrics"].items()}


def new_metric_with_labels_and_value(metric, name, documentation, labels, value):
    assert isinstance(labels, dict)
    m = metric(name, documentation, labels=labels.keys())
    m.add_metric(labels.values(), value)
    return m


def get_deluge_config_dir():
    if sys.platform == "win32":
        return Path(os.environ["APPDATA"]) / "deluge"
    return Path.home() / ".config" / "deluge"


def generate_per_torrent_metrics(definition):
    for metric_type, metric_name, metric_description in definition:
        # Remove total_ prefix from counters because prometheus suffixes all
        # counters with _total.
        exported_metric_name = metric_name.decode("utf-8")
        if exported_metric_name.startswith("total_") and metric_type == CounterMetricFamily:
            exported_metric_name = exported_metric_name[6:]

        yield (metric_name, metric_type(f"deluge_torrent_{exported_metric_name}", metric_description, labels=["name", "hash"]))


class DelugeCollector:
    def __init__(self):
        if all(x in os.environ for x in ["DELUGE_HOST", "DELUGE_PORT", "DELUGE_USER", "DELUGE_PASSWORD"]):
            self.rpc_host = os.environ["DELUGE_HOST"]
            self.rpc_port = int(os.environ["DELUGE_PORT"])
            self.rpc_user = os.environ["DELUGE_USER"]
            self.rpc_password = os.environ["DELUGE_PASSWORD"]
        else:
            deluge_config_dir = Path(os.environ.get("DELUGE_CONFIG_DIR", get_deluge_config_dir()))
            with (deluge_config_dir / "core.conf").open() as f:
                while f.read(1) != "}":
                    pass
                self.rpc_port = json.load(f)["daemon_port"]
            with Path(deluge_config_dir / "auth").open() as f:
                self.rpc_user, self.rpc_password = f.readline().strip().split(":")[:2]

            self.rpc_host = os.environ.get("DELUGE_HOST", "127.0.0.1")

        self.per_torrent_metrics_enabled = int(os.environ.get("PER_TORRENT_METRICS", 0)) == 1

    def collect(self):
        client = DelugeRPCClient(self.rpc_host, self.rpc_port, self.rpc_user, self.rpc_password)
        client.connect()

        libtorrent_metrics = get_libtorrent_metrics_meta()
        libtorrent_metric_values = client.call("core.get_session_status", [])

        for metric, metric_type in libtorrent_metrics.items():
            encoded_name = metric.encode("ascii")
            if encoded_name in libtorrent_metric_values:
                yield metric_type("deluge_libtorrent_{}".format(metric.replace(".", "_")), f"libtorrent metric {metric}", value=libtorrent_metric_values[encoded_name])

        yield new_metric_with_labels_and_value(
            GaugeMetricFamily,
            "deluge_info",
            "Deluge information",
            labels={
                "version": client.call("daemon.info").decode("utf-8"),
                "libtorrent_version": client.call("core.get_libtorrent_version").decode("utf-8"),
            },
            value=1,
        )

        for key, value in client.call("core.get_config").items():
            if isinstance(value, (int, float, bool)):
                yield GaugeMetricFamily("deluge_config_{}".format(key.decode("utf-8")), "Value of the deluge config setting {}".format(key.decode("utf-8")), value=value)

        torrents_by_state = {
            "downloading": 0,
            "seeding": 0,
            "paused": 0,
            "checking": 0,
            "queued": 0,
            "error": 0,
            "active": 0,
            # not the prometheus way, but the states above (as defined by deluge) are already overlapping, so sum() over them is already meaningless
            "total": 0,
        }
        torrents_by_label = defaultdict(int)
        for torrent in client.core.get_torrents_status({}, [b"label", b"state", b"download_payload_rate", b"upload_payload_rate"]).values():
            if b"label" in torrent:
                torrents_by_label[torrent[b"label"].decode("utf-8")] += 1
            torrents_by_state[torrent[b"state"].decode("utf-8").lower()] += 1
            torrents_by_state["total"] += 1
            if torrent[b"download_payload_rate"] > 0 or torrent[b"upload_payload_rate"] > 0:
                torrents_by_state["active"] += 1

        if len(torrents_by_label) > 0:
            torrents_by_label_metric = GaugeMetricFamily("deluge_torrents_by_label", "The number of torrents for each label assigned to a torrent using the deluge label plugin", labels=["label"])
            for label, count in torrents_by_label.items():
                torrents_by_label_metric.add_metric([label], count)
            yield torrents_by_label_metric

        torrents_metric = GaugeMetricFamily("deluge_torrents", "The number of torrents in a specific state (note: some states overlap)", labels=["state"])
        for state, torrent_count in torrents_by_state.items():
            torrents_metric.add_metric([state], torrent_count)
        yield torrents_metric

        if self.per_torrent_metrics_enabled:
            per_torrent_keys = [
                (CounterMetricFamily, b"total_done", "The amount of data downloaded for this torrent"),
                (CounterMetricFamily, b"total_size", "The size of this torrent"),
                (CounterMetricFamily, b"total_uploaded", "The amount of data uploaded for this torrent"),
                (GaugeMetricFamily, b"num_peers", "The number of peers currently connected to for this torrent"),
                (GaugeMetricFamily, b"num_seeds", "The number of seeds currently connected to for this torrent"),
                (GaugeMetricFamily, b"total_peers", "The number of peers in the swarm for this torrent"),
                (GaugeMetricFamily, b"total_seeds", "The number of seeds in the swarm for this torrent"),
            ]
            per_torrent_metrics = dict(generate_per_torrent_metrics(per_torrent_keys))

            for torrent_hash, torrent in client.core.get_torrents_status({}, [key[1] for key in per_torrent_keys] + [b"name"]).items():
                for metric_name, metric in per_torrent_metrics.items():
                    metric.add_metric([torrent[b"name"].decode("utf-8"), torrent_hash.decode("utf-8")], torrent[metric_name])

            for metric in per_torrent_metrics.values():
                yield metric

        client.disconnect()


def start_exporter():
    REGISTRY.register(DelugeCollector())
    port = int(os.environ.get("LISTEN_PORT", 9354))
    address = os.environ.get("LISTEN_ADDRESS", "")
    start_http_server(port, address)


if __name__ == "__main__":
    start_exporter()
    while True:
        time.sleep(60)
