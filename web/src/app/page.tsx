import type { Metadata } from "next";
import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { RunsList } from "@/components/RunsList";

export const metadata: Metadata = {
  title: 'Galatus · Runs',
};

export default function Page() {
  return (
    <>
      <AppHeader />
      <main className="mx-auto flex max-w-[1360px] flex-col gap-6 px-4 pb-12 pt-7 sm:px-8">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-[26px] font-bold tracking-tight">Runs</h1>
            <p className="mt-1.5 text-sm text-muted">Every PRD that entered the pipeline, from parsing to merged pull request.</p>
          </div>
          <span className="rounded-full bg-[#1a2038] px-2.5 py-1.5 text-xs text-subtle">Sample data · last 7 days</span>
        </div>
        <section aria-label="Key metrics" className="grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-4">
          <div className="flex flex-col gap-2 rounded-xl border border-line bg-surface px-5 py-4.5">
            <span className="text-[13px] font-medium text-muted">Runs this week</span>
            <span className="text-[28px] font-bold tracking-tight">6</span>
            <span className="text-xs text-subtle">PRDs submitted to the pipeline</span>
          </div>
          <div className="flex flex-col gap-2 rounded-xl border border-line bg-surface px-5 py-4.5">
            <span className="text-[13px] font-medium text-muted">PRs opened</span>
            <span className="text-[28px] font-bold tracking-tight">3</span>
            <span className="text-xs text-subtle">2 merged, 1 awaiting review</span>
          </div>
          <div className="flex flex-col gap-2 rounded-xl border border-line bg-surface px-5 py-4.5">
            <span className="text-[13px] font-medium text-muted">Median PRD → PR</span>
            <span className="text-[28px] font-bold tracking-tight">38 min</span>
            <span className="text-xs text-subtle">From parse to PR opened</span>
          </div>
          <div className="flex flex-col gap-2 rounded-xl border border-line bg-surface px-5 py-4.5">
            <span className="text-[13px] font-medium text-muted">Test pass rate</span>
            <span className="text-[28px] font-bold tracking-tight">75%</span>
            <span className="text-xs text-subtle">Runs that passed tests first try</span>
          </div>
        </section>
        <section aria-label="Pipeline" className="rounded-xl border border-line bg-surface p-5">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-base font-semibold">Pipeline</h2>
            <span className="text-xs text-subtle">Runs currently at each stage</span>
          </div>
          <ol className="grid grid-cols-[repeat(auto-fit,minmax(130px,1fr))] gap-2.5">
            <li className="flex flex-col gap-2.5 rounded-[10px] border border-line bg-panel px-3.5 py-3">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-medium text-muted">PRD parsed</span>
                <span className="font-mono text-[11px] text-subtle">01</span>
              </div>
              <span className="text-[22px] font-bold">0</span>
              <div className="h-1 overflow-hidden rounded bg-[#1e2540]" aria-hidden="true">
                <div className="h-full rounded bg-accent" style={{ width: "0%" }}></div>
              </div>
            </li>
            <li className="flex flex-col gap-2.5 rounded-[10px] border border-line bg-panel px-3.5 py-3">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-medium text-muted">Repo indexed</span>
                <span className="font-mono text-[11px] text-subtle">02</span>
              </div>
              <span className="text-[22px] font-bold">0</span>
              <div className="h-1 overflow-hidden rounded bg-[#1e2540]" aria-hidden="true">
                <div className="h-full rounded bg-accent" style={{ width: "0%" }}></div>
              </div>
            </li>
            <li className="flex flex-col gap-2.5 rounded-[10px] border border-line bg-panel px-3.5 py-3">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-medium text-muted">Edit plan</span>
                <span className="font-mono text-[11px] text-subtle">03</span>
              </div>
              <span className="text-[22px] font-bold">1</span>
              <div className="h-1 overflow-hidden rounded bg-[#1e2540]" aria-hidden="true">
                <div className="h-full rounded bg-accent" style={{ width: "17%" }}></div>
              </div>
            </li>
            <li className="flex flex-col gap-2.5 rounded-[10px] border border-line bg-panel px-3.5 py-3">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-medium text-muted">Code gen</span>
                <span className="font-mono text-[11px] text-subtle">04</span>
              </div>
              <span className="text-[22px] font-bold">1</span>
              <div className="h-1 overflow-hidden rounded bg-[#1e2540]" aria-hidden="true">
                <div className="h-full rounded bg-accent" style={{ width: "17%" }}></div>
              </div>
            </li>
            <li className="flex flex-col gap-2.5 rounded-[10px] border border-line bg-panel px-3.5 py-3">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-medium text-muted">Tests</span>
                <span className="font-mono text-[11px] text-subtle">05</span>
              </div>
              <span className="text-[22px] font-bold">1</span>
              <div className="h-1 overflow-hidden rounded bg-[#1e2540]" aria-hidden="true">
                <div className="h-full rounded bg-accent" style={{ width: "17%" }}></div>
              </div>
            </li>
            <li className="flex flex-col gap-2.5 rounded-[10px] border border-line bg-panel px-3.5 py-3">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-medium text-muted">PR opened</span>
                <span className="font-mono text-[11px] text-subtle">06</span>
              </div>
              <span className="text-[22px] font-bold">1</span>
              <div className="h-1 overflow-hidden rounded bg-[#1e2540]" aria-hidden="true">
                <div className="h-full rounded bg-accent" style={{ width: "17%" }}></div>
              </div>
            </li>
            <li className="flex flex-col gap-2.5 rounded-[10px] border border-line bg-panel px-3.5 py-3">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-medium text-muted">Merged</span>
                <span className="font-mono text-[11px] text-subtle">07</span>
              </div>
              <span className="text-[22px] font-bold">2</span>
              <div className="h-1 overflow-hidden rounded bg-[#1e2540]" aria-hidden="true">
                <div className="h-full rounded bg-accent" style={{ width: "33%" }}></div>
              </div>
            </li>
          </ol>
        </section>
        <div id="runs" className="flex flex-wrap items-start gap-6">
          <RunsList />
          <aside aria-label="Run detail" className="flex min-w-0 flex-[1_1_340px] flex-col gap-5 rounded-xl border border-line bg-surface p-5">
            <div className="flex flex-col gap-1.5">
              <span className="font-mono text-xs text-subtle">
run-142 · acme/web-store
</span>
              <h2 className="text-lg font-bold tracking-tight">Referral rewards at checkout</h2>
              <div>
                <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#3a2a12] text-[#f5c26b]">Needs review</span>
              </div>
            </div>
            <div>
              <h3 className="mb-3 text-[13px] font-semibold text-muted">Stages</h3>
              <ol>
                <li className="flex items-start gap-3">
                  <div className="flex w-3.5 flex-col items-center self-stretch">
                    <span className="mt-[3px] box-border h-3 w-3 rounded-full bg-accent"></span>
                    <span className="min-h-[18px] w-0.5 flex-1 bg-accent"></span>
                  </div>
                  <div className="flex flex-1 justify-between gap-2 pb-3">
                    <span className="text-sm font-medium text-ink">PRD parsed</span>
                    <span className="text-xs text-subtle">Done</span>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="flex w-3.5 flex-col items-center self-stretch">
                    <span className="mt-[3px] box-border h-3 w-3 rounded-full bg-accent"></span>
                    <span className="min-h-[18px] w-0.5 flex-1 bg-accent"></span>
                  </div>
                  <div className="flex flex-1 justify-between gap-2 pb-3">
                    <span className="text-sm font-medium text-ink">Repo indexed</span>
                    <span className="text-xs text-subtle">Done</span>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="flex w-3.5 flex-col items-center self-stretch">
                    <span className="mt-[3px] box-border h-3 w-3 rounded-full bg-accent"></span>
                    <span className="min-h-[18px] w-0.5 flex-1 bg-accent"></span>
                  </div>
                  <div className="flex flex-1 justify-between gap-2 pb-3">
                    <span className="text-sm font-medium text-ink">Edit plan</span>
                    <span className="text-xs text-subtle">Done</span>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="flex w-3.5 flex-col items-center self-stretch">
                    <span className="mt-[3px] box-border h-3 w-3 rounded-full bg-accent"></span>
                    <span className="min-h-[18px] w-0.5 flex-1 bg-accent"></span>
                  </div>
                  <div className="flex flex-1 justify-between gap-2 pb-3">
                    <span className="text-sm font-medium text-ink">Code gen</span>
                    <span className="text-xs text-subtle">Done</span>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="flex w-3.5 flex-col items-center self-stretch">
                    <span className="mt-[3px] box-border h-3 w-3 rounded-full bg-accent"></span>
                    <span className="min-h-[18px] w-0.5 flex-1 bg-accent"></span>
                  </div>
                  <div className="flex flex-1 justify-between gap-2 pb-3">
                    <span className="text-sm font-medium text-ink">Tests</span>
                    <span className="text-xs text-subtle">Done</span>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="flex w-3.5 flex-col items-center self-stretch">
                    <span className="mt-[3px] box-border h-3 w-3 rounded-full border-[3px] border-accent bg-surface"></span>
                    <span className="min-h-[18px] w-0.5 flex-1 bg-line"></span>
                  </div>
                  <div className="flex flex-1 justify-between gap-2 pb-3">
                    <span className="text-sm font-medium text-ink">PR opened</span>
                    <span className="text-xs text-subtle">Awaiting review</span>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="flex w-3.5 flex-col items-center self-stretch">
                    <span className="mt-[3px] box-border h-3 w-3 rounded-full border-2 border-[#3a4466] bg-surface"></span>
                  </div>
                  <div className="flex flex-1 justify-between gap-2 pb-3">
                    <span className="text-sm text-subtle">Merged</span>
                    <span className="text-xs text-subtle"></span>
                  </div>
                </li>
              </ol>
            </div>
            <div>
              <h3 className="mb-2.5 text-[13px] font-semibold text-muted">Edit plan</h3>
              <ul className="flex flex-col gap-2">
                <li className="flex flex-col gap-1 rounded-lg border border-line bg-panel px-3 py-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="min-w-0 font-mono text-xs text-ink [overflow-wrap:anywhere]">src/checkout/ReferralBox.tsx</span>
                    <span className="shrink-0 rounded-md px-2 py-0.5 text-[11px] font-semibold bg-[#12352a] text-[#6ee7b7]">create</span>
                  </div>
                  <span className="text-xs text-muted">Input for a referral code on the payment step, with inline validation</span>
                </li>
                <li className="flex flex-col gap-1 rounded-lg border border-line bg-panel px-3 py-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="min-w-0 font-mono text-xs text-ink [overflow-wrap:anywhere]">src/api/referrals.ts</span>
                    <span className="shrink-0 rounded-md px-2 py-0.5 text-[11px] font-semibold bg-[#12352a] text-[#6ee7b7]">create</span>
                  </div>
                  <span className="text-xs text-muted">Validate the code and return the reward for this cart</span>
                </li>
                <li className="flex flex-col gap-1 rounded-lg border border-line bg-panel px-3 py-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="min-w-0 font-mono text-xs text-ink [overflow-wrap:anywhere]">src/checkout/summary.ts</span>
                    <span className="shrink-0 rounded-md px-2 py-0.5 text-[11px] font-semibold bg-[#1a2038] text-ink-2">modify</span>
                  </div>
                  <span className="text-xs text-muted">Subtract the reward from the order total</span>
                </li>
                <li className="flex flex-col gap-1 rounded-lg border border-line bg-panel px-3 py-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="min-w-0 font-mono text-xs text-ink [overflow-wrap:anywhere]">src/checkout/PaymentStep.tsx</span>
                    <span className="shrink-0 rounded-md px-2 py-0.5 text-[11px] font-semibold bg-[#1a2038] text-ink-2">modify</span>
                  </div>
                  <span className="text-xs text-muted">Mount ReferralBox above the pay button</span>
                </li>
                <li className="flex flex-col gap-1 rounded-lg border border-line bg-panel px-3 py-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="min-w-0 font-mono text-xs text-ink [overflow-wrap:anywhere]">src/api/referrals.test.ts</span>
                    <span className="shrink-0 rounded-md px-2 py-0.5 text-[11px] font-semibold bg-[#12352a] text-[#6ee7b7]">create</span>
                  </div>
                  <span className="text-xs text-muted">Unit tests for valid, expired and self-referral codes</span>
                </li>
              </ul>
            </div>
            <div className="flex flex-wrap gap-2.5">
              <Link className="flex h-11 items-center rounded-lg bg-accent px-4 text-sm font-semibold text-white hover:bg-accent-hover" href="/run-detail">Open full run</Link>
              <a href="https://github.com/acme/web-store/pull/482" target="_blank" rel="noreferrer" className="flex h-11 items-center rounded-lg border border-line-2 px-4 text-sm font-semibold text-ink hover:border-subtle">
PR #482
</a>
            </div>
          </aside>
        </div>
      </main>
    </>
  );
}
