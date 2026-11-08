"use client";

import { useState } from "react";

type Mode = "plan" | "full";

const MODES: {
  id: Mode;
  title: string;
  description: string;
}[] = [
  {
    id: "plan",
    title: "Edit plan only",
    description: "Index the repo and list which files change and why. No code is written.",
  },
  {
    id: "full",
    title: "Plan, code and PR",
    description: "Write the code on a new branch, run tests and open a pull request.",
  },
];

function modeClass(active: boolean) {
  return active
    ? "flex flex-col gap-1 rounded-[10px] px-4 py-3.5 text-left border-2 border-accent bg-accent-soft"
    : "flex flex-col gap-1 rounded-[10px] px-4 py-3.5 text-left m-px border border-line-2 bg-surface hover:border-subtle";
}

function switchClass(on: boolean) {
  return on
    ? "flex h-[26px] w-11 shrink-0 cursor-pointer rounded-full p-[3px] transition-colors justify-end bg-accent"
    : "flex h-[26px] w-11 shrink-0 cursor-pointer rounded-full p-[3px] transition-colors justify-start bg-[#2a3352]";
}

export function OutputModePicker() {
  const [mode, setMode] = useState<Mode>("full");
  const [runTests, setRunTests] = useState(true);
  const [requireReview, setRequireReview] = useState(true);

  return (
    <>
      <input type="hidden" name="mode" value={mode} />
      <div role="radiogroup" aria-label="Output mode" className="grid grid-cols-[repeat(auto-fit,minmax(240px,1fr))] gap-3">
        {MODES.map((m) => (
          <button
            key={m.id}
            type="button"
            role="radio"
            aria-checked={mode === m.id}
            className={modeClass(mode === m.id)}
            onClick={() => setMode(m.id)}
          >
            <span className="text-sm font-semibold text-ink">{m.title}</span>
            <span className="text-[13px] leading-snug text-muted">{m.description}</span>
          </button>
        ))}
      </div>
      <div className="divide-y divide-[#1a2038]">
        <div className="flex items-center justify-between gap-4 py-3">
          <div>
            <div className="text-sm font-semibold">Run tests before opening the PR</div>
            <div className="text-xs text-subtle">Stops the run if the test suite fails</div>
          </div>
          <input type="hidden" name="runTests" value={runTests ? "on" : "off"} />
          <button
            type="button"
            role="switch"
            aria-checked={runTests}
            aria-label="Run tests before opening the PR"
            className={switchClass(runTests)}
            onClick={() => setRunTests((v) => !v)}
          >
            <span className="block h-5 w-5 rounded-full bg-[#f4f2ff]" />
          </button>
        </div>
        <div className="flex items-center justify-between gap-4 py-3">
          <div>
            <div className="text-sm font-semibold">Require human review</div>
            <div className="text-xs text-subtle">PR is opened as a draft until someone approves the plan</div>
          </div>
          <input type="hidden" name="requireReview" value={requireReview ? "on" : "off"} />
          <button
            type="button"
            role="switch"
            aria-checked={requireReview}
            aria-label="Require human review"
            className={switchClass(requireReview)}
            onClick={() => setRequireReview((v) => !v)}
          >
            <span className="block h-5 w-5 rounded-full bg-[#f4f2ff]" />
          </button>
        </div>
      </div>
    </>
  );
}
