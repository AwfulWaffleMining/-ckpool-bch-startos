#!/usr/bin/env python3
"""Minimal stats web server for CKPool BCH — reads ckpool log files."""
import http.server, json, os, glob, html, re

LOG_DIR = '/data/ckpool/logs'
PORT = 8080

def read_stats():
    stats = {'workers': [], 'blocks': 0, 'pool_hashrate': '—'}
    if not os.path.isdir(LOG_DIR):
        return stats
    # Read worker stats from per-worker log files
    for wf in glob.glob(os.path.join(LOG_DIR, '*.log')):
        name = os.path.basename(wf).replace('.log', '')
        if name in ('ckpool', 'listener', 'generator'):
            continue
        try:
            with open(wf, 'r') as f:
                lines = f.readlines()
            last = next((l for l in reversed(lines) if l.strip()), '')
            stats['workers'].append({'name': html.escape(name), 'last': html.escape(last.strip()[:120])})
        except Exception:
            pass
    # Count block finds
    pool_log = os.path.join(LOG_DIR, 'ckpool.log')
    if os.path.exists(pool_log):
        try:
            with open(pool_log, 'r') as f:
                content = f.read()
            stats['blocks'] = content.count('Solved block')
        except Exception:
            pass
    return stats

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args): pass  # suppress access logs
    def do_GET(self):
        s = read_stats()
        workers_html = ''.join(
            f'<tr><td>{w["name"]}</td><td style="color:#aaa;font-size:11px">{w["last"]}</td></tr>'
            for w in s['workers']
        ) or '<tr><td colspan="2" style="color:#666">No miners connected yet</td></tr>'
        body = f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<title>CKPool BCH</title>
<meta http-equiv="refresh" content="30">
<style>
body{{background:#111;color:#eee;font-family:monospace;padding:24px;max-width:800px;margin:0 auto}}
h1{{color:#00ff88;letter-spacing:2px;font-size:18px}}
.stat{{background:#1a1a1a;border:1px solid #333;border-radius:6px;padding:16px;margin:12px 0}}
.label{{font-size:10px;color:#666;text-transform:uppercase;letter-spacing:1px}}
.val{{font-size:24px;font-weight:bold;color:#00ff88}}
table{{width:100%;border-collapse:collapse;margin-top:8px}}
td{{padding:8px;border-bottom:1px solid #222;vertical-align:top}}
td:first-child{{color:#00ff88;white-space:nowrap}}
</style></head><body>
<h1>⛏ CKPool BCH — Solo Mining Stats</h1>
<div class="stat"><div class="label">Miners Connected</div><div class="val">{len(s["workers"])}</div></div>
<div class="stat"><div class="label">Blocks Found</div><div class="val">{s["blocks"]}</div></div>
<div class="stat"><div class="label">Active Workers</div>
<table><tr><th style="text-align:left;color:#666;font-size:10px">WORKER</th><th style="text-align:left;color:#666;font-size:10px">LAST LOG</th></tr>
{workers_html}</table></div>
<p style="color:#444;font-size:10px">Refreshes every 30s · Stratum: port 4444 · Worker name = your BCH address</p>
</body></html>'''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(body.encode())

if __name__ == '__main__':
    with http.server.HTTPServer(('0.0.0.0', PORT), Handler) as srv:
        srv.serve_forever()
