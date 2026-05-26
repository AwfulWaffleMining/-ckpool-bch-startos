import { sdk } from '../sdk'
import { setDependencies } from '../dependencies'
import { setInterfaces } from '../interfaces'
import { versionGraph } from '../versions'
import { actions } from '../actions'
import { restoreInit } from '../backups'
import { installDep } from '../actions/installDep'

const createDepTask = sdk.setupOnInit(
  async (effects, kind) => {
    if (kind === 'install') {
      await sdk.action.createOwnTask(effects, installDep, 'critical', {
        replayId: 'install-dep',
        reason: 'Must enable ZMQ in Bitcoin Cash to use it with CKPool BCH',
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
  createDepTask,
)

export const uninit = sdk.setupUninit(versionGraph)
