import assert from 'node:assert/strict';
import test from 'node:test';
import { nonNegativeInput } from '../app/numeric-input.ts';
test('calculator inputs reject negative and non-finite values while preserving valid fractions', () => {
  for (const value of [-1, '-25', Infinity, -Infinity, NaN, '1e999', 'invalid', '']) assert.equal(nonNegativeInput(value), 0);
  assert.equal(nonNegativeInput('12.5'), 12.5);
  assert.equal(nonNegativeInput(48), 48);
  assert.equal(nonNegativeInput('1e300'), Number.MAX_SAFE_INTEGER);
});
