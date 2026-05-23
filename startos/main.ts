import { sdk } from './sdk'
import { setInterfaces } from './interfaces'
import { setDependencies } from './dependencies'

export const main = sdk.setupMain(async ({ effects }) => {
  console.info('Starting CKPool BCH...')

  await setInterfaces(effects)
  await setDependencies(effects)

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
    },
    ready: {
      display: 'CKPool BCH Stratum',
      gracePeriod: 30_000,
      fn: () =>
        sdk.healthCheck.checkPortListening(effects, 4444, {
          successMessage: 'Stratum server is ready on port 4444',
          errorMessage: 'Stratum port 4444 is not yet open',
        }),
    },
    requires: [],
  })
})
