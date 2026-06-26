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
  visibility?: 'public' | 'private';  // true GitHub visibility, independent of whether named
  allowlisted: boolean;
  status: 'active' | 'archived';
  label?: string | null;
  category?: string | null;
  metrics: { commits: number; active_days: number; files: number; loc_added: number; loc_removed: number; loc_net: number; };
  signals: { has_tests: boolean; has_ci: boolean; has_migrations: boolean; };
  coauthorship: Coauthorship;
  ai_artefacts: { workflow_infrastructure: number; delivery_artefacts: number; quality_controls: number; };
  agent_sessions?: { sessions: number; output_tokens: number; total_tokens: number };
}
export interface Practice {
  available: boolean;
  cadence: { sessions: number; claude_sessions?: number; codex_sessions?: number };
  tokens?: { output: number; total: number };
  model_mix: { model: string; sessions: number; share: number }[];
  cache_hit_ratio: number | null;
  cost: { available: boolean; total: number | null };
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
  agentic_practice: Practice & { [k: string]: unknown };
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

// ---------------------------------------------------------------------------
// Derived rollups. One place computes every cross-repo figure the page shows,
// as a pure function of repositories[] (AD-14) — so a headline always equals the
// sum of the rows a skeptic can drill into. Nothing here is hand-entered.
// ---------------------------------------------------------------------------
const artOf = (r: Repo): number =>
  r.ai_artefacts.workflow_infrastructure + r.ai_artefacts.delivery_artefacts + r.ai_artefacts.quality_controls;
const isPublic = (r: Repo): boolean => r.display_tier === 'public';
const sum = <T>(arr: T[], f: (x: T) => number): number => arr.reduce((a, x) => a + f(x), 0);

export interface RepoGroup {
  count: number; commits: number; coauthored: number;
  withTests: number; withCI: number; withMig: number; files: number; artefacts: number;
}
function group(repos: Repo[], pred: (r: Repo) => boolean): RepoGroup {
  const g = repos.filter(pred);
  return {
    count: g.length,
    commits: sum(g, (r) => r.metrics.commits),
    coauthored: sum(g, (r) => r.coauthorship.ai_coauthored_commits),
    withTests: g.filter((r) => r.signals.has_tests).length,
    withCI: g.filter((r) => r.signals.has_ci).length,
    withMig: g.filter((r) => r.signals.has_migrations).length,
    files: sum(g, (r) => r.metrics.files),
    artefacts: sum(g, (r) => artOf(r)),
  };
}

export interface Stats {
  co: Coauthorship & { agent_authored_commits: number };
  humanNoTrailer: number;       // human commits that carry no AI trailer
  repoCount: number; publicCount: number; privateCount: number;
  withTests: number; withCI: number; withMig: number; filesTotal: number;
  arts: { wi: number; da: number; qc: number }; artTotal: number; reposWithArtefacts: number;
  active: Repo[];               // commits > 0, sorted desc
  dormant: Repo[];              // commits === 0
  maxCommits: number;           // largest single-repo commit count (bar scaling)
  maxSessions: number;          // largest single-repo agent-session count (bar scaling)
  priv: RepoGroup; pub: RepoGroup;
  top: Repo | null;             // single most active repository
  firstCommit: string | null; latestCommit: string | null;
  practice: Practice;           // agentic_practice block (sessions, tokens, model mix, cache)
  reposWithSessions: number;    // repos carrying agent-session evidence
}

export function deriveStats(l: Ledger): Stats {
  const repos = l.repositories;
  const co = l.aggregates.coauthorship;
  const arts = repos.reduce(
    (a, r) => {
      a.wi += r.ai_artefacts.workflow_infrastructure;
      a.da += r.ai_artefacts.delivery_artefacts;
      a.qc += r.ai_artefacts.quality_controls;
      return a;
    },
    { wi: 0, da: 0, qc: 0 },
  );
  const active = repos.filter((r) => r.metrics.commits > 0).sort((a, b) => b.metrics.commits - a.metrics.commits);
  return {
    co,
    humanNoTrailer: Math.max(0, co.human_commits - co.ai_coauthored_commits),
    repoCount: repos.length,
    publicCount: l.aggregates.repo_counts.public,
    privateCount: l.aggregates.repo_counts.private,
    withTests: repos.filter((r) => r.signals.has_tests).length,
    withCI: repos.filter((r) => r.signals.has_ci).length,
    withMig: repos.filter((r) => r.signals.has_migrations).length,
    filesTotal: sum(repos, (r) => r.metrics.files),
    arts,
    artTotal: arts.wi + arts.da + arts.qc,
    reposWithArtefacts: repos.filter((r) => artOf(r) > 0).length,
    active,
    dormant: repos.filter((r) => r.metrics.commits === 0),
    maxCommits: active[0]?.metrics.commits ?? 0,
    maxSessions: Math.max(0, ...repos.map((r) => r.agent_sessions?.sessions ?? 0)),
    priv: group(repos, (r) => !isPublic(r)),
    pub: group(repos, isPublic),
    top: active[0] ?? null,
    firstCommit: l.ledger_metadata.date_range.first_commit,
    latestCommit: l.ledger_metadata.date_range.latest_commit,
    practice: l.agentic_practice,
    reposWithSessions: repos.filter((r) => (r.agent_sessions?.sessions ?? 0) > 0).length,
  };
}
