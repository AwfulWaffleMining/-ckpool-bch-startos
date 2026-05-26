import { sdk } from '../sdk'

export const installDep = sdk.Action.withoutInput(
  'install-dep',

  async ({ effects }) => ({
    name: 'Not Installed',
    description:
      'Bitcoin Cash Node is not installed. ' +
      'Install and start the Bitcoin Cash Node package first, then return here to start CKPool BCH.',
    warning: null,
    allowedStatuses: 'any' as const,
    group: null,
    visibility: { disabled: 'Install the Bitcoin Cash Node package to proceed' },
  }),

  async ({ effects }) => {
    await sdk.action.clearTask(effects, 'install-dep')
    return {
      version: '1' as const,
      title: 'Acknowledged',
      message: 'Install the Bitcoin Cash Node package and wait for it to fully sync, then start CKPool BCH.',
      result: null,
    }
  },
)
