import { sdk } from '../sdk'

export const { init, uninit } = sdk.setupInit({
  init: async ({ effects }) => {},
  uninit: async ({ effects }) => {},
})
