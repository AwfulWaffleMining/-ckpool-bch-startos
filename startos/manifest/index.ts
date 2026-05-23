import { setupManifest } from '@start9labs/start-sdk'

export const manifest = setupManifest({
  id: 'ckpool-bch',
  title: 'CKPool BCH',
  license: 'GPL-3.0',
  packageRepo: 'https://github.com/AwfulWaffleMining/-ckpool-bch-startos',
  upstreamRepo: 'https://bitbucket.org/ckolivas/ckpool',
  supportSite: 'https://github.com/AwfulWaffleMining/-ckpool-bch-startos/issues',
  marketingUrl: 'https://bitbucket.org/ckolivas/ckpool',
  donationUrl: null,
  description: {
    short: 'CKPool solo mining stratum server for Bitcoin Cash (BCH)',
    long: 'CKPool BCH is a high-performance solo mining stratum server that connects directly to your local Bitcoin Cash Node. Point your SHA-256 miners at port 4444 and every block found pays the full reward straight to your configured BCH address — no pool fees, no third parties, no trust required.\n\nCKPool is written in C by Con Kolivas (kernel/cgminer developer) and is the same software behind solo.ckpool.org. This StartOS package pairs it with your local bitcoin-cash node for a fully sovereign solo mining setup.',
  },
  volumes: ['main'],
  images: {
    ckpool: {
      source: { dockerBuild: {} },
      arch: ['x86_64'],
    },
  },
  hardwareRequirements: { device: [], ram: null, arch: ['x86_64'] },
  alerts: {
    install:
      'Make sure Bitcoin Cash Node is installed and fully synced before starting CKPool BCH. Initial sync can take several days.',
    update: null,
    uninstall: null,
    restore: null,
    start: null,
    stop: 'Your miners will lose connection and fall back to any configured fallback pool when CKPool stops.',
  },
  dependencies: {
    'bitcoin-cash': {
      version: '>=29.0.1:0',
      requirement: { type: 'required' },
      description:
        'CKPool BCH requires a running, fully-synced Bitcoin Cash Node for block templates and ZMQ block notifications.',
    },
  },
  releaseNotes:
    'Initial StartOS community release. Stratum on port 4444. Requires bitcoin-cash package.',
})
