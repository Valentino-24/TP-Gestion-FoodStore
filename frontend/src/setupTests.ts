/**
 * jest-dom matchers for Vitest.
 *
 * We use the CJS entry point + createRequire to bypass ESM
 * resolution bugs in @testing-library/jest-dom v6.6.3 on Windows.
 */
import { expect } from 'vitest'
import { createRequire } from 'node:module'

const require = createRequire(import.meta.url)
const matchers = require('@testing-library/jest-dom/matchers')
expect.extend(matchers)
