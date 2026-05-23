import { sdk } from './sdk'

export const setDependencies = sdk.setupDependencies(async ({ effects }) => ({
  'bitcoin-cash': {
    kind: 'running' as const,
    versionRange: '>=29.0.0:0',
    healthChecks: [],
  },
}))
