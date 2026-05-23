import { sdk } from './sdk'
import { storeJson } from './file-models/store.json'

export const main = sdk.setupMain(async ({ effects }) => {
  console.info('Starting CKPool BCH...')

  const stored = await storeJson.read().once()
  const payoutAddress = stored?.BCH_PAYOUT_ADDRESS ?? ''
  const poolSig       = stored?.POOL_SIG       ?? '/AwfulWaffle/'
  const minDiff       = stored?.MIN_DIFF        ?? 1
  const startDiff     = stored?.START_DIFF      ?? 8

  // bitcoin-cash Start9 package container — try getContainerIp first, fallback to known IP
  let bchHost    = '10.0.3.120'   // bitcoin-cash package container (stable)
  const bchRpcPort = '9002'
  const bchZmqPort = '7002'

  try {
    const depIp = await sdk.getContainerIp(effects, { packageId: 'bitcoin-cash' }).const()
    if (depIp && depIp !== '10.0.3.179') {
      bchHost = depIp
      console.info(`Using bitcoin-cash container IP: ${bchHost}`)
    }
  } catch {
    console.info(`Using known bitcoin-cash IP: ${bchHost}`)
  }

  return sdk.Daemons.of(effects).addDaemon('ckpool', {
    subcontainer: await sdk.SubContainer.of(
      effects,
      { imageId: 'ckpool' },
      sdk.Mounts.of().mountVolume({
        volumeId: 'main',
        subpath: null,
        mountpoint: '/data',
        readonly: false,
      }),
      'ckpool',
    ),
    exec: {
      command: ['/usr/local/bin/docker_entrypoint.sh'],
      env: {
        BCH_PAYOUT_ADDRESS:      payoutAddress,
        POOL_SIG:                poolSig,
        MIN_DIFF:                String(minDiff),
        START_DIFF:              String(startDiff),
        BITCOIN_CASH_HOST:       bchHost,
        BITCOIN_CASH_RPC_PORT:   bchRpcPort,
        BITCOIN_CASH_ZMQ_PORT:   bchZmqPort,
        BITCOIN_CASH_RPC_USER:   'bchuser',
        BITCOIN_CASH_RPC_PASS:   'bchpass123',
      },
    },
    ready: {
      display: 'Stratum Server',
      fn: () =>
        sdk.healthCheck.checkPortListening(effects, 4444, {
          successMessage: 'BCH stratum ready on port 4444',
          errorMessage: 'Stratum port 4444 not yet open',
        }),
    },
    requires: [],
  })
})
