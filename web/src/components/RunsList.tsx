"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

type Status = "needs-review" | "in-progress" | "merged" | "failed";
type Filter = "all" | Status;

type RunRow = {
  id: string;
  title: string;
  repo: string;
  stage: string;
  status: Status;
  statusLabel: string;
  statusClass: string;
  files: number;
  pr?: { href: string; label: string };
  updated: string;
  selected?: boolean;
};

const FILTERS: { id: Filter; label: string; count: number }[] = [
  { id: "all", label: "All", count: 6 },
  { id: "in-progress", label: "In progress", count: 2 },
  { id: "needs-review", label: "Needs review", count: 1 },
  { id: "merged", label: "Merged", count: 2 },
  { id: "failed", label: "Failed", count: 1 },
];

const RUNS: RunRow[] = [
  {
    id: "run-142",
    title: "Referral rewards at checkout",
    repo: "acme/web-store",
    stage: "PR opened",
    status: "needs-review",
    statusLabel: "Needs review",
    statusClass: "bg-[#3a2a12] text-[#f5c26b]",
    files: 5,
    pr: { href: "https://github.com/acme/web-store/pull/482", label: "#482" },
    updated: "12 min ago",
    selected: true,
  },
  {
    id: "run-141",
    title: "Bulk CSV import for leads",
    repo: "acme/crm-api",
    stage: "Code gen",
    status: "in-progress",
    statusLabel: "In progress",
    statusClass: "bg-[#16264a] text-[#8db4ff]",
    files: 3,
    updated: "25 min ago",
  },
  {
    id: "run-140",
    title: "Google Workspace SSO",
    repo: "acme/auth-service",
    stage: "Merged",
    status: "merged",
    statusLabel: "Merged",
    statusClass: "bg-[#12352a] text-[#6ee7b7]",
    files: 2,
    pr: { href: "https://github.com/acme/auth-service/pull/477", label: "#477" },
    updated: "2 h ago",
  },
  {
    id: "run-139",
    title: "Rate limit headers on gateway",
    repo: "acme/gateway",
    stage: "Tests",
    status: "failed",
    statusLabel: "Failed",
    statusClass: "bg-[#3a1518] text-[#f5a3a8]",
    files: 4,
    updated: "3 h ago",
  },
  {
    id: "run-138",
    title: "Invoice PDF attachments",
    repo: "acme/billing",
    stage: "Merged",
    status: "merged",
    statusLabel: "Merged",
    statusClass: "bg-[#12352a] text-[#6ee7b7]",
    files: 6,
    pr: { href: "https://github.com/acme/billing/pull/455", label: "#455" },
    updated: "1 d ago",
  },
  {
    id: "run-137",
    title: "Webhook retry queue",
    repo: "acme/gateway",
    stage: "Edit plan",
    status: "in-progress",
    statusLabel: "In progress",
    statusClass: "bg-[#16264a] text-[#8db4ff]",
    files: 2,
    pr: { href: "https://github.com/acme/gateway/pull/471", label: "#471" },
    updated: "1 d ago",
  },
];

function chipClass(active: boolean) {
  return active
    ? "flex min-h-9 items-center gap-1.5 rounded-lg border px-3 text-[13px] font-semibold border-ink bg-ink text-canvas"
    : "flex min-h-9 items-center gap-1.5 rounded-lg border px-3 text-[13px] font-semibold border-line-2 bg-surface text-ink-2 hover:border-subtle";
}

export function RunsList() {
  const [filter, setFilter] = useState<Filter>("all");
  const [selectedId, setSelectedId] = useState("run-142");

  const rows = useMemo(
    () => (filter === "all" ? RUNS : RUNS.filter((r) => r.status === filter)),
    [filter],
  );

  return (
    <section aria-label="Runs list" className="min-w-0 flex-[999_1_560px] rounded-xl border border-line bg-surface">
      <div role="group" aria-label="Filter by status" className="flex flex-wrap gap-2 border-b border-line px-5 py-4">
        {FILTERS.map((f) => (
          <button
            key={f.id}
            type="button"
            aria-pressed={filter === f.id}
            className={chipClass(filter === f.id)}
            onClick={() => setFilter(f.id)}
          >
            {f.label}
            <span className="font-mono text-xs opacity-80">{f.count}</span>
          </button>
        ))}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] border-collapse text-sm">
          <thead>
            <tr className="text-left text-xs text-muted">
              <th className="px-5 py-3 font-semibold">PRD</th>
              <th className="px-3 py-3 font-semibold">Repository</th>
              <th className="px-3 py-3 font-semibold">Stage</th>
              <th className="px-3 py-3 font-semibold">Status</th>
              <th className="px-3 py-3 font-semibold">Files</th>
              <th className="px-3 py-3 font-semibold">PR</th>
              <th className="py-3 pl-3 pr-5 font-semibold">Updated</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((run) => {
              const selected = run.id === selectedId;
              return (
                <tr
                  key={run.id}
                  className={
                    selected
                      ? "border-t border-[#1a2038] bg-accent-soft shadow-[inset_3px_0_0_var(--color-accent)]"
                      : "border-t border-[#1a2038] bg-surface hover:bg-panel"
                  }
                >
                  <td className="px-5 py-3.5">
                    <button
                      type="button"
                      aria-current={selected ? "true" : undefined}
                      className="flex min-h-11 cursor-pointer flex-col justify-center gap-0.5 text-left"
                      onClick={() => setSelectedId(run.id)}
                    >
                      <span className="font-semibold text-ink">{run.title}</span>
                      <span className="font-mono text-xs text-subtle">{run.id}</span>
                    </button>
                  </td>
                  <td className="px-3 py-3.5 font-mono text-[13px] text-ink-2">{run.repo}</td>
                  <td className="px-3 py-3.5 text-ink-2">{run.stage}</td>
                  <td className="px-3 py-3.5">
                    <span
                      className={`inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold ${run.statusClass}`}
                    >
                      {run.statusLabel}
                    </span>
                  </td>
                  <td className="px-3 py-3.5 font-mono text-ink-2">{run.files}</td>
                  <td className="px-3 py-3.5 font-mono">
                    {run.pr ? (
                      <a
                        href={run.pr.href}
                        target="_blank"
                        rel="noreferrer"
                        className="text-link hover:text-link-hover"
                      >
                        {run.pr.label}
                      </a>
                    ) : (
                      <span className="text-subtle">—</span>
                    )}
                  </td>
                  <td className="whitespace-nowrap py-3.5 pl-3 pr-5 text-muted">{run.updated}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="flex justify-end border-t border-line px-5 py-3">
        <Link href="/run-detail" className="text-[13px] font-semibold text-link hover:text-link-hover">
          Open selected run
        </Link>
      </div>
    </section>
  );
}
