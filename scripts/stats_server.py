#!/usr/bin/env python3
"""CKPool BCH stats web server — dashboard + How to Connect page."""
import http.server, json, os, glob, html, time
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    """Handle each request in its own thread — fixes F5/concurrent spinning."""
    daemon_threads = True

LOG_DIR = '/data/ckpool/logs'
PORT    = 8080
SKIP    = {'ckpool', 'listener', 'generator', 'stratifier', 'connector', 'ckdb'}
BCH_ADDRESS = os.environ.get('BCH_PAYOUT_ADDRESS', '')

# ── Parse ckpool worker log files ─────────────────────────────────────────────

def parse_worker(path):
    name = os.path.basename(path).replace('.log', '')
    w = {'name': name, 'accepted': 0, 'rejected': 0, 'stale': 0,
         'diff': 0, 'dsps': 0.0, 'status': 'active'}
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
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
        if time.time() - os.path.getmtime(path) > 600:
            w['status'] = 'offline'
    except Exception:
        pass
    return w

def read_stats():
    workers, blocks = [], 0
    if os.path.isdir(LOG_DIR):
        for wf in sorted(glob.glob(os.path.join(LOG_DIR, '*.log'))):
            if os.path.basename(wf).replace('.log', '').lower() not in SKIP:
                workers.append(parse_worker(wf))
        pool_log = os.path.join(LOG_DIR, 'ckpool.log')
        if os.path.exists(pool_log):
            try:
                with open(pool_log, 'r') as f:
                    blocks = f.read().count('Solved block')
            except Exception:
                pass

    active  = sum(1 for w in workers if w['status'] == 'active')
    offline = sum(1 for w in workers if w['status'] == 'offline')
    tot_acc = sum(w['accepted'] for w in workers)
    tot_rej = sum(w['rejected'] for w in workers)
    tot_stl = sum(w['stale']    for w in workers)
    hs      = sum(w['dsps'] * w['diff'] for w in workers)

    def fmt(h):
        if h >= 1e12: return f'{h/1e12:.2f} TH/s'
        if h >= 1e9:  return f'{h/1e9:.2f} GH/s'
        if h >= 1e6:  return f'{h/1e6:.2f} MH/s'
        return f'{h:.0f} H/s'

    rej_pct = (tot_rej / max(1, tot_acc + tot_rej)) * 100
    return {'workers': workers, 'blocks': blocks,
            'active': active, 'offline': offline,
            'tot_acc': tot_acc, 'tot_rej': tot_rej, 'tot_stl': tot_stl,
            'hashrate': fmt(hs), 'rej_pct': f'{rej_pct:.2f}%'}

# ── Shared CSS ─────────────────────────────────────────────────────────────────

CSS = '''
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d0d0d;color:#eee;font-family:-apple-system,monospace;padding:24px}
.top{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px}
h1{color:#00ff88;font-size:18px;letter-spacing:2px}
.nav-link{color:#00ff88;font-size:12px;text-decoration:none;border:1px solid #00ff8844;padding:6px 14px;border-radius:4px}
.nav-link:hover{background:#00ff8811}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px}
@media(max-width:700px){.grid{grid-template-columns:1fr}}
.card{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;padding:20px}
.card-title{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block}
.dot-g{background:#00ff88}.dot-p{background:#a855f7}.dot-b{background:#3b82f6}
.big{font-size:28px;font-weight:700;color:#00ff88}
.lbl{font-size:10px;color:#666;text-transform:uppercase;letter-spacing:1px;margin-top:2px}
.sub-row{display:flex;gap:20px;margin-top:12px}
.sub-val{font-size:13px;color:#e55}
.sub-val.g{color:#00ff88}
.circle{width:80px;height:80px;border-radius:50%;border:4px solid #00ff88;display:flex;align-items:center;justify-content:center;flex-direction:column}
.circle-n{font-size:22px;font-weight:700;color:#00ff88}
.circle-l{font-size:9px;color:#666}
.legend span{display:block;margin-bottom:4px;font-size:12px;color:#aaa}
.table-wrap{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;padding:20px;margin-bottom:20px}
.table-title{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px}
table{width:100%;border-collapse:collapse;font-size:12px}
th{text-align:left;color:#555;font-size:10px;text-transform:uppercase;letter-spacing:1px;padding:8px 0;border-bottom:1px solid #2a2a2a}
td{padding:10px 0;border-bottom:1px solid #1e1e1e;color:#aaa}
td:first-child{color:#00ff88;word-break:break-all}
.badge{font-size:9px;padding:2px 6px;border-radius:3px;font-weight:bold}
.ba{background:#00ff8822;color:#00ff88;border:1px solid #00ff8844}
.bo{background:#ff555522;color:#f87171;border:1px solid #ff555544}
.footer{color:#444;font-size:10px;text-align:center;margin-top:16px}
/* connect page */
.step{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;padding:20px;margin-bottom:16px}
.step-num{color:#00ff88;font-size:11px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px}
code{background:#0d0d0d;border:1px solid #2a2a2a;padding:3px 8px;border-radius:3px;font-size:13px;color:#00ff88}
input[type=text]{background:#0d0d0d;border:1px solid #00ff8844;border-radius:6px;padding:10px 14px;
  font-family:monospace;font-size:13px;color:#00ff88;width:100%;outline:none;margin-top:6px}
input[type=text]:focus{border-color:#00ff88}
.cfg-table{width:100%;border-collapse:collapse;font-size:13px;margin-top:10px}
.cfg-table td{padding:8px 0;border-bottom:1px solid #1e1e1e;vertical-align:top}
.cfg-table td:first-child{color:#666;width:130px;padding-right:12px}
.cfg-val{color:#00ff88;word-break:break-all;cursor:pointer}
.cfg-val:hover{color:#fff}
.hint{font-size:10px;color:#555;margin-top:2px}
'''

# ── Dashboard page ─────────────────────────────────────────────────────────────

def dashboard_html(s):
    rows = ''.join(f'''<tr>
      <td>{html.escape(w["name"])}</td>
      <td>{w["accepted"]:,}</td><td>{w["stale"]}</td><td>{w["rejected"]}</td>
      <td><span class="badge {"ba" if w["status"]=="active" else "bo"}">{w["status"].upper()}</span></td>
    </tr>''' for w in s['workers']
    ) or '<tr><td colspan="5" style="color:#555;text-align:center;padding:20px">No miners connected yet</td></tr>'

    return f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<title>CKPool BCH</title><meta http-equiv="refresh" content="30">
<style>{CSS}</style></head><body>
<div class="top">
  <h1>⛏ CKPool BCH — Solo Mining</h1>
  <a class="nav-link" href="/connect">How to Connect →</a>
</div>
<div class="grid">
  <div class="card">
    <div class="card-title"><span class="dot dot-b"></span>Account Info
      <span style="font-size:9px;background:#1e3a2a;color:#00ff88;padding:2px 6px;border-radius:3px;margin-left:auto">SOLO</span>
    </div>
    <div class="big">{s["tot_acc"]:,}</div><div class="lbl" style="margin-bottom:12px">valid shares</div>
    <div class="sub-row">
      <div><div class="sub-val">{s["tot_stl"]}</div><div class="lbl">Stale</div></div>
      <div><div class="sub-val">{s["tot_rej"]}</div><div class="lbl">Invalid</div></div>
      <div><div class="sub-val g">{s["blocks"]}</div><div class="lbl">Blocks</div></div>
    </div>
  </div>
  <div class="card">
    <div class="card-title"><span class="dot dot-g"></span>Hashrate</div>
    <div class="big">{s["hashrate"]}</div><div class="lbl" style="margin-bottom:12px">current speed</div>
    <div class="sub-row">
      <div><div class="sub-val g">{s["hashrate"]}</div><div class="lbl">Average</div></div>
      <div><div class="sub-val">{s["rej_pct"]}</div><div class="lbl">Rejection</div></div>
    </div>
  </div>
  <div class="card">
    <div class="card-title"><span class="dot dot-p"></span>Workers</div>
    <div style="display:flex;align-items:center;gap:20px">
      <div class="circle"><div class="circle-n">{s["active"]+s["offline"]}</div><div class="circle-l">TOTAL</div></div>
      <div class="legend">
        <span style="color:#00ff88">● {s["active"]} Active</span>
        <span style="color:#f59e0b">● {s["offline"]} Offline</span>
      </div>
    </div>
  </div>
</div>
<div class="table-wrap">
  <div class="table-title">Active Workers</div>
  <table><tr><th>Worker (BCH Address)</th><th>Accepted</th><th>Stale</th><th>Rejected</th><th>Status</th></tr>
  {rows}</table>
</div>
<div class="footer">Auto-refreshes every 30s &nbsp;·&nbsp; Stratum port 4444 &nbsp;·&nbsp; Worker name = BCH address</div>
</body></html>'''

# ── How to Connect page ────────────────────────────────────────────────────────

def connect_html():
    bch = html.escape(BCH_ADDRESS) if BCH_ADDRESS else 'bitcoincash:your_bch_address'
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<title>How to Connect — CKPool BCH</title>
<style>{CSS}</style></head><body>
<div class="top">
  <h1>⛏ How to Connect</h1>
  <a class="nav-link" href="/">← Dashboard</a>
</div>

<div class="step">
  <div class="step-num">Step 1 — Enter your worker name</div>
  <p style="color:#aaa;font-size:13px;margin-bottom:10px">
    A short label to identify this miner in the dashboard (e.g. <code>miner1</code>, <code>s21-garage</code>).
  </p>
  <label style="color:#666;font-size:10px;text-transform:uppercase;letter-spacing:1px">Worker Name</label>
  <input type="text" id="workerName" placeholder="e.g. miner1" oninput="updateConfig()" autofocus>
</div>

<div class="step">
  <div class="step-num">Step 2 — Copy these settings into your miner</div>
  <p style="color:#aaa;font-size:13px;margin-bottom:6px">
    Find your Stratum URL in StartOS → CKPool BCH → Service Interfaces → Stratum Mining, then enter the values below.
  </p>
  <table class="cfg-table">
    <tr>
      <td>Pool URL</td>
      <td>
        <div class="cfg-val">[your-stratum-address]:4444</div>
        <div class="hint">⬆ Copy from StartOS → CKPool BCH → Service Interfaces → Stratum Mining</div>
      </td>
    </tr>
    <tr>
      <td>Username</td>
      <td>
        <div class="cfg-val" id="usernameVal" onclick="copyVal(this)">{bch}.miner1</div>
        <div class="hint">Click to copy</div>
      </td>
    </tr>
    <tr>
      <td>Password</td>
      <td><div class="cfg-val" onclick="copyVal(this)">x</div><div class="hint">Any value works</div></td>
    </tr>
  </table>
</div>

<div class="step">
  <div class="step-num">Step 3 — Start mining</div>
  <p style="color:#aaa;font-size:13px">
    Your miner appears in the Active Workers table within a few minutes.
    Any block found pays <strong style="color:#00ff88">100% of the reward</strong> directly to your BCH address. No pool fees.
  </p>
</div>

<div class="step">
  <div class="step-num">Supported hardware</div>
  <p style="color:#aaa;font-size:13px">Any SHA-256 ASIC: Bitmain Antminer S-series, MicroBT Whatsminer M-series, NerdAxe, and compatible devices.</p>
</div>

<a class="nav-link" href="/" style="display:inline-block;margin-top:8px">← Return to Dashboard</a>

<script>
const BCH = "{bch}";
function updateConfig() {{
  const w = document.getElementById('workerName').value.trim() || 'miner1';
  document.getElementById('usernameVal').textContent = BCH + '.' + w;
}}
function copyVal(el) {{
  navigator.clipboard.writeText(el.textContent).then(() => {{
    const c = el.style.color; el.style.color='#fff';
    setTimeout(()=>el.style.color=c, 500);
  }});
}}
</script>
</body></html>'''

# ── HTTP handler ───────────────────────────────────────────────────────────────

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_GET(self):
        body = connect_html() if self.path.startswith('/connect') else dashboard_html(read_stats())
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.end_headers()
        self.wfile.write(body.encode())

if __name__ == '__main__':
    print(f'[stats] Starting web UI on port {PORT}')
    with ThreadedHTTPServer(('0.0.0.0', PORT), Handler) as srv:
        srv.serve_forever()
