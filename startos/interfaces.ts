import { sdk } from './sdk'

export const setInterfaces = sdk.setupInterfaces(async ({ effects }) => {
  const host = sdk.MultiHost.of(effects, 'main')

  const stratumOrigin = await host.bindPort(4444, {
    protocol: null,
    addSsl: null,
    preferredExternalPort: 4444,
    secure: { ssl: false },
  })

  const stratum = sdk.createInterface(effects, {
    name: 'Stratum Mining',
    id: 'stratum',
    description: 'Point your SHA-256 miners here',
    type: 'api',
    masked: false,
    schemeOverride: null,
    username: null,
    path: '',
    query: {},
  })

  const stratumReceipt = await stratumOrigin.export([stratum])

  return [stratumReceipt]
})
