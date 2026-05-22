#!/bin/bash
set -e

# ── StartOS wires dependency connection details via environment ────────────────
# bitcoin-cash dependency provides these automatically:
BCH_HOST="${BITCOIN_CASH_HOST:-127.0.0.1}"
BCH_RPC_PORT="${BITCOIN_CASH_RPC_PORT:-9002}"
BCH_RPC_USER="${BITCOIN_CASH_RPC_USER:-testuser}"
BCH_RPC_PASS="${BITCOIN_CASH_RPC_PASS:-testpass123}"
BCH_ZMQ_PORT="${BITCOIN_CASH_ZMQ_PORT:-7002}"

# ── User-configurable via Start9 config UI ────────────────────────────────────
BCH_ADDRESS="${BCH_PAYOUT_ADDRESS:?BCH_PAYOUT_ADDRESS must be set}"
STRATUM_PORT="${STRATUM_PORT:-4444}"
POOL_SIG="${POOL_SIG:-/ckpool-bch-startos/}"
MIN_DIFF="${MIN_DIFF:-1}"
START_DIFF="${START_DIFF:-8}"

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_DIR="/data/ckpool"
LOG_DIR="${DATA_DIR}/logs"
CONF_FILE="${DATA_DIR}/ckpool.conf"

mkdir -p "${DATA_DIR}" "${LOG_DIR}"

# ── Verify BCH node is reachable before starting ──────────────────────────────
echo "[ckpool-bch] Checking BCH node at ${BCH_HOST}:${BCH_RPC_PORT}..."
for i in $(seq 1 12); do
    if curl -sf -u "${BCH_RPC_USER}:${BCH_RPC_PASS}" \
        --data '{"jsonrpc":"1.0","method":"getblockchaininfo","params":[]}' \
        "http://${BCH_HOST}:${BCH_RPC_PORT}/" \
        | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if not d.get('result',{}).get('initialblockdownload',True) else 1)" 2>/dev/null; then
        echo "[ckpool-bch] BCH node is synced and ready."
        break
    fi
    echo "[ckpool-bch] BCH node not ready (attempt ${i}/12) — waiting 10s..."
    sleep 10
done

# ── Write ckpool.conf ──────────────────────────────────────────────────────────
cat > "${CONF_FILE}" <<EOF
{
"btcd" : [
  {
    "url"    : "${BCH_HOST}:${BCH_RPC_PORT}",
    "auth"   : "${BCH_RPC_USER}",
    "pass"   : "${BCH_RPC_PASS}",
    "notify" : true
  }
],
"btcaddress"      : "${BCH_ADDRESS}",
"btcsig"          : "${POOL_SIG}",
"blockpoll"       : 100,
"nonce1length"    : 4,
"nonce2length"    : 8,
"update_interval" : 30,
"version_mask"    : "1fffe000",
"serverurl"       : [
  "0.0.0.0:${STRATUM_PORT}"
],
"mindiff"         : ${MIN_DIFF},
"startdiff"       : ${START_DIFF},
"zmqblock"        : "tcp://${BCH_HOST}:${BCH_ZMQ_PORT}",
"logdir"          : "${LOG_DIR}"
}
EOF

echo "[ckpool-bch] Starting stratum on port ${STRATUM_PORT}"
echo "[ckpool-bch] Payout address: ${BCH_ADDRESS}"

exec /usr/local/bin/ckpool --config "${CONF_FILE}"
