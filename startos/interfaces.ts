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

  // ── Stats Web UI ───────────────────────────────────────────────────────────
  const uiMulti = sdk.MultiHost.of(effects, 'ui')
  const uiOrigin = await uiMulti.bindPort(8080, {
    protocol: null,
    addSsl: null,
    preferredExternalPort: 8080,
    secure: { ssl: false },
  })
  const ui = sdk.createInterface(effects, {
    name: 'Web UI',
    id: 'ui',
    description: 'Mining stats dashboard — connected workers and blocks found.',
    type: 'ui',
    masked: false,
    schemeOverride: { ssl: null, noSsl: 'http' },
    username: null,
    path: '/',
    query: {},
  })
  const uiReceipt = await uiOrigin.export([ui])

  return [stratumReceipt, uiReceipt]
})
