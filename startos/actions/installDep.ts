import { sdk } from '../sdk'
import * as http from 'node:http'

// ── RPC helper (same creds as entrypoint.sh) ──────────────────────────────────
export function bchRpcCall(host: string, method: string): Promise<any> {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ jsonrpc: '1.0', id: 'dep-check', method, params: [] })
    const req = http.request(
      { hostname: host, port: 9002, path: '/', method: 'POST',
        auth: 'bchuser:bchpass123',
        headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) } },
      (res) => { let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve(JSON.parse(d)) } catch { reject(new Error('bad json')) } }) },
    )
    req.on('error', reject)
    req.setTimeout(4000, () => req.destroy(new Error('timeout')))
    req.write(body); req.end()
  })
}

// ── State 1: Not Installed ────────────────────────────────────────────────────
export const depNotInstalled = sdk.Action.withoutInput(
  'dep-not-installed',
  async ({ effects }) => ({
    name: 'Not Installed',
    description: 'Bitcoin Cash Node is not installed. Install it first, then CKPool BCH will become available.',
    warning: null,
    allowedStatuses: 'any' as const,
    group: null,
    visibility: { disabled: 'Install the Bitcoin Cash Node package to proceed' },
  }),
  async ({ effects }) => ({
    version: '1' as const, title: 'Action Required',
    message: 'Install the Bitcoin Cash Node package first.',
    result: null,
  }),
)

// ── State 2: Installed, Not Synced ────────────────────────────────────────────
export const depNotSynced = sdk.Action.withoutInput(
  'dep-not-synced',
  async ({ effects }) => ({
    name: 'Installed, Not Synced',
    description: 'Bitcoin Cash Node is installed but the blockchain is still syncing. CKPool BCH will become available once the sync is complete.',
    warning: null,
    allowedStatuses: 'any' as const,
    group: null,
    visibility: { disabled: 'Wait for Bitcoin Cash Node to finish syncing' },
  }),
  async ({ effects }) => ({
    version: '1' as const, title: 'Sync In Progress',
    message: 'Bitcoin Cash Node is still syncing. Please wait.',
    result: null,
  }),
)
