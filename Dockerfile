FROM python:alpine
RUN pip install deluge-client prometheus_client
COPY ./deluge_exporter.py /deluge_exporter.py
COPY ./libtorrent_metrics.json /libtorrent_metrics.json
EXPOSE 9354
ENTRYPOINT ["/usr/local/bin/python", "/deluge_exporter.py"]
