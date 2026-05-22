# CKPool BCH — StartOS Package

A StartOS community package that runs [CKPool](https://bitbucket.org/ckolivas/ckpool) as a solo mining stratum server for Bitcoin Cash (BCH).

## What It Does

Point your SHA-256 ASIC miners at your StartOS server on port **4444**. CKPool connects to your local `bitcoin-cash` node, builds block templates, and distributes work to your miners. When you find a block, the full reward goes straight to your BCH address — no pool fees, no intermediaries.

## Requirements

- **bitcoin-cash** StartOS package — must be installed and fully synced
- One or more SHA-256 miners (NerdAxe, Bitaxe, ASIC, etc.)

## Miner Setup

Configure each miner with:
- **Pool URL:** `stratum+tcp://<your-server-lan-ip>:4444`
- **Username:** Your BCH address (e.g. `bitcoincash:qq...`)
- **Worker name:** Append `.rigname` to distinguish miners: `bitcoincash:qq....NerdQAxe1`
- **Password:** `x`

## Building

### Prerequisites
- Docker
- [start-sdk CLI](https://github.com/Start9Labs/start-os)
- Node.js 20+
- make

### Build

```bash
git clone https://github.com/awfulwafflenode/ckpool-bch-startos
cd ckpool-bch-startos
npm install
make
```

This produces `ckpool-bch.s9pk` which can be sideloaded or submitted to the community registry.

## Contributing

PRs welcome. The upstream ckpool source is at https://bitbucket.org/ckolivas/ckpool.

## License

MIT (wrapper) / GPL-3.0 (ckpool upstream). See [LICENSE.md](LICENSE.md).
