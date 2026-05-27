#!/usr/bin/env python3
"""CKPool BCH stats web server — reads ckpool log files and serves a dashboard."""
import http.server, json, os, glob, html, re, time

LOG_DIR  = '/data/ckpool/logs'
PORT     = 8080
STRATUM  = 'stratum+tcp://[your-node-address]:4444'

SKIP = {'ckpool', 'listener', 'generator', 'stratifier', 'connector', 'ckdb'}

# ── Parse ckpool worker log files ─────────────────────────────────────────────

def parse_worker(path):
    name = os.path.basename(path).replace('.log', '')
    w = {'name': name, 'accepted': 0, 'rejected': 0, 'stale': 0,
         'diff': 0, 'dsps': 0.0, 'status': 'active'}
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
        # Find the most recent JSON line
        for line in reversed(lines):
            line = line.strip()
            if line.startswith('{'):
                try:
                    d = json.loads(line)
                    w['accepted'] = d.get('accepted', 0)
                    w['rejected'] = d.get('rejected', 0)
                    w['stale']    = d.get('stale', 0)
                    w['diff']     = d.get('diff', 0)
                    w['dsps']     = d.get('dsps', 0.0)
                    break
                except Exception:
                    pass
        # Check if recently active (file modified in last 10 min)
        mtime = os.path.getmtime(path)
        if time.time() - mtime > 600:
            w['status'] = 'offline'
    except Exception:
        pass
    return w

def read_stats():
    workers = []
    blocks  = 0

    if os.path.isdir(LOG_DIR):
        for wf in sorted(glob.glob(os.path.join(LOG_DIR, '*.log'))):
            name = os.path.basename(wf).replace('.log', '')
            if name.lower() in SKIP:
                continue
            workers.append(parse_worker(wf))

        # Count blocks from pool log
        pool_log = os.path.join(LOG_DIR, 'ckpool.log')
        if os.path.exists(pool_log):
            try:
                with open(pool_log, 'r') as f:
                    blocks = f.read().count('Solved block')
            except Exception:
                pass

    active  = sum(1 for w in workers if w['status'] == 'active')
    offline = sum(1 for w in workers if w['status'] == 'offline')
    total_accepted = sum(w['accepted'] for w in workers)
    total_rejected = sum(w['rejected'] for w in workers)
    total_stale    = sum(w['stale']    for w in workers)
    total_hashrate = sum(w['dsps'] * w['diff'] for w in workers)  # hashes/sec approx

    def fmt_hs(hs):
        if hs >= 1e12: return f'{hs/1e12:.2f} TH/s'
        if hs >= 1e9:  return f'{hs/1e9:.2f} GH/s'
        if hs >= 1e6:  return f'{hs/1e6:.2f} MH/s'
        return f'{hs:.0f} H/s'

    reject_pct = (total_rejected / max(1, total_accepted + total_rejected)) * 100

    return {
        'workers': workers, 'blocks': blocks,
        'active': active, 'offline': offline,
        'total_accepted': total_accepted, 'total_rejected': total_rejected,
        'total_stale': total_stale,
        'hashrate': fmt_hs(total_hashrate),
        'reject_pct': f'{reject_pct:.2f}%',
    }

# ── HTML pages ────────────────────────────────────────────────────────────────

CSS = '''
* { box-sizing: border-box; margin: 0; padding: 0 }
body { background: #0d0d0d; color: #eee; font-family: -apple-system, monospace; padding: 24px; }
.top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
h1 { color: #00ff88; font-size: 18px; letter-spacing: 2px; }
.how-link { color: #00ff88; font-size: 12px; text-decoration: none; border: 1px solid #00ff8844; padding: 6px 14px; border-radius: 4px; }
.how-link:hover { background: #00ff8811; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
@media(max-width: 700px) { .grid { grid-template-columns: 1fr; } }
.card { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 8px; padding: 20px; }
.card-title { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot-green { background: #00ff88; }
.dot-purple { background: #a855f7; }
.dot-blue { background: #3b82f6; }
.stat-row { display: flex; gap: 24px; margin-bottom: 8px; }
.stat { flex: 1; }
.stat-val { font-size: 28px; font-weight: 700; color: #00ff88; }
.stat-label { font-size: 10px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }
.sub-val { font-size: 13px; color: #e55; margin-top: 12px; }
.sub-label { font-size: 10px; color: #666; text-transform: uppercase; letter-spacing: 1px; }
.worker-circle { width: 80px; height: 80px; border-radius: 50%; border: 4px solid #00ff88; display: flex; align-items: center; justify-content: center; flex-direction: column; margin-bottom: 12px; }
.circle-num { font-size: 22px; font-weight: 700; color: #00ff88; }
.circle-label { font-size: 9px; color: #666; }
.worker-legend { font-size: 12px; color: #aaa; }
.worker-legend span { display: block; margin-bottom: 4px; }
.table-wrap { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 8px; padding: 20px; }
.table-title { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 14px; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th { text-align: left; color: #555; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; padding: 8px 0; border-bottom: 1px solid #2a2a2a; }
td { padding: 10px 0; border-bottom: 1px solid #1e1e1e; color: #aaa; }
td:first-child { color: #00ff88; word-break: break-all; }
.badge { font-size: 9px; padding: 2px 6px; border-radius: 3px; font-weight: bold; }
.badge-active { background: #00ff8822; color: #00ff88; border: 1px solid #00ff8844; }
.badge-offline { background: #ff555522; color: #ff8888; border: 1px solid #ff555544; }
.footer { margin-top: 20px; color: #444; font-size: 10px; text-align: center; }
'''

def dashboard_html(s):
    worker_rows = ''.join(f'''
    <tr>
      <td>{html.escape(w["name"])}</td>
      <td>{w["accepted"]:,}</td>
      <td>{w["stale"]}</td>
      <td>{w["rejected"]}</td>
      <td><span class="badge badge-{w["status"]}">{w["status"].upper()}</span></td>
    </tr>''' for w in s['workers']
    ) or '<tr><td colspan="5" style="color:#555;text-align:center;padding:20px">No miners connected yet</td></tr>'

    return f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<title>CKPool BCH</title><meta http-equiv="refresh" content="30">
<style>{CSS}</style></head><body>
<div class="top">
  <h1>⛏ CKPool BCH — Solo Mining</h1>
  <a class="how-link" href="/connect">How to Connect →</a>
</div>
<div class="grid">
  <div class="card">
    <div class="card-title"><span class="dot dot-blue"></span>Account Info <span style="font-size:9px;background:#1e3a2a;color:#00ff88;padding:2px 6px;border-radius:3px;margin-left:auto">SOLO</span></div>
    <div class="stat-val">{s["total_accepted"]:,}</div>
    <div class="stat-label" style="margin-bottom:12px">valid shares submitted</div>
    <div style="display:flex;gap:24px">
      <div><div class="sub-val">{s["total_stale"]}</div><div class="sub-label">Stale</div></div>
      <div><div class="sub-val">{s["total_rejected"]}</div><div class="sub-label">Invalid</div></div>
      <div><div class="sub-val" style="color:#00ff88">{s["blocks"]}</div><div class="sub-label">Blocks Found</div></div>
    </div>
  </div>
  <div class="card">
    <div class="card-title"><span class="dot dot-green"></span>Hashrate</div>
    <div class="stat-val">{s["hashrate"]}</div>
    <div class="stat-label" style="margin-bottom:12px">current speed</div>
    <div style="display:flex;gap:24px">
      <div><div style="color:#00ff88;font-size:13px">{s["hashrate"]}</div><div class="sub-label">Average</div></div>
      <div><div style="color:#e55;font-size:13px">{s["reject_pct"]}</div><div class="sub-label">Rejection</div></div>
    </div>
  </div>
  <div class="card">
    <div class="card-title"><span class="dot dot-purple"></span>Workers</div>
    <div style="display:flex;align-items:center;gap:20px">
      <div class="worker-circle">
        <div class="circle-num">{s["active"] + s["offline"]}</div>
        <div class="circle-label">TOTAL</div>
      </div>
      <div class="worker-legend">
        <span style="color:#00ff88">● {s["active"]} Active</span>
        <span style="color:#f59e0b">● {s["offline"]} Offline</span>
      </div>
    </div>
  </div>
</div>
<div class="table-wrap">
  <div class="table-title">Active Workers</div>
  <table>
    <tr><th>Worker (BCH Address)</th><th>Accepted</th><th>Stale</th><th>Rejected</th><th>Status</th></tr>
    {worker_rows}
  </table>
</div>
<div class="footer">Auto-refreshes every 30s &nbsp;·&nbsp; Stratum port 4444 &nbsp;·&nbsp; Worker name = your BCH payout address</div>
</body></html>'''

def connect_html():
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<title>How to Connect — CKPool BCH</title>
<style>{CSS}
.back {{ color: #00ff88; font-size: 12px; text-decoration: none; }}
.step {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 8px; padding: 20px; margin-bottom: 16px; }}
.step-num {{ color: #00ff88; font-size: 11px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; }}
code {{ background: #0d0d0d; border: 1px solid #2a2a2a; padding: 3px 8px; border-radius: 3px; font-size: 13px; color: #00ff88; }}
.copy-box {{ background: #0d0d0d; border: 1px solid #00ff8844; border-radius: 6px; padding: 14px; font-size: 13px; color: #00ff88; word-break: break-all; margin-top: 8px; }}
</style></head><body>
<div class="top">
  <h1>⛏ How to Connect</h1>
  <a class="back" href="/">← Dashboard</a>
</div>
<div class="step">
  <div class="step-num">Step 1 — Get your node's Stratum address</div>
  <p style="color:#aaa;font-size:13px;margin-bottom:8px">
    In StartOS, open CKPool BCH → Service Interfaces → Stratum Mining. Copy the address shown.
    It will look like: <code>192.168.x.x:4444</code> or a Tor/clearnet address.
  </p>
</div>
<div class="step">
  <div class="step-num">Step 2 — Configure your miner</div>
  <p style="color:#aaa;font-size:13px;margin-bottom:10px">Set the following in your miner's pool settings:</p>
  <table style="font-size:13px;width:100%">
    <tr><td style="color:#666;padding:6px 0;width:140px">Pool URL</td><td><code>stratum+tcp://[your-node-address]:4444</code></td></tr>
    <tr><td style="color:#666;padding:6px 0">Worker / Username</td><td><code>bitcoincash:your_bch_address_here</code></td></tr>
    <tr><td style="color:#666;padding:6px 0">Password</td><td><code>x</code> (any value)</td></tr>
  </table>
</div>
<div class="step">
  <div class="step-num">Step 3 — Start mining</div>
  <p style="color:#aaa;font-size:13px">
    Your miner will appear in the Active Workers table on the dashboard within a few minutes.
    Any block found pays the full reward directly to the BCH address you set as your worker name.
    <strong style="color:#00ff88">No pool fees. 100% of the block reward is yours.</strong>
  </p>
</div>
<div class="step">
  <div class="step-num">Supported hardware</div>
  <p style="color:#aaa;font-size:13px">Any SHA-256 ASIC miner: Bitmain Antminer S-series, MicroBT Whatsminer M-series, and compatible hardware.</p>
</div>
<a class="back" href="/">← Return to Dashboard</a>
</body></html>'''

# ── HTTP handler ──────────────────────────────────────────────────────────────

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_GET(self):
        if self.path == '/connect':
            body = connect_html()
        else:
            body = dashboard_html(read_stats())
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(body.encode())

if __name__ == '__main__':
    print(f'[stats] Starting web UI on port {PORT}')
    with http.server.HTTPServer(('0.0.0.0', PORT), Handler) as srv:
        srv.serve_forever()
