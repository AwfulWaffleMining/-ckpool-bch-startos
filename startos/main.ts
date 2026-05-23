import { sdk } from './sdk'
import { storeJson } from './file-models/store.json'

export const main = sdk.setupMain(async ({ effects }) => {
  console.info('Starting CKPool BCH...')

  // Read stored config — set by the Configure action
  const stored = await storeJson.read().once()

  const payoutAddress = stored?.BCH_PAYOUT_ADDRESS ?? ''
  const poolSig       = stored?.POOL_SIG       ?? '/AwfulWaffle/'
  const minDiff       = stored?.MIN_DIFF        ?? 1
  const startDiff     = stored?.START_DIFF      ?? 8

  if (!payoutAddress) {
    console.error('BCH_PAYOUT_ADDRESS not set — run the Configure action first')
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
        BCH_PAYOUT_ADDRESS: payoutAddress,
        POOL_SIG:           poolSig,
        MIN_DIFF:           String(minDiff),
        START_DIFF:         String(startDiff),
      },
    },
    ready: {
      display: 'Stratum Server',
      fn: () =>
        sdk.healthCheck.checkPortListening(effects, 4444, {
          successMessage: 'Stratum server is ready on port 4444',
          errorMessage: 'Stratum port 4444 not yet open',
        }),
    },
    requires: [],
  })
})
