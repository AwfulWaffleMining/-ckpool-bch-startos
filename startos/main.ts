import { sdk } from './sdk'
import { storeJson } from './file-models/store.json'

export const main = sdk.setupMain(async ({ effects }) => {
  console.info('Starting CKPool (DGB mode via port 9335)...')

  const stored = await storeJson.read().once()
  const payoutAddress = stored?.BCH_PAYOUT_ADDRESS ?? ''
  const poolSig       = stored?.POOL_SIG       ?? '/AwfulWaffle-DGB/'
  const minDiff       = stored?.MIN_DIFF        ?? 1
  const startDiff     = stored?.START_DIFF      ?? 8

  // DGB node running in same container at port 9335
  const dgbHost    = '10.0.3.179'
  const dgbRpcPort = '9335'
  const dgbZmqPort = '7007'

  console.info(`Connecting to DGB node at ${dgbHost}:${dgbRpcPort}`)

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
        BITCOIN_CASH_HOST:       dgbHost,
        BITCOIN_CASH_RPC_PORT:   dgbRpcPort,
        BITCOIN_CASH_ZMQ_PORT:   dgbZmqPort,
        BITCOIN_CASH_RPC_USER:   'dgbuser',
        BITCOIN_CASH_RPC_PASS:   'dgbpass123',
      },
    },
    ready: {
      display: 'Stratum Server',
      fn: () =>
        sdk.healthCheck.checkPortListening(effects, 4444, {
          successMessage: 'DGB stratum ready on port 4444',
          errorMessage: 'Stratum port 4444 not yet open',
        }),
    },
    requires: [],
  })
})
