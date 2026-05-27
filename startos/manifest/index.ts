import { setupManifest } from '@start9labs/start-sdk'

export const manifest = setupManifest({
  id: 'ckpool-bch',
  title: 'CKPool BCH',
  license: 'GPL-3.0',
  packageRepo: 'https://github.com/AwfulWaffleMining/-ckpool-bch-startos',
  upstreamRepo: 'https://bitbucket.org/ckolivas/ckpool',
  supportSite: 'https://github.com/AwfulWaffleMining/-ckpool-bch-startos/issues',
  marketingUrl: 'https://www.awfulwafflemining.com',
  donationUrl: 'https://www.awfulwafflemining.com/donate',
  description: {
    short: 'CKPool solo mining stratum server for Bitcoin Cash (BCH)',
    long: 'CKPool BCH is a high-performance solo mining stratum server that connects directly to your local Bitcoin Cash Node. Point your SHA-256 miners at port 4444 and every block found pays the full reward straight to your configured BCH address — no pool fees, no third parties.',
  },
  volumes: ['main'],
  images: {
    ckpool: {
      source: { dockerBuild: {} },
      arch: ['x86_64'],
    },
  },
  alerts: {
    install: 'Make sure Bitcoin Cash Node is installed and fully synced before starting CKPool BCH.',
    update: null,
    uninstall: null,
    restore: null,
    start: null,
    stop: 'Your miners will lose connection when CKPool stops.',
  },
  dependencies: {
    'bitcoin-cash': {
      description: 'Must enable ZMQ in Bitcoin Cash to use it with CKPool BCH',
      optional: false,
      s9pk: null,
    },
  },
})
