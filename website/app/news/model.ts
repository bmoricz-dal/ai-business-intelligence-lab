export type Story = { headline: string; facts: string; interpretation: string; evidence_boundary: string; watch_next: string; sources: { title: string; url: string }[] };
export type Edition = { date: string; title: string; introduction: string; stories: Story[]; evidence_run_ids: string[] };
export function validDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const parsed = new Date(value + "T00:00:00Z");
  return Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
}
