import { FileHelper, z } from '@start9labs/start-sdk'
import { sdk } from '../sdk'

export const shape = z.object({
  BCH_PAYOUT_ADDRESS: z.string().catch(''),
  POOL_SIG:           z.string().catch('/AwfulWaffle/'),
  MIN_DIFF:           z.number().catch(1),
  START_DIFF:         z.number().catch(8),
}).strip()

export const storeJson = FileHelper.json(
  {
    base: sdk.volumes.main,
    subpath: '/ckpool-config.json',
  },
  shape,
)
