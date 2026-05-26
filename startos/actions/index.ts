import { sdk } from '../sdk'
import { config } from './config'
import { installDep } from './installDep'

export const actions = sdk.Actions.of().addAction(config).addAction(installDep)
