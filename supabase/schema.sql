-- ====================================================================
-- CODE SENTINEL AI: Autonomous AI Software Quality Engineer
-- Enterprise PostgreSQL Schema with Row Level Security (RLS)
-- ====================================================================

create extension if not exists "pgcrypto";

-- 1. Scans & Repositories Table
create table if not exists public.scans (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  source_type text not null check (source_type in ('snippet', 'upload', 'github_pr', 'repository', 'agent_run')),
  repo_full_name text,
  pr_number integer,
  filename text default 'main.py',
  language text not null default 'python',
  status text not null default 'completed' check (status in ('queued', 'running', 'completed', 'failed', 'awaiting_approval')),
  high_count integer not null default 0,
  medium_count integer not null default 0,
  low_count integer not null default 0,
  total_findings integer not null default 0,
  quality_score jsonb, -- { overall, code_quality, security, performance, test_coverage, maintainability }
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 2. Granular Findings Table
create table if not exists public.findings (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid not null references public.scans(id) on delete cascade,
  user_id text not null,
  tool text not null,
  rule_id text not null,
  severity text not null check (severity in ('high', 'medium', 'low', 'info')),
  category text not null,
  file_path text not null,
  line_number integer not null,
  message text not null,
  root_cause text,
  exploitability text,
  confidence float not null default 0.90,
  ai_explanation text,
  suggested_fix text,
  regression_test text,
  status text not null default 'open' check (status in ('open', 'fixed', 'dismissed', 'applied')),
  created_at timestamptz not null default now()
);

-- 3. Project Memory & Architectural Knowledge Base
create table if not exists public.project_memory (
  id uuid primary key default gen_random_uuid(),
  repo_full_name text not null,
  user_id text not null,
  memory_type text not null check (memory_type in ('convention', 'decision', 'approved_patch', 'framework_pattern')),
  title text not null,
  description text not null,
  evidence text,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 4. Agent Threads & Interactive Runs
create table if not exists public.agent_threads (
  thread_id text primary key,
  user_id text not null,
  scan_id uuid references public.scans(id) on delete set null,
  repo_full_name text,
  status text not null default 'active' check (status in ('active', 'awaiting_approval', 'completed', 'failed', 'rejected')),
  proposal jsonb,
  patch_attempts integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 5. Audit Trail Logs
create table if not exists public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  action text not null,
  entity_type text not null,
  entity_id text not null,
  details jsonb,
  created_at timestamptz not null default now()
);

-- 6. Indexes for Performance
create index if not exists idx_scans_user_id on public.scans(user_id);
create index if not exists idx_scans_repo on public.scans(repo_full_name);
create index if not exists idx_findings_scan_id on public.findings(scan_id);
create index if not exists idx_findings_severity on public.findings(severity);
create index if not exists idx_project_memory_repo on public.project_memory(repo_full_name);

-- 7. Row Level Security Policies
alter table public.scans enable row level security;
alter table public.findings enable row level security;
alter table public.project_memory enable row level security;
alter table public.agent_threads enable row level security;
alter table public.audit_logs enable row level security;

-- Policies allowing access for owner or local development
create policy "scans_policy" on public.scans for all
  using (auth.uid()::text = user_id or user_id = 'local-dev-user')
  with check (auth.uid()::text = user_id or user_id = 'local-dev-user');

create policy "findings_policy" on public.findings for all
  using (auth.uid()::text = user_id or user_id = 'local-dev-user')
  with check (auth.uid()::text = user_id or user_id = 'local-dev-user');

create policy "memory_policy" on public.project_memory for all
  using (auth.uid()::text = user_id or user_id = 'local-dev-user')
  with check (auth.uid()::text = user_id or user_id = 'local-dev-user');

create policy "threads_policy" on public.agent_threads for all
  using (auth.uid()::text = user_id or user_id = 'local-dev-user')
  with check (auth.uid()::text = user_id or user_id = 'local-dev-user');

create policy "audit_policy" on public.audit_logs for all
  using (auth.uid()::text = user_id or user_id = 'local-dev-user')
  with check (auth.uid()::text = user_id or user_id = 'local-dev-user');
