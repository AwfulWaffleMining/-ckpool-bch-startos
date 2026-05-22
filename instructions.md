# CKPool BCH — Solo Mining Stratum Server

## Requirements
- **Bitcoin Cash Node** must be installed and fully synced before starting CKPool BCH.

## Setup

1. Install and sync **Bitcoin Cash Node** from the Start9 marketplace.
2. Install **CKPool BCH**.
3. Set your BCH payout address in the service config (default is pre-filled from the BCH node package).
4. Start the service.
5. Point your SHA-256 miners at:
   - **Host:** `awfulwafflenode.local` (or your server's LAN IP)
   - **Port:** `4444`
   - **User:** your BCH address (or any string — solo pool ignores worker names)
   - **Password:** `x`

## What It Does

CKPool acts as a local solo stratum server. Your miners connect to it, receive work templates from your BCH node, and submit shares. When a block is found, the full reward goes directly to your configured BCH address — no pool fees, no third parties.

## Logs

Logs and per-worker stats are written to `/data/ckpool/logs/` inside the package volume. The mining dashboard at `awfulwafflemining.com` reads from this directory to display live hashrate, accepted shares, and worker names.

## Ports

| Port | Protocol | Description |
|------|----------|-------------|
| 4444 | TCP      | Stratum mining endpoint |
