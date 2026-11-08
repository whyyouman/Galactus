import type { Metadata } from "next";
import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";

export const metadata: Metadata = {
  title: 'Run detail · Galatus',
};

export default function Page() {
  return (
    <>
      <AppHeader />
      <main className="mx-auto flex max-w-[1360px] flex-col gap-5 px-4 pb-12 pt-6 sm:px-8">
        <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-[13px] text-subtle">
          <Link className="text-link hover:text-link-hover" href="/">Runs</Link>
          <span aria-hidden="true">/</span>
          <span className="font-mono">run-142</span>
        </nav>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex flex-col gap-2.5">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-[26px] font-bold tracking-tight">Referral rewards at checkout</h1>
              <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#3a2a12] text-[#f5c26b]">Needs review</span>
            </div>
            <div className="flex flex-wrap gap-4.5 text-[13px] text-muted">
              <span>
Repo                 <strong className="font-mono font-medium text-ink">acme/web-store</strong>
              </span>
              <span>
Branch                 <strong className="font-mono font-medium text-ink">prd/referral-rewards</strong>
              </span>
              <span>
PR                 <a href="https://github.com/acme/web-store/pull/482" target="_blank" rel="noreferrer" className="font-mono text-link">
#482
</a>
              </span>
              <span>
Started 30 min ago
</span>
            </div>
          </div>
          <div className="flex flex-wrap gap-2.5">
            <button type="button" className="flex h-11 items-center gap-2 rounded-lg border border-line-2 bg-surface px-4 text-sm font-semibold text-ink hover:border-subtle">Re-run from plan</button>
            <a href="https://github.com/acme/web-store/pull/482" target="_blank" rel="noreferrer" className="flex h-11 items-center gap-2 rounded-lg bg-accent px-4 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60">Open pull request</a>
          </div>
        </div>
        <section aria-label="Stages" className="overflow-x-auto rounded-xl border border-line bg-surface px-5 py-4.5">
          <ol className="flex min-w-[820px]">
            <li className="flex flex-1 flex-col gap-2">
              <div className="flex items-center">
                <span className="box-border h-3.5 w-3.5 shrink-0 rounded-full bg-accent"></span>
                <span className="mx-1.5 h-0.5 flex-1 bg-accent"></span>
              </div>
              <span className="text-[13px] font-semibold text-ink">PRD parsed</span>
              <span className="text-xs text-subtle">0:04</span>
            </li>
            <li className="flex flex-1 flex-col gap-2">
              <div className="flex items-center">
                <span className="box-border h-3.5 w-3.5 shrink-0 rounded-full bg-accent"></span>
                <span className="mx-1.5 h-0.5 flex-1 bg-accent"></span>
              </div>
              <span className="text-[13px] font-semibold text-ink">Repo indexed</span>
              <span className="text-xs text-subtle">1:52</span>
            </li>
            <li className="flex flex-1 flex-col gap-2">
              <div className="flex items-center">
                <span className="box-border h-3.5 w-3.5 shrink-0 rounded-full bg-accent"></span>
                <span className="mx-1.5 h-0.5 flex-1 bg-accent"></span>
              </div>
              <span className="text-[13px] font-semibold text-ink">Edit plan</span>
              <span className="text-xs text-subtle">3:10</span>
            </li>
            <li className="flex flex-1 flex-col gap-2">
              <div className="flex items-center">
                <span className="box-border h-3.5 w-3.5 shrink-0 rounded-full bg-accent"></span>
                <span className="mx-1.5 h-0.5 flex-1 bg-accent"></span>
              </div>
              <span className="text-[13px] font-semibold text-ink">Code gen</span>
              <span className="text-xs text-subtle">9:41</span>
            </li>
            <li className="flex flex-1 flex-col gap-2">
              <div className="flex items-center">
                <span className="box-border h-3.5 w-3.5 shrink-0 rounded-full bg-accent"></span>
                <span className="mx-1.5 h-0.5 flex-1 bg-accent"></span>
              </div>
              <span className="text-[13px] font-semibold text-ink">Tests</span>
              <span className="text-xs text-subtle">2:26</span>
            </li>
            <li className="flex flex-1 flex-col gap-2">
              <div className="flex items-center">
                <span className="box-border h-3.5 w-3.5 shrink-0 rounded-full border-[3px] border-accent bg-surface"></span>
                <span className="mx-1.5 h-0.5 flex-1 bg-line"></span>
              </div>
              <span className="text-[13px] font-semibold text-ink">PR opened</span>
              <span className="text-xs text-subtle">Awaiting review</span>
            </li>
            <li className="flex flex-1 flex-col gap-2">
              <div className="flex items-center">
                <span className="box-border h-3.5 w-3.5 shrink-0 rounded-full border-2 border-[#3a4466] bg-surface"></span>
              </div>
              <span className="text-[13px] text-subtle">Merged</span>
              <span className="text-xs text-subtle"></span>
            </li>
          </ol>
        </section>
        <div className="flex flex-wrap items-start gap-6">
          <section className="min-w-0 flex-[999_1_600px] rounded-xl border border-line bg-surface">
            <div role="tablist" aria-label="Run output" className="flex flex-wrap gap-1 border-b border-line px-3 pt-2">
              <button type="button" role="tab" id="tab-plan" aria-selected="true" aria-controls="panel-plan" className="-mb-px flex min-h-11 items-center gap-1.5 border-b-2 px-3.5 text-sm font-semibold border-accent text-ink">
Edit plan                <span className="font-mono text-xs text-subtle">5</span>
              </button>
              <button type="button" role="tab" id="tab-diff" aria-selected="false" aria-controls="panel-diff" className="-mb-px flex min-h-11 items-center gap-1.5 border-b-2 px-3.5 text-sm font-semibold border-transparent text-muted hover:text-ink">
Diff                <span className="font-mono text-xs text-subtle">7</span>
              </button>
              <button type="button" role="tab" id="tab-tests" aria-selected="false" aria-controls="panel-tests" className="-mb-px flex min-h-11 items-center gap-1.5 border-b-2 px-3.5 text-sm font-semibold border-transparent text-muted hover:text-ink">
Tests                <span className="font-mono text-xs text-subtle">5</span>
              </button>
              <button type="button" role="tab" id="tab-logs" aria-selected="false" aria-controls="panel-logs" className="-mb-px flex min-h-11 items-center gap-1.5 border-b-2 px-3.5 text-sm font-semibold border-transparent text-muted hover:text-ink">
Logs                <span className="font-mono text-xs text-subtle">10</span>
              </button>
            </div>
            <div role="tabpanel" id="panel-plan" aria-labelledby="tab-plan">
              <div className="flex flex-col gap-2.5 p-5">
                <div className="flex items-start gap-3.5 rounded-[10px] border border-line bg-panel px-3.5 py-3">
                  <span className="shrink-0 rounded-md px-2 py-0.5 text-[11px] font-semibold bg-[#12352a] text-[#6ee7b7]">create</span>
                  <div className="flex min-w-0 flex-col gap-1">
                    <span className="font-mono text-[13px] text-ink [overflow-wrap:anywhere]">src/checkout/ReferralBox.tsx</span>
                    <span className="text-[13px] text-muted">Input for a referral code on the payment step, with inline validation</span>
                    <span className="text-xs text-subtle">
Covers R1, R2
</span>
                  </div>
                </div>
                <div className="flex items-start gap-3.5 rounded-[10px] border border-line bg-panel px-3.5 py-3">
                  <span className="shrink-0 rounded-md px-2 py-0.5 text-[11px] font-semibold bg-[#12352a] text-[#6ee7b7]">create</span>
                  <div className="flex min-w-0 flex-col gap-1">
                    <span className="font-mono text-[13px] text-ink [overflow-wrap:anywhere]">src/api/referrals.ts</span>
                    <span className="text-[13px] text-muted">Validate the code and return the reward for this cart</span>
                    <span className="text-xs text-subtle">
Covers R2, R3
</span>
                  </div>
                </div>
                <div className="flex items-start gap-3.5 rounded-[10px] border border-line bg-panel px-3.5 py-3">
                  <span className="shrink-0 rounded-md px-2 py-0.5 text-[11px] font-semibold bg-[#1a2038] text-ink-2">modify</span>
                  <div className="flex min-w-0 flex-col gap-1">
                    <span className="font-mono text-[13px] text-ink [overflow-wrap:anywhere]">src/checkout/summary.ts</span>
                    <span className="text-[13px] text-muted">Subtract the reward from the order total</span>
                    <span className="text-xs text-subtle">
Covers R3
</span>
                  </div>
                </div>
                <div className="flex items-start gap-3.5 rounded-[10px] border border-line bg-panel px-3.5 py-3">
                  <span className="shrink-0 rounded-md px-2 py-0.5 text-[11px] font-semibold bg-[#1a2038] text-ink-2">modify</span>
                  <div className="flex min-w-0 flex-col gap-1">
                    <span className="font-mono text-[13px] text-ink [overflow-wrap:anywhere]">src/checkout/PaymentStep.tsx</span>
                    <span className="text-[13px] text-muted">Mount ReferralBox above the pay button</span>
                    <span className="text-xs text-subtle">
Covers R1
</span>
                  </div>
                </div>
                <div className="flex items-start gap-3.5 rounded-[10px] border border-line bg-panel px-3.5 py-3">
                  <span className="shrink-0 rounded-md px-2 py-0.5 text-[11px] font-semibold bg-[#12352a] text-[#6ee7b7]">create</span>
                  <div className="flex min-w-0 flex-col gap-1">
                    <span className="font-mono text-[13px] text-ink [overflow-wrap:anywhere]">src/api/referrals.test.ts</span>
                    <span className="text-[13px] text-muted">Unit tests for valid, expired and self-referral codes</span>
                    <span className="text-xs text-subtle">
Covers R4
</span>
                  </div>
                </div>
              </div>
            </div>
          </section>
          <aside className="flex min-w-0 flex-[1_1_320px] flex-col gap-4">
            <section className="flex flex-col gap-3 rounded-xl border border-line bg-surface p-5">
              <div className="flex items-center justify-between gap-2">
                <h2 className="text-[15px] font-semibold">Requirements coverage</h2>
                <span className="text-xs text-subtle">
4 of 4
</span>
              </div>
              <div className="flex items-start gap-2.5">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6ee7b7" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" className="mt-0.5 shrink-0" aria-label="Covered" role="img">
                  <path d="M20 6 9 17l-5-5"></path>
                </svg>
                <div>
                  <div className="text-[13px] leading-snug text-ink">Shopper can enter a referral code on the payment step</div>
                  <div className="font-mono text-[11px] text-subtle">R1</div>
                </div>
              </div>
              <div className="flex items-start gap-2.5">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6ee7b7" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" className="mt-0.5 shrink-0" aria-label="Covered" role="img">
                  <path d="M20 6 9 17l-5-5"></path>
                </svg>
                <div>
                  <div className="text-[13px] leading-snug text-ink">Invalid or expired codes show a clear error</div>
                  <div className="font-mono text-[11px] text-subtle">R2</div>
                </div>
              </div>
              <div className="flex items-start gap-2.5">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6ee7b7" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" className="mt-0.5 shrink-0" aria-label="Covered" role="img">
                  <path d="M20 6 9 17l-5-5"></path>
                </svg>
                <div>
                  <div className="text-[13px] leading-snug text-ink">Reward is applied to the order total</div>
                  <div className="font-mono text-[11px] text-subtle">R3</div>
                </div>
              </div>
              <div className="flex items-start gap-2.5">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6ee7b7" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" className="mt-0.5 shrink-0" aria-label="Covered" role="img">
                  <path d="M20 6 9 17l-5-5"></path>
                </svg>
                <div>
                  <div className="text-[13px] leading-snug text-ink">A shopper cannot use their own code</div>
                  <div className="font-mono text-[11px] text-subtle">R4</div>
                </div>
              </div>
            </section>
            <section className="flex flex-col gap-2.5 rounded-xl border border-line bg-surface p-5">
              <h2 className="text-[15px] font-semibold">Source PRD</h2>
              <p className="text-[13px] leading-normal text-muted">Let shoppers enter a friend&apos;s referral code at checkout and get a reward on their first order.</p>
              <Link className="inline-flex min-h-8 items-center text-[13px] font-semibold text-link hover:text-link-hover" href="/prds">
View PRD · v3
</Link>
            </section>
          </aside>
        </div>
      </main>
    </>
  );
}
