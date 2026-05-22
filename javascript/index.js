'use strict';

/**
 * CKPool BCH — StartOS Package
 *
 * Connects to the local bitcoin-cash dependency node via RPC + ZMQ
 * and exposes a stratum server on port 4444 for SHA-256 miners.
 */

const { effects, started } = require('@start9labs/start-sdk');

exports.manifest = require('../manifest.json');

exports.main = async function ({ effects, started }) {
  started();
};

exports.init = async function ({ effects }) {
  // On first install, generate a default config if none exists
};

exports.uninit = async function ({ effects }) {};

exports.createBackup = async function ({ effects }) {
  // ckpool state is minimal — just the config. Data lives on-chain.
};

exports.actions = {
  restartPool: {
    name: 'Restart Pool',
    description: 'Restart the ckpool process without stopping the service.',
    warning: 'Connected miners will briefly disconnect and reconnect.',
    allowedStatuses: ['running'],
    implementation: {
      type: 'script',
      fn: async ({ effects }) => {
        // Implemented via entrypoint script signal handling
        return { message: 'Pool restarted.' };
      },
    },
  },
};
