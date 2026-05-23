import { sdk } from './sdk'

export const main = sdk.setupMain(async ({ effects }) => {
  console.info('Starting CKPool BCH...')

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
