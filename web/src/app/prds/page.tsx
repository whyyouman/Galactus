import type { Metadata } from "next";
import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";

export const metadata: Metadata = {
  title: 'PRDs · Galatus',
};

export default function Page() {
  return (
    <>
      <AppHeader />
      <main className="mx-auto flex max-w-[1360px] flex-col gap-6 px-4 pb-12 pt-7 sm:px-8">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-[26px] font-bold tracking-tight">PRDs</h1>
            <p className="mt-1.5 text-sm text-muted">Product requirement documents and the runs created from each version.</p>
          </div>
          <Link className="flex h-11 items-center gap-2 rounded-lg border border-line-2 bg-surface px-4 text-sm font-semibold text-ink hover:border-subtle" href="/new-run">Add PRD</Link>
        </div>
        <div className="flex flex-wrap items-start gap-6">
          <section aria-label="PRD list" className="min-w-0 flex-[999_1_560px] rounded-xl border border-line bg-surface">
            <div className="border-b border-line px-5 py-4">
              <label className="flex h-10 max-w-[360px] items-center gap-2 rounded-lg border border-line-2 px-3">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#8d96b3" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
                  <circle cx="11" cy="11" r="7"></circle>
                  <path d="m20 20-3.5-3.5"></path>
                </svg>
                <span className="sr-only">Search PRDs</span>
                <input type="search" placeholder="Search PRDs" className="w-full bg-transparent text-sm outline-none placeholder:text-subtle" />
              </label>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[680px] border-collapse text-sm">
                <thead>
                  <tr className="text-left text-xs text-muted">
                    <th className="px-5 py-3 font-semibold">Title</th>
                    <th className="px-3 py-3 font-semibold">Author</th>
                    <th className="px-3 py-3 font-semibold">Version</th>
                    <th className="px-3 py-3 font-semibold">Runs</th>
                    <th className="px-3 py-3 font-semibold">Latest run</th>
                    <th className="py-3 pl-3 pr-5 font-semibold">Updated</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-t border-[#1a2038] bg-accent-soft shadow-[inset_3px_0_0_var(--color-accent)]">
                    <td className="px-5 py-3">
                      <button type="button" aria-current="true" className="min-h-11 cursor-pointer text-left font-semibold text-ink">Referral rewards at checkout</button>
                    </td>
                    <td className="px-3 py-3 text-ink-2">Priya M.</td>
                    <td className="px-3 py-3 font-mono text-ink-2">
v3                    </td>
                    <td className="px-3 py-3 font-mono text-ink-2">1</td>
                    <td className="px-3 py-3">
                      <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#3a2a12] text-[#f5c26b]">Needs review</span>
                    </td>
                    <td className="whitespace-nowrap py-3 pl-3 pr-5 text-muted">40 min ago</td>
                  </tr>
                  <tr className="border-t border-[#1a2038] bg-surface hover:bg-panel">
                    <td className="px-5 py-3">
                      <button type="button" className="min-h-11 cursor-pointer text-left font-semibold text-ink">Bulk CSV import for leads</button>
                    </td>
                    <td className="px-3 py-3 text-ink-2">Rahul K.</td>
                    <td className="px-3 py-3 font-mono text-ink-2">
v2                    </td>
                    <td className="px-3 py-3 font-mono text-ink-2">1</td>
                    <td className="px-3 py-3">
                      <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#16264a] text-[#8db4ff]">In progress</span>
                    </td>
                    <td className="whitespace-nowrap py-3 pl-3 pr-5 text-muted">2 h ago</td>
                  </tr>
                  <tr className="border-t border-[#1a2038] bg-surface hover:bg-panel">
                    <td className="px-5 py-3">
                      <button type="button" className="min-h-11 cursor-pointer text-left font-semibold text-ink">Google Workspace SSO</button>
                    </td>
                    <td className="px-3 py-3 text-ink-2">Ankit S.</td>
                    <td className="px-3 py-3 font-mono text-ink-2">
v1                    </td>
                    <td className="px-3 py-3 font-mono text-ink-2">1</td>
                    <td className="px-3 py-3">
                      <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#12352a] text-[#6ee7b7]">Merged</span>
                    </td>
                    <td className="whitespace-nowrap py-3 pl-3 pr-5 text-muted">Yesterday</td>
                  </tr>
                  <tr className="border-t border-[#1a2038] bg-surface hover:bg-panel">
                    <td className="px-5 py-3">
                      <button type="button" className="min-h-11 cursor-pointer text-left font-semibold text-ink">Invoice PDF redesign</button>
                    </td>
                    <td className="px-3 py-3 text-ink-2">Neha G.</td>
                    <td className="px-3 py-3 font-mono text-ink-2">
v2                    </td>
                    <td className="px-3 py-3 font-mono text-ink-2">1</td>
                    <td className="px-3 py-3">
                      <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#3d1620] text-[#ff8fa3]">Failed</span>
                    </td>
                    <td className="whitespace-nowrap py-3 pl-3 pr-5 text-muted">2 days ago</td>
                  </tr>
                  <tr className="border-t border-[#1a2038] bg-surface hover:bg-panel">
                    <td className="px-5 py-3">
                      <button type="button" className="min-h-11 cursor-pointer text-left font-semibold text-ink">Notification preferences page</button>
                    </td>
                    <td className="px-3 py-3 text-ink-2">Priya M.</td>
                    <td className="px-3 py-3 font-mono text-ink-2">
v1                    </td>
                    <td className="px-3 py-3 font-mono text-ink-2">1</td>
                    <td className="px-3 py-3">
                      <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#16264a] text-[#8db4ff]">In progress</span>
                    </td>
                    <td className="whitespace-nowrap py-3 pl-3 pr-5 text-muted">3 days ago</td>
                  </tr>
                  <tr className="border-t border-[#1a2038] bg-surface hover:bg-panel">
                    <td className="px-5 py-3">
                      <button type="button" className="min-h-11 cursor-pointer text-left font-semibold text-ink">Rate-limit public API</button>
                    </td>
                    <td className="px-3 py-3 text-ink-2">Ankit S.</td>
                    <td className="px-3 py-3 font-mono text-ink-2">
v1                    </td>
                    <td className="px-3 py-3 font-mono text-ink-2">1</td>
                    <td className="px-3 py-3">
                      <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#12352a] text-[#6ee7b7]">Merged</span>
                    </td>
                    <td className="whitespace-nowrap py-3 pl-3 pr-5 text-muted">6 days ago</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
          <aside aria-label="PRD preview" className="flex min-w-0 flex-[1_1_340px] flex-col gap-4.5 rounded-xl border border-line bg-surface p-5">
            <div className="flex flex-col gap-1.5">
              <span className="text-xs text-subtle">
Priya M. · v3 · 40 min ago
</span>
              <h2 className="text-lg font-bold tracking-tight">Referral rewards at checkout</h2>
              <p className="text-[13px] leading-normal text-muted">Let shoppers enter a friend&apos;s referral code at checkout and get a reward on their first order.</p>
            </div>
            <div>
              <h3 className="mb-2.5 text-[13px] font-semibold text-muted">Acceptance criteria</h3>
              <ul className="flex flex-col gap-2">
                <li className="flex gap-2.5 text-[13px] leading-snug">
                  <span className="pt-0.5 font-mono text-[11px] text-subtle">R1</span>
Shopper can enter a referral code on the payment step                </li>
                <li className="flex gap-2.5 text-[13px] leading-snug">
                  <span className="pt-0.5 font-mono text-[11px] text-subtle">R2</span>
Invalid or expired codes show a clear error                </li>
                <li className="flex gap-2.5 text-[13px] leading-snug">
                  <span className="pt-0.5 font-mono text-[11px] text-subtle">R3</span>
Reward is applied to the order total                </li>
                <li className="flex gap-2.5 text-[13px] leading-snug">
                  <span className="pt-0.5 font-mono text-[11px] text-subtle">R4</span>
A shopper cannot use their own code                </li>
              </ul>
            </div>
            <div>
              <h3 className="mb-2.5 text-[13px] font-semibold text-muted">Versions</h3>
              <div className="flex flex-col gap-1.5">
                <div className="flex justify-between gap-2 rounded-lg border border-line bg-panel px-2.5 py-2 text-[13px]">
                  <span className="font-mono">
v3
</span>
                  <span className="text-muted">Added self-referral rule</span>
                </div>
                <div className="flex justify-between gap-2 rounded-lg border border-line bg-panel px-2.5 py-2 text-[13px]">
                  <span className="font-mono">
v2
</span>
                  <span className="text-muted">Reward capped at order total</span>
                </div>
                <div className="flex justify-between gap-2 rounded-lg border border-line bg-panel px-2.5 py-2 text-[13px]">
                  <span className="font-mono">
v1
</span>
                  <span className="text-muted">First draft</span>
                </div>
              </div>
            </div>
            <div className="flex flex-wrap gap-2.5">
              <Link className="flex h-11 items-center rounded-lg bg-accent px-4 text-sm font-semibold text-white hover:bg-accent-hover" href="/new-run">Start run from this PRD</Link>
              <Link className="flex h-11 items-center rounded-lg border border-line-2 px-4 text-sm font-semibold text-ink hover:border-subtle" href="/run-detail">Latest run</Link>
            </div>
          </aside>
        </div>
      </main>
    </>
  );
}
