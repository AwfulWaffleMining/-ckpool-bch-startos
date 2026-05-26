import { sdk } from '../sdk'
import { storeJson } from '../file-models/store.json'

const { InputSpec, Value } = sdk

export const inputSpec = InputSpec.of({
  BCH_PAYOUT_ADDRESS: Value.text({
    name: 'BCH Payout Address',
    description: 'Your Bitcoin Cash address for block rewards',
    required: true,
    placeholder: 'bitcoincash:q...',
    default: null,
    patterns: [],
    inputmode: 'text',
    masked: false,
  }),
  POOL_SIG: Value.text({
    name: 'Pool Signature',
    description: 'Tag included in coinbase transactions',
    required: false,
    default: '/AwfulWaffle/',
    placeholder: '/YourTag/',
    patterns: [],
    inputmode: 'text',
    masked: false,
  }),
  MIN_DIFF: Value.number({
    name: 'Minimum Difficulty',
    description: 'Minimum share difficulty enforced for all miners.',
    required: false,
    default: 1,
    min: 1,
    integer: false,
  }),
  START_DIFF: Value.number({
    name: 'Starting Difficulty',
    description: 'Initial difficulty assigned to newly connected miners.',
    required: false,
    default: 8,
    min: 1,
    integer: false,
  }),
})

export const config = sdk.Action.withInput(
  'config',
  async ({ effects }) => ({
    name: 'Configure',
    description: 'Set CKPool BCH stratum settings',
    warning: 'Changing these settings requires restarting CKPool BCH.',
    allowedStatuses: 'any',
    group: null,
    visibility: 'enabled',
  }),
  inputSpec,
  async ({ effects }) => {
    const stored = await storeJson.read().once()
    return {
      BCH_PAYOUT_ADDRESS: stored?.BCH_PAYOUT_ADDRESS ?? '',
      POOL_SIG: stored?.POOL_SIG ?? '/AwfulWaffle/',
      MIN_DIFF: stored?.MIN_DIFF ?? 1,
      START_DIFF: stored?.START_DIFF ?? 8,
    }
  },
  async ({ effects, input }) => {
    await storeJson.merge(effects, {
      BCH_PAYOUT_ADDRESS: input.BCH_PAYOUT_ADDRESS,
      POOL_SIG: input.POOL_SIG ?? '/AwfulWaffle/',
      MIN_DIFF: input.MIN_DIFF ?? 1,
      START_DIFF: input.START_DIFF ?? 8,
    })
    // Clear the first-run setup task if it exists
    await sdk.action.clearTask(effects, 'initial-setup')
  },
)
