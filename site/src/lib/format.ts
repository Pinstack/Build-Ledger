// Small, dependency-free formatting helpers. Numbers are formatted at build time.

export const int = (n: number): string => new Intl.NumberFormat('en-US').format(Math.round(n || 0));

export function pct(share: number, dp = 1): string {
  return `${(100 * (share || 0)).toFixed(dp)}%`;
}

// Compact magnitude: 363500 -> "363.5k", 151667746 -> "151.7M", 27422520827 -> "27.4B"
export function compact(n: number): string {
  const a = Math.abs(n || 0);
  if (a >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)}B`;
  if (a >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (a >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return String(Math.round(n || 0));
}

export function shortDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return String(iso).slice(0, 10);
}

// "2026-06-24T…" -> "24 June 2026" (build-time, UTC, no locale surprises)
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
export function longDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(iso));
  if (!m) return shortDate(iso);
  const [, y, mo, d] = m;
  return `${parseInt(d, 10)} ${MONTHS[parseInt(mo, 10) - 1]} ${y}`;
}

// "2017" from an ISO date
export function year(iso: string | null | undefined): string {
  if (!iso) return '—';
  return String(iso).slice(0, 4);
}

export function shortId(id: string): string {
  return String(id).slice(0, 8);
}
