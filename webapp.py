"""
webapp.py
Flask UI + JSON API exposing devices, metrics and alerts.

Routes:
- /              -> simple HTML dashboard summary
- /api/devices   -> list of devices monitored
- /api/metrics/<host> -> recent metrics (JSON)
- /api/alerts    -> recent alerts (JSON)
"""

from flask import Flask, jsonify, render_template_string, request
from database import recentAlerts, recentMetrics
import database

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html>
<head><title>NetHealth Monitor</title></head>
<body>
  <h1>NetHealth Monitor</h1>
  <p>Monitored devices: {{ deviceCount }}</p>
  <h2>Recent Alerts</h2>
  <ul>
  {% for a in alerts %}
    <li>[{{ a[1] }}] {{ a[3] }} (ts: {{ a[2] }})</li>
  {% endfor %}
  </ul>
  <p>Use the API endpoints /api/devices, /api/metrics/&lt;host&gt;, /api/alerts</p>
</body>
</html>
"""


@app.route("/")
def index():
    alerts = recentAlerts(10)
    # device count is approximate (not stored here)
    deviceCount = "see /api/devices"
    return render_template_string(TEMPLATE, alerts=alerts, deviceCount=deviceCount)


@app.route("/api/alerts")
def apiAlerts():
    limit = int(request.args.get("limit", "50"))
    rows = recentAlerts(limit)
    # rows: id, severity, ts, message
    return jsonify([{"id": r[0], "severity": r[1], "ts": r[2], "message": r[3]} for r in rows])


@app.route("/api/metrics/<host>")
def apiMetrics(host):
    limit = int(request.args.get("limit", "100"))
    rows = recentMetrics(host, limit)
    # rows: ts, ifIndex, inBytes, outBytes
    data = [{"ts": r[0], "ifIndex": r[1], "inBytes": r[2], "outBytes": r[3]}
            for r in rows]
    return jsonify({"host": host, "metrics": data})
