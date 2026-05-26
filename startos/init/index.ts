import { sdk } from '../sdk'
import { setDependencies } from '../dependencies'
import { setInterfaces } from '../interfaces'
import { versionGraph } from '../versions'
import { actions } from '../actions'
import { restoreInit } from '../backups'
import type { ActionInfo } from '@start9labs/start-sdk/base/lib/actions/setupActions'

// Stub for bitcoin-cash's 'config' action — matches its input shape
// (same pattern as Public Pool → bitcoind:autoconfig)
const bchConfigStub = {
  id: 'config' as const,
  _INPUT: undefined as unknown as { zmqEnabled: boolean },
} satisfies ActionInfo<'config', { zmqEnabled: boolean }>

// When bitcoin-cash is not installed: task shows, play button disabled (can't
// run an action on an uninstalled package). When installed with zmqEnabled=true:
// input-not-matches evaluates false → task disappears automatically.
// This is the exact same mechanism Public Pool uses for Bitcoin Knots.
const createDepTask = sdk.setupOnInit(async (effects) => {
  await sdk.action.createTask(
    effects,
    'bitcoin-cash',
    bchConfigStub,
    'critical',
    {
      reason: 'Must enable ZMQ in Bitcoin Cash to use it with CKPool BCH',
      when: { once: false, condition: 'input-not-matches' },
      input: { kind: 'partial', value: { zmqEnabled: true } },
    },
  )
})

export const init = sdk.setupInit(
  restoreInit,
  versionGraph,
  setInterfaces,
  setDependencies,
  actions,
  createDepTask,
)

export const uninit = sdk.setupUninit(versionGraph)
