// Load build-ledger.json at build time and gate on the schema MAJOR (AD-7): a v1 page renders
// MAJOR 1 only and refuses an unsupported MAJOR rather than mis-render.
import ledgerData from '../data/build-ledger.json';

export const SUPPORTED_MAJOR = 1;

export interface Author { author: string; commits: number; }
export interface Coauthorship {
  unit: string; total_commits: number; human_commits: number;
  ai_coauthored_commits: number; ai_coauthored_share: number;
  agents: Author[]; excluded_bots: Author[];
}
export interface Repo {
  id: string;
  display_tier: 'public' | 'redacted' | 'aggregate_only';
  allowlisted: boolean;
  status: 'active' | 'archived';
  label?: string | null;
  category?: string | null;
  metrics: { commits: number; active_days: number; files: number; loc_added: number; loc_removed: number; loc_net: number; };
  signals: { has_tests: boolean; has_ci: boolean; has_migrations: boolean; };
  coauthorship: Coauthorship;
  ai_artefacts: { workflow_infrastructure: number; delivery_artefacts: number; quality_controls: number; };
}
export interface Ledger {
  schema_version: string;
  ledger_metadata: {
    generated_at: string; collector_version: string; schema_version: string;
    identities_included: string[];
    date_range: { first_commit: string | null; latest_commit: string | null };
    data_url: string; methodology_url: string;
  };
  repositories: Repo[];
  aggregates: {
    repo_counts: { public: number; private: number; archived: number; active: number };
    languages: { name: string; share: number }[];
    totals: { commits: number; user_authored_commits: number; loc_net: number };
    coauthorship: Coauthorship & { agent_authored_commits: number };
  };
  agentic_practice: { available: boolean; [k: string]: unknown };
  retrospective: { available: boolean; window_view: unknown[] };
  in_flight: { available: boolean; wip_branches: number; open_issues: number; draft_prs: number; todo_fixme: number; commit_trajectory: number[] };
  activity: { available: boolean; monthly: { month: string; commits: number; loc_net: number }[]; heatmap: { date: string; commits: number }[] };
  exclusions: { forks: number; vendored: number; generated: number; lockfiles: number; minified: number; bot_commits: number; mirrors: number };
}

export type LoadResult =
  | { ok: true; ledger: Ledger; major: number }
  | { ok: false; major: number; version: string };

export function loadLedger(): LoadResult {
  const l = ledgerData as unknown as Ledger;
  const version = l.ledger_metadata?.schema_version ?? l.schema_version ?? '0.0.0';
  const major = parseInt(String(version).split('.')[0] || '0', 10);
  if (major !== SUPPORTED_MAJOR) return { ok: false, major, version };
  return { ok: true, ledger: l, major };
}
