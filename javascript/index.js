'use strict';

/**
 * CKPool BCH — StartOS Package JavaScript
 * SDK: @start9labs/start-sdk v1.5.2
 *
 * Wires ckpool-bch into the StartOS UI:
 *  - Reads bitcoin-cash dependency connection details
 *  - Stores stratum display address for the UI
 *  - Exposes pool stats as Properties
 *  - Health check: verify stratum port is listening
 */

const path = require('path');
const fs   = require('fs');

// ── Manifest (must match manifest.json exactly) ──────────────────────────────
const manifest = require('../manifest.json');
exports.manifest = manifest;

// ── Constants ────────────────────────────────────────────────────────────────
const STRATUM_PORT    = 4444;
const LOG_DIR         = '/data/ckpool/logs';
const POOL_STATUS     = path.join(LOG_DIR, 'pool', 'pool.status');
const USER_DIR        = path.join(LOG_DIR, 'users');

// ── Helper: read ckpool pool.status ──────────────────────────────────────────
function readPoolStatus() {
  try {
    const lines = fs.readFileSync(POOL_STATUS, 'utf8').trim().split('\n').filter(Boolean);
    const result = { hashrate1m: null, workers: 0, accepted: 0, rejected: 0, bestshare: 0 };
    for (const line of lines) {
      try {
        const j = JSON.parse(line);
        if (j.hashrate1m != null) { result.hashrate1m = j.hashrate1m; }
        if (j.Workers   != null) { result.workers   = j.Workers; }
        if (j.accepted  != null) { result.accepted  = j.accepted; result.rejected = j.rejected; result.bestshare = j.bestshare; }
      } catch (_) {}
    }
    return result;
  } catch (_) {
    return null;
  }
}

// ── Helper: read best-ever difficulty from user file ─────────────────────────
function readBestEver() {
  try {
    const users = fs.readdirSync(USER_DIR);
    for (const u of users) {
      const d = JSON.parse(fs.readFileSync(path.join(USER_DIR, u), 'utf8'));
      if (d.bestever) return d.bestever;
    }
  } catch (_) {}
  return 0;
}

// ── Main: called when the service starts ─────────────────────────────────────
exports.main = async function ({ effects, started }) {
  // Resolve LAN address from StartOS host system
  const lanAddress = await effects.getHostInfo({ packageId: null, interfaceId: 'stratum' })
    .then(info => `${info.localAddress}:${STRATUM_PORT}`)
    .catch(() => `<your-server-ip>:${STRATUM_PORT}`);

  // Store the stratum connection string for display in the UI
  await effects.store.set({
    path:  '/stratumDisplayAddress',
    value: lanAddress,
  }).catch(() => {});

  // Signal StartOS that the service is running
  started();
};

// ── Properties: shown in the "Properties" tab in the Start9 UI ───────────────
exports.properties = async function ({ effects }) {
  const pool      = readPoolStatus();
  const bestEver  = readBestEver();

  return {
    version: 2,
    data: {
      'Stratum Address': {
        type:        'string',
        value:       `stratum+tcp://<your-server-ip>:${STRATUM_PORT}`,
        description: 'Point your SHA-256 miners here. Replace <your-server-ip> with your server\'s LAN IP.',
        copyable:    false,
        qr:          false,
        masked:      false,
      },
      'Pool Hashrate (1m)': {
        type:        'string',
        value:       pool ? `${pool.hashrate1m} TH/s` : 'Waiting for first share...',
        description: 'Combined 1-minute rolling hashrate of all connected miners.',
        copyable:    false,
        qr:          false,
        masked:      false,
      },
      'Connected Miners': {
        type:        'string',
        value:       pool ? String(pool.workers) : '0',
        description: 'Number of miners currently connected to the stratum server.',
        copyable:    false,
        qr:          false,
        masked:      false,
      },
      'Accepted Shares': {
        type:        'string',
        value:       pool ? pool.accepted.toLocaleString() : '0',
        description: 'Total shares accepted since pool started.',
        copyable:    false,
        qr:          false,
        masked:      false,
      },
      'Best Difficulty (All Time)': {
        type:        'string',
        value:       bestEver ? bestEver.toLocaleString() : '—',
        description: 'Highest difficulty share ever submitted. BCH network difficulty is ~662 billion.',
        copyable:    false,
        qr:          false,
        masked:      false,
      },
    },
  };
};

// ── Health checks ─────────────────────────────────────────────────────────────
exports.health = {
  stratum: async function ({ effects }) {
    // Check stratum port is accepting connections
    const net = require('net');
    return new Promise((resolve) => {
      const socket = net.createConnection({ port: STRATUM_PORT, host: '127.0.0.1', timeout: 3000 });
      socket.on('connect', () => { socket.destroy(); resolve({ result: 'success', message: `Stratum listening on port ${STRATUM_PORT}` }); });
      socket.on('error',   () => resolve({ result: 'failure', message: `Stratum port ${STRATUM_PORT} not yet open` }));
      socket.on('timeout', () => { socket.destroy(); resolve({ result: 'failure', message: 'Stratum connection timeout' }); });
    });
  },
};

// ── Init / Uninit ─────────────────────────────────────────────────────────────
exports.init   = async function ({ effects }) {};
exports.uninit = async function ({ effects }) {};

// ── Backup (minimal — config only, chain data lives in bitcoin-cash package) ──
exports.createBackup = async function ({ effects }) {
  // Nothing critical to back up — ckpool config is regenerated from env vars on start
};

// ── Actions ───────────────────────────────────────────────────────────────────
exports.actions = {};
