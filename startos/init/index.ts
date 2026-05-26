import { sdk } from '../sdk'
import { setDependencies } from '../dependencies'
import { setInterfaces } from '../interfaces'
import { versionGraph } from '../versions'
import { actions } from '../actions'
import { restoreInit } from '../backups'
import { depNotInstalled, depNotSynced, bchRpcCall } from '../actions/installDep'

// ── Check BCH state and manage task accordingly ───────────────────────────────
const manageDepTask = sdk.setupOnInit(async (effects) => {
  const TASK_NOT_INSTALLED = 'dep-not-installed'
  const TASK_NOT_SYNCED    = 'dep-not-synced'

  try {
    // Try to get bitcoin-cash container IP
    const bchHost = await (sdk.getContainerIp(effects, { packageId: 'bitcoin-cash' }) as any).const().catch(() => null)

    if (!bchHost) {
      // State 1: Not installed
      await sdk.action.clearTask(effects, TASK_NOT_SYNCED).catch(() => {})
      await sdk.action.createOwnTask(effects, depNotInstalled, 'critical', { replayId: TASK_NOT_INSTALLED, reason: 'Must enable ZMQ in Bitcoin Cash to use it with CKPool BCH' })
      return
    }

    // State 2 or 3: Installed — check sync via RPC
    const result = await bchRpcCall(bchHost, 'getblockchaininfo').catch(() => null)
    const progress: number = result?.result?.verificationprogress ?? 0

    if (progress < 0.9999) {
      // State 2: Installed, not synced
      await sdk.action.clearTask(effects, TASK_NOT_INSTALLED).catch(() => {})
      await sdk.action.createOwnTask(effects, depNotSynced, 'critical', { replayId: TASK_NOT_SYNCED, reason: 'Bitcoin Cash Node is still syncing — CKPool BCH will start when sync is complete' })
    } else {
      // State 3: Installed and synced — clear all dep tasks
      await sdk.action.clearTask(effects, TASK_NOT_INSTALLED).catch(() => {})
      await sdk.action.clearTask(effects, TASK_NOT_SYNCED).catch(() => {})
    }
  } catch {
    // Fallback: assume not installed
    await sdk.action.createOwnTask(effects, depNotInstalled, 'critical', { replayId: TASK_NOT_INSTALLED, reason: 'Must enable ZMQ in Bitcoin Cash to use it with CKPool BCH' }).catch(() => {})
  }
})

export const init = sdk.setupInit(
  restoreInit,
  versionGraph,
  setInterfaces,
  setDependencies,
  actions,
  manageDepTask,
)

export const uninit = sdk.setupUninit(versionGraph)
