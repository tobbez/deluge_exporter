# Deluge Exporter

Prometheus exporter for the [Deluge](https://deluge-torrent.org/) BitTorrent client.


## Requirements

 * Python 3
 * [prometheus\_client](https://github.com/prometheus/client_python)
 * [deluge-client](https://github.com/JohnDoee/deluge-client)


## Notes
### State
The project is generally considered complete. However, there are a number of
areas that could be improved, and contributions are welcome. Some areas that
could use improvements are:

 - [ ] Packaging: There are currently no packaging scripts nor PyPI packages
 - [ ] Configuration


### Configuration
There is currently no explicit configuration. The Deluge Exporter currently
expects to be run under the same user account as the deluge daemon, and
extracts the connection details from Deluge's configuration files.

The exporter listens on port 9354.

### Per-torrent metrics
Per-torrent metrics are not included by design. They are not particularly
useful, and would cause series bloat.

A contribution adding them would be accepted assuming it would be opt-in (by
command line flag or configuration option).


### libtorrent metrics in Deluge 2
Once Deluge 2 is released, the libtorrent metrics need to be updated to expose the
newer [performance/statistics counters](https://www.libtorrent.org/manual-ref.html#session-statistics).

Deluge 1.3.x only exposes the statistics provided by the deprecated
`session_get_status()`.

## Docker

A docker image is [available on Docker Hub](https://hub.docker.com/r/tobbez/deluge_exporter/).

It currently requires passing the deluge config directory into the container, [for example](https://github.com/tobbez/deluge_exporter/pull/1#issue-229784499):

```
docker run -e "DELUGE_HOST=172.17.0.1" -v /etc/deluge:/root/.config/deluge/ -p 9354:9354 tobbez/deluge_exporter:latest
```

## Exported metrics

| Name                                                  | Type    | Description                                                                                                                                                   |
| ----------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| deluge\_libtorrent\_has\_incoming\_connections        | gauge   | 0 as long as no incoming connections have been established on the listening socket. Every time you change the listen port, this will be reset to 0.           |
| deluge\_libtorrent\_redundant\_download\_bytes\_total | counter | The number of bytes that has been received more than once.                                                                                                    |
| deluge\_libtorrent\_failed\_bytes\_total              | counter | The number of bytes that were downloaded and later failed the hash check.                                                                                     |
| deluge\_libtorrent\_peers                             | gauge   | Current number of peer connections in the current session, including connections that are not yet fully open.                                                 |
| deluge\_libtorrent\_unchoked\_peers                   | gauge   | The current number of unchoked peers.                                                                                                                         |
| deluge\_libtorrent\_allowed\_upload\_slots            | gauge   | The current allowed number of unchoked peers.                                                                                                                 |
| deluge\_libtorrent\_upload\_queued\_peers             | gauge   | The number of peers that are waiting for more bandwidth quota from the torrent rate limiter.                                                                  |
| deluge\_libtorrent\_download\_queued\_peers           | gauge   | The number of peers that are waiting for more bandwidth quota from the torrent rate limiter.                                                                  |
| deluge\_libtorrent\_upload\_queued\_bytes             | gauge   | The number of bytes the queued connections are waiting for to be able to send.                                                                                |
| deluge\_libtorrent\_download\_queued\_bytes           | gauge   | The number of bytes the queued connections are waiting for to be able to receive.                                                                             |
| deluge\_libtorrent\_dht\_nodes                        | gauge   | The number of nodes in the DHT routing table.                                                                                                                 |
| deluge\_libtorrent\_dht\_cached\_nodes                | gauge   | The number of cached DHT nodes (used to replace the regular nodes in the routing table in case any of them becomes unresponsive).                             |
| deluge\_libtorrent\_dht\_torrents                     | gauge   | The number of torrents tracked by the DHT at the moment.                                                                                                      |
| deluge\_libtorrent\_dht\_estimated\_global\_nodes     | gauge   | An estimation of the total number of nodes in the DHT network.                                                                                                |
| deluge\_libtorrent\_dht\_total\_allocations           | gauge   | The number of nodes allocated dynamically for a particular DHT lookup. This represents roughly the amount of memory used by the DHT.                          |
| deluge\_libtorrent\_upload\_bytes\_total              | counter | Total bytes uploaded for all torrents. (labels: {type=dht\|ip\_overhead\|payload\|tracker})                                                                   |
| deluge\_libtorrent\_download\_bytes\_total            | counter | Total bytes downloaded for all torrents. (labels: {type=dht\|ip\_overhead\|payload\|tracker})                                                                 |
| deluge\_info                                          | gauge   | Deluge information (labels: {libtorrent\_version=, version=})                                                                                                 |
| deluge\_config\_info\_sent                            | gauge   | Value of the deluge config setting info\_sent                                                                                                                 |
| deluge\_config\_lsd                                   | gauge   | Value of the deluge config setting lsd                                                                                                                        |
| deluge\_config\_send\_info                            | gauge   | Value of the deluge config setting send\_info                                                                                                                 |
| deluge\_config\_enc\_in\_policy                       | gauge   | Value of the deluge config setting enc\_in\_policy                                                                                                            |
| deluge\_config\_queue\_new\_to\_top                   | gauge   | Value of the deluge config setting queue\_new\_to\_top                                                                                                        |
| deluge\_config\_ignore\_limits\_on\_local\_network    | gauge   | Value of the deluge config setting ignore\_limits\_on\_local\_network                                                                                         |
| deluge\_config\_rate\_limit\_ip\_overhead             | gauge   | Value of the deluge config setting rate\_limit\_ip\_overhead                                                                                                  |
| deluge\_config\_daemon\_port                          | gauge   | Value of the deluge config setting daemon\_port                                                                                                               |
| deluge\_config\_natpmp                                | gauge   | Value of the deluge config setting natpmp                                                                                                                     |
| deluge\_config\_max\_active\_limit                    | gauge   | Value of the deluge config setting max\_active\_limit                                                                                                         |
| deluge\_config\_utpex                                 | gauge   | Value of the deluge config setting utpex                                                                                                                      |
| deluge\_config\_max\_active\_downloading              | gauge   | Value of the deluge config setting max\_active\_downloading                                                                                                   |
| deluge\_config\_max\_active\_seeding                  | gauge   | Value of the deluge config setting max\_active\_seeding                                                                                                       |
| deluge\_config\_allow\_remote                         | gauge   | Value of the deluge config setting allow\_remote                                                                                                              |
| deluge\_config\_max\_half\_open\_connections          | gauge   | Value of the deluge config setting max\_half\_open\_connections                                                                                               |
| deluge\_config\_compact\_allocation                   | gauge   | Value of the deluge config setting compact\_allocation                                                                                                        |
| deluge\_config\_max\_upload\_speed                    | gauge   | Value of the deluge config setting max\_upload\_speed                                                                                                         |
| deluge\_config\_cache\_expiry                         | gauge   | Value of the deluge config setting cache\_expiry                                                                                                              |
| deluge\_config\_prioritize\_first\_last\_pieces       | gauge   | Value of the deluge config setting prioritize\_first\_last\_pieces                                                                                            |
| deluge\_config\_auto\_managed                         | gauge   | Value of the deluge config setting auto\_managed                                                                                                              |
| deluge\_config\_enc\_level                            | gauge   | Value of the deluge config setting enc\_level                                                                                                                 |
| deluge\_config\_max\_connections\_per\_second         | gauge   | Value of the deluge config setting max\_connections\_per\_second                                                                                              |
| deluge\_config\_dont\_count\_slow\_torrents           | gauge   | Value of the deluge config setting dont\_count\_slow\_torrents                                                                                                |
| deluge\_config\_random\_outgoing\_ports               | gauge   | Value of the deluge config setting random\_outgoing\_ports                                                                                                    |
| deluge\_config\_max\_upload\_slots\_per\_torrent      | gauge   | Value of the deluge config setting max\_upload\_slots\_per\_torrent                                                                                           |
| deluge\_config\_new\_release\_check                   | gauge   | Value of the deluge config setting new\_release\_check                                                                                                        |
| deluge\_config\_enc\_out\_policy                      | gauge   | Value of the deluge config setting enc\_out\_policy                                                                                                           |
| deluge\_config\_seed\_time\_limit                     | gauge   | Value of the deluge config setting seed\_time\_limit                                                                                                          |
| deluge\_config\_cache\_size                           | gauge   | Value of the deluge config setting cache\_size                                                                                                                |
| deluge\_config\_share\_ratio\_limit                   | gauge   | Value of the deluge config setting share\_ratio\_limit                                                                                                        |
| deluge\_config\_max\_download\_speed                  | gauge   | Value of the deluge config setting max\_download\_speed                                                                                                       |
| deluge\_config\_stop\_seed\_at\_ratio                 | gauge   | Value of the deluge config setting stop\_seed\_at\_ratio                                                                                                      |
| deluge\_config\_upnp                                  | gauge   | Value of the deluge config setting upnp                                                                                                                       |
| deluge\_config\_max\_download\_speed\_per\_torrent    | gauge   | Value of the deluge config setting max\_download\_speed\_per\_torrent                                                                                         |
| deluge\_config\_max\_upload\_slots\_global            | gauge   | Value of the deluge config setting max\_upload\_slots\_global                                                                                                 |
| deluge\_config\_random\_port                          | gauge   | Value of the deluge config setting random\_port                                                                                                               |
| deluge\_config\_autoadd\_enable                       | gauge   | Value of the deluge config setting autoadd\_enable                                                                                                            |
| deluge\_config\_max\_connections\_global              | gauge   | Value of the deluge config setting max\_connections\_global                                                                                                   |
| deluge\_config\_enc\_prefer\_rc4                      | gauge   | Value of the deluge config setting enc\_prefer\_rc4                                                                                                           |
| deluge\_config\_dht                                   | gauge   | Value of the deluge config setting dht                                                                                                                        |
| deluge\_config\_stop\_seed\_ratio                     | gauge   | Value of the deluge config setting stop\_seed\_ratio                                                                                                          |
| deluge\_config\_seed\_time\_ratio\_limit              | gauge   | Value of the deluge config setting seed\_time\_ratio\_limit                                                                                                   |
| deluge\_config\_max\_upload\_speed\_per\_torrent      | gauge   | Value of the deluge config setting max\_upload\_speed\_per\_torrent                                                                                           |
| deluge\_config\_copy\_torrent\_file                   | gauge   | Value of the deluge config setting copy\_torrent\_file                                                                                                        |
| deluge\_config\_del\_copy\_torrent\_file              | gauge   | Value of the deluge config setting del\_copy\_torrent\_file                                                                                                   |
| deluge\_config\_move\_completed                       | gauge   | Value of the deluge config setting move\_completed                                                                                                            |
| deluge\_config\_add\_paused                           | gauge   | Value of the deluge config setting add\_paused                                                                                                                |
| deluge\_config\_max\_connections\_per\_torrent        | gauge   | Value of the deluge config setting max\_connections\_per\_torrent                                                                                             |
| deluge\_config\_remove\_seed\_at\_ratio               | gauge   | Value of the deluge config setting remove\_seed\_at\_ratio                                                                                                    |
| deluge\_torrents\_by\_label                           | gauge   | The number of torrents for each label assigned to a torrent using the deluge label plugin (labels: {label=})                                                  |
| deluge\_torrents                                      | gauge   | The number of torrents in a specific state (note: some states overlap) (labels: {state=active\|checking\|downloading\|error\|paused\|queued\|seeding\|total}) |
