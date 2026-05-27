#!/usr/bin/env python3
"""CKPool BCH stats web server — dashboard + Performance History + How to Connect."""
import http.server, json, os, html, time, threading
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

LOG_DIR      = '/data/ckpool/logs'
USERS_DIR    = '/data/ckpool/logs/users'
POOL_STATUS  = '/data/ckpool/logs/pool/pool.status'
HISTORY_FILE = '/data/ckpool/stats_history.json'
PORT         = 8080
BCH_ADDRESS  = os.environ.get('BCH_PAYOUT_ADDRESS', '')
MAX_HISTORY  = 10080   # 7 days @ 1-min intervals

# ── History storage ────────────────────────────────────────────────────────────

_history = []
_history_lock = threading.Lock()

def load_history():
    global _history
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                _history = json.load(f)
    except Exception:
        _history = []

def save_history():
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(_history[-MAX_HISTORY:], f)
    except Exception:
        pass

def record_history():
    """Background thread — records a data point every 60 seconds."""
    while True:
        time.sleep(60)
        try:
            s = read_stats()
            pt = {
                'ts':  int(time.time()),
                'hs':  s['hashrate'],
                'rej': float(s['rej_pct'].replace('%', '')),
            }
            with _history_lock:
                _history.append(pt)
                if len(_history) > MAX_HISTORY:
                    _history.pop(0)
            save_history()
        except Exception:
            pass

def get_history(hours=1):
    cutoff = int(time.time()) - hours * 3600
    with _history_lock:
        return [p for p in _history if p['ts'] >= cutoff]

# ── Read ckpool stats ──────────────────────────────────────────────────────────

def short_name(wname):
    """bitcoincash:qq3...ne.nerqaxe1 → nerqaxe1"""
    parts = wname.rsplit('.', 1)
    return parts[-1] if len(parts) > 1 else wname

def read_stats():
    workers = []
    blocks = 0
    tot_acc = tot_rej = 0
    pool_hashrate = '—'
    pool_rej_pct = '0.00%'

    if os.path.isdir(USERS_DIR):
        for uf in sorted(os.listdir(USERS_DIR)):
            path = os.path.join(USERS_DIR, uf)
            try:
                with open(path, 'r') as f:
                    d = json.load(f)
                mtime = os.path.getmtime(path)
                for w in d.get('worker', []):
                    wname = w.get('workername', uf)
                    status = 'active' if time.time() - mtime < 600 else 'offline'
                    workers.append({
                        'name':      html.escape(short_name(wname)),
                        'fullname':  html.escape(wname),
                        'hashrate':  w.get('hashrate1m', '—'),
                        'shares':    w.get('shares', 0),
                        'best':      int(w.get('bestshare', 0)),
                        'status':    status,
                    })
            except Exception:
                pass

    if os.path.exists(POOL_STATUS):
        try:
            with open(POOL_STATUS, 'r') as f:
                for line in f:
                    try:
                        d = json.loads(line.strip())
                        if 'accepted' in d:
                            tot_acc, tot_rej = d['accepted'], d['rejected']
                        if 'hashrate1m' in d and 'Users' not in d:
                            pool_hashrate = d['hashrate1m']
                    except Exception:
                        pass
            pool_rej_pct = f'{(tot_rej/max(1,tot_acc+tot_rej)*100):.2f}%'
        except Exception:
            pass

    pool_log = os.path.join(LOG_DIR, 'ckpool.log')
    if os.path.exists(pool_log):
        try:
            with open(pool_log, 'r') as f:
                blocks = f.read().count('Solved block')
        except Exception:
            pass

    active  = sum(1 for w in workers if w['status'] == 'active')
    offline = sum(1 for w in workers if w['status'] == 'offline')
    return {'workers': workers, 'blocks': blocks,
            'active': active, 'offline': offline,
            'tot_acc': tot_acc, 'tot_rej': tot_rej,
            'hashrate': pool_hashrate, 'rej_pct': pool_rej_pct}

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
.chart-wrap{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;padding:20px;margin-bottom:20px}
.chart-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.chart-title{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px}
.tab-group{display:flex;gap:4px}
.tab{font-size:11px;padding:4px 10px;border-radius:4px;border:1px solid #2a2a2a;background:#0d0d0d;color:#666;cursor:pointer}
.tab.active{background:#00ff8822;color:#00ff88;border-color:#00ff8844}
.table-wrap{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;padding:20px;margin-bottom:20px}
.table-title{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px}
table{width:100%;border-collapse:collapse;font-size:12px}
th{text-align:left;color:#555;font-size:10px;text-transform:uppercase;letter-spacing:1px;padding:8px 0;border-bottom:1px solid #2a2a2a}
td{padding:10px 0;border-bottom:1px solid #1e1e1e;color:#aaa}
td:first-child{color:#00ff88}
.badge{font-size:9px;padding:2px 6px;border-radius:3px;font-weight:bold}
.ba{background:#00ff8822;color:#00ff88;border:1px solid #00ff8844}
.bo{background:#ff555522;color:#f87171;border:1px solid #ff555544}
.footer{color:#444;font-size:10px;text-align:center;margin-top:16px}
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
      <td title="{w["fullname"]}">{w["name"]}</td>
      <td>{w["shares"]:,}</td><td>{w["hashrate"]}</td><td>{w["best"]:,}</td>
      <td><span class="badge {"ba" if w["status"]=="active" else "bo"}">{w["status"].upper()}</span></td>
    </tr>''' for w in s['workers']
    ) or '<tr><td colspan="5" style="color:#555;text-align:center;padding:20px">No miners connected yet</td></tr>'

    last_update = time.strftime('%I:%M %p', time.localtime())

    return f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<title>CKPool BCH</title><meta http-equiv="refresh" content="30">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
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
      <div><div class="sub-val">{s["tot_rej"]}</div><div class="lbl">Rejected</div></div>
      <div><div class="sub-val g">{s["blocks"]}</div><div class="lbl">Blocks</div></div>
    </div>
  </div>
  <div class="card">
    <div class="card-title"><span class="dot dot-g"></span>Hashrate</div>
    <div class="big">{s["hashrate"]}</div><div class="lbl" style="margin-bottom:12px">current speed</div>
    <div class="sub-row">
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

<div class="chart-wrap">
  <div class="chart-header">
    <div style="display:flex;align-items:center;gap:8px">
      <span style="font-size:14px">📈</span>
      <span class="chart-title">Performance History</span>
    </div>
    <div class="tab-group">
      <button class="tab active" onclick="loadChart(1,this)">1H</button>
      <button class="tab" onclick="loadChart(24,this)">24H</button>
      <button class="tab" onclick="loadChart(168,this)">7D</button>
    </div>
  </div>
  <canvas id="perfChart" height="80"></canvas>
  <div style="display:flex;justify-content:space-between;margin-top:8px">
    <div style="display:flex;gap:16px;font-size:11px;color:#666">
      <span>● <span style="color:#3b82f6">Hashrate</span></span>
      <span>● <span style="color:#e55">Reject Rate</span></span>
    </div>
    <div style="font-size:10px;color:#555">LAST UPDATED: {last_update}</div>
  </div>
</div>

<div class="table-wrap">
  <div class="table-title">Active Workers</div>
  <table><tr><th>Worker</th><th>Shares</th><th>Hashrate</th><th>Best Share</th><th>Status</th></tr>
  {rows}</table>
</div>
<div class="footer">Auto-refreshes every 30s &nbsp;·&nbsp; Stratum port 4444 &nbsp;·&nbsp; Hover worker name for full address</div>

<script>
let chart = null;
function loadChart(hours, btn) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  fetch('/history?hours=' + hours).then(r=>r.json()).then(data => {{
    const labels = data.map(p => {{
      const d = new Date(p.ts * 1000);
      return d.toLocaleTimeString([], {{hour:'2-digit', minute:'2-digit'}});
    }});
    const hs = data.map(p => p.hs_num || 0);
    const rej = data.map(p => p.rej);
    const ctx = document.getElementById('perfChart').getContext('2d');
    if (chart) chart.destroy();
    chart = new Chart(ctx, {{
      type: 'line',
      data: {{
        labels,
        datasets: [
          {{label:'Hashrate', data:hs, borderColor:'#3b82f6', backgroundColor:'#3b82f611',
            yAxisID:'y', tension:0.3, pointRadius:0, borderWidth:2}},
          {{label:'Reject %', data:rej, borderColor:'#e55', backgroundColor:'#e5511111',
            yAxisID:'y2', tension:0.3, pointRadius:0, borderWidth:1.5}},
        ]
      }},
      options: {{
        responsive:true, interaction:{{mode:'index',intersect:false}},
        plugins:{{legend:{{display:false}}}},
        scales:{{
          x:{{ticks:{{color:'#555',maxTicksLimit:12}}, grid:{{color:'#1a1a1a'}}}},
          y:{{ticks:{{color:'#3b82f6'}}, grid:{{color:'#1e1e1e'}}, position:'left'}},
          y2:{{ticks:{{color:'#e55',callback:v=>v+'%'}}, grid:{{display:false}}, position:'right'}},
        }}
      }}
    }});
  }}).catch(()=>{{
    const ctx = document.getElementById('perfChart').getContext('2d');
    ctx.fillStyle='#555'; ctx.font='12px monospace';
    ctx.fillText('Collecting data — check back in a few minutes', 20, 60);
  }});
}}
loadChart(1, document.querySelector('.tab.active'));
</script>
</body></html>'''

# ── How to Connect page ────────────────────────────────────────────────────────

def connect_html(host='[your-stratum-address]'):
    bch = html.escape(BCH_ADDRESS) if BCH_ADDRESS else 'bitcoincash:your_bch_address'
    stratum_url = f'stratum+tcp://{html.escape(host)}:4444'
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
  <p style="color:#aaa;font-size:13px;margin-bottom:6px">Click any value to copy it.</p>
  <table class="cfg-table">
    <tr><td>Pool URL</td><td>
      <div class="cfg-val" id="stratumVal" onclick="copyVal(this)">{stratum_url}</div>
      <div class="hint">Click to copy</div>
    </td></tr>
    <tr><td>Username</td><td>
      <div class="cfg-val" id="usernameVal" onclick="copyVal(this)">{bch}.miner1</div>
      <div class="hint">Click to copy</div>
    </td></tr>
    <tr><td>Password</td><td>
      <div class="cfg-val" onclick="copyVal(this)">x</div>
      <div class="hint">Any value works</div>
    </td></tr>
  </table>
</div>
<div class="step">
  <div class="step-num">Step 3 — Start mining</div>
  <p style="color:#aaa;font-size:13px">
    Your miner appears in Active Workers within a few minutes.
    Any block found pays <strong style="color:#00ff88">100% of the reward</strong> to your BCH address. No pool fees.
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

def parse_hashrate_num(hs_str):
    """Convert '4.5T' → float TH/s for chart."""
    try:
        s = hs_str.strip()
        if s.endswith('T'): return float(s[:-1])
        if s.endswith('G'): return float(s[:-1]) / 1000
        if s.endswith('M'): return float(s[:-1]) / 1e6
        return float(s)
    except Exception:
        return 0.0

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_GET(self):
        if self.path.startswith('/history'):
            hours = 1
            try:
                hours = int(self.path.split('hours=')[1])
            except Exception:
                pass
            pts = get_history(hours)
            # Add numeric hashrate for chart
            for p in pts:
                p['hs_num'] = parse_hashrate_num(p.get('hs', '0'))
            body = json.dumps(pts).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(body)
            return
        host = (self.headers.get('Host') or '').split(':')[0] or '[your-stratum-address]'
        body = connect_html(host) if self.path.startswith('/connect') else dashboard_html(read_stats())
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.end_headers()
        self.wfile.write(body.encode())

if __name__ == '__main__':
    load_history()
    t = threading.Thread(target=record_history, daemon=True)
    t.start()
    print(f'[stats] Starting web UI on port {PORT}')
    with ThreadedHTTPServer(('0.0.0.0', PORT), Handler) as srv:
        srv.serve_forever()
