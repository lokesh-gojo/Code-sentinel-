# CODE SENTINEL AI: Autonomous AI Software Quality Engineer
## Identity & Core Mission
**Detect. Understand. Repair. Verify.**
An enterprise-grade, hybrid deterministic and agentic AI software quality platform featuring:
- Whole-repository intelligence and NetworkX dependency graph analysis.
- Autonomous multi-agent orchestration via LangGraph (Code Analyst, Bug Hunter, Security, Performance, Test, Fix, Verification, and Review Manager).
- Self-healing code loop with isolated sandbox verification (E2B / container / restricted runner) and human approval gates.
- Multi-LLM provider abstraction (Gemini 2.5 Flash for cloud, Ollama for local/offline inference, deterministic heuristic fallback).
- Persistent repository memory & architectural convention store.
- Transparent, deterministic 0–100 Code Quality Scoring engine.

## Hard Architectural & Security Constraints
- **Zero Untrusted Code on Host:** User or agent-generated code must never execute on the host OS; test validation runs strictly inside isolated microVMs (E2B) or locked-down ephemeral sandboxes with network restrictions, memory/CPU bounds, and 15s execution timeouts.
- **Subprocess Safety:** Every tool invocation (Ruff, Bandit, ESLint, Semgrep, AST parsers) must use argument lists (`shell=False`) and sanitized paths (`Path(name).name`).
- **Human Approval Gate (LangGraph `interrupt`):** The system must NEVER auto-commit, silently overwrite files, or publish GitHub PR comments without explicit, authenticated developer approval.
- **Evidence-Based Patch Validation:** Tests passing in the sandbox serve as empirical evidence, not speculative LLM claims. Confidence scores are calibrated based on test outcomes and static scanner confirmation.
- **Strict Secret & Tenant Isolation:** Production secrets stay in `.env` / `.env.local`. PostgreSQL Row Level Security (RLS) is enforced across scans, findings, and project memories.
- **Dual Cloud & Offline Capability:** Every pipeline must support local offline mode (Ollama / local AST rules / mock repository) as well as cloud deployment (Gemini / Supabase / E2B / Vercel / Render).
