
FILES=deluge_exporter.py deluge_exporter_windows_service.py gen_libtorrent_metrics_json.py gen_metrics_table.py

format:
	pyupgrade --py36-plus --exit-zero-even-if-changed $(FILES)
	black -l 1000 $(FILES)
