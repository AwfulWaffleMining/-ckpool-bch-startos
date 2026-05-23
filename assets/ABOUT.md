# CKPool BCH

CKPool BCH is a high-performance solo mining stratum server for Bitcoin Cash (BCH). It connects directly to your local Bitcoin Cash Node to source block templates, and accepts connections from SHA-256 miners on port 4444.

## Solo Mining

Every block found pays the **full block reward** directly to your configured BCH address — no pool fees, no third parties, no trust required. The odds of finding a block depend entirely on your hashrate relative to the total BCH network difficulty.

## Setup

1. Install and fully sync **Bitcoin Cash Node** first
2. Install and start **CKPool BCH**
3. Configure your BCH payout address via the **Configure** action
4. Point your SHA-256 miners at: `your-server-ip:4444`
   - **User:** your BCH address (e.g. `bitcoincash:qq...`)
   - **Password:** `x`

## Upstream

- [CKPool by Con Kolivas](https://bitbucket.org/ckolivas/ckpool)
- [CKPool BCH StartOS Source](https://github.com/AwfulWaffleMining/-ckpool-bch-startos)
