import { sdk } from '../sdk'
import { setDependencies } from '../dependencies'
import { setInterfaces } from '../interfaces'
import { versionGraph } from '../versions'
import { actions } from '../actions'
import { restoreInit } from '../backups'
import { config } from '../actions/config'

const createSetupTask = sdk.setupOnInit(
  async (effects, kind) => {
    if (kind === 'install') {
      await sdk.action.createOwnTask(effects, config, 'critical', {
        replayId: 'initial-setup',
        reason: 'Set your BCH payout address before starting CKPool BCH',
      })
    }
  },
)

export const init = sdk.setupInit(
  restoreInit,
  versionGraph,
  setInterfaces,
  setDependencies,
  actions,
  createSetupTask,
)

export const uninit = sdk.setupUninit(versionGraph)
