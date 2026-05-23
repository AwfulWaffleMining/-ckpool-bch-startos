import { sdk } from './sdk'

export const setInterfaces = sdk.setupInterfaces(async ({ effects }) => {
  const stratumMulti = sdk.MultiHost.of(effects, 'stratum')
  const stratumOrigin = await stratumMulti.bindPort(4444, {
    protocol: null,
    addSsl: null,
    preferredExternalPort: 4444,
    secure: { ssl: false },
  })
  const stratum = sdk.createInterface(effects, {
    name: 'Stratum Mining',
    id: 'stratum',
    description: 'Point your SHA-256 miners here. Use worker name as your BCH address.',
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
