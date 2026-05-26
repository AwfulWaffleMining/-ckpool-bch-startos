import { sdk } from '../sdk'
import { config } from './config'
import { depNotInstalled, depNotSynced } from './installDep'

export const actions = sdk.Actions.of().addAction(config).addAction(depNotInstalled).addAction(depNotSynced)
