export { createBackup, restoreInit } from './backups'
export { main } from './main'
export { init, uninit } from './init'
export { actions } from './actions'
import { buildManifest } from '@start9labs/start-sdk'
import { manifest as sdkManifest } from './manifest/index'
export const manifest = buildManifest([[sdkManifest.version, sdkManifest]], sdkManifest)
