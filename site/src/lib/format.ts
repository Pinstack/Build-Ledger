// Small, dependency-free formatting helpers. Numbers are formatted at build time.

export const int = (n: number): string => new Intl.NumberFormat('en-US').format(Math.round(n || 0));

export function pct(share: number, dp = 1): string {
  return `${(100 * (share || 0)).toFixed(dp)}%`;
}

// Net LOC, demoted and compact (never the headline): 363500 -> "363.5k"
export function compact(n: number): string {
  const a = Math.abs(n || 0);
  if (a >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (a >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return String(Math.round(n || 0));
}

export function shortDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return String(iso).slice(0, 10);
}

export function shortId(id: string): string {
  return String(id).slice(0, 8);
}
