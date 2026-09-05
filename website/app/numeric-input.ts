/** Keep illustrative calculator inputs finite and non-negative. */
export function nonNegativeInput(value: string | number): number {
  const number = Number(value);
  return Number.isFinite(number) ? Math.min(Number.MAX_SAFE_INTEGER, Math.max(0, number)) : 0;
}
