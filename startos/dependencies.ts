import { sdk } from './sdk'

export const setDependencies = sdk.setupDependencies(async ({ effects }) => {
  return {
    'bitcoin-cash': {
      kind: 'running',
      versionRange: '>=29.0.1:0',
      healthChecks: ['bitcoind'],
    },
  }
})
