import type { Metadata } from "next";
import { AppHeader } from "@/components/AppHeader";

export const metadata: Metadata = {
  title: 'Repositories · Galatus',
};

export default function Page() {
  return (
    <>
      <AppHeader />
      <main className="mx-auto flex max-w-[1360px] flex-col gap-6 px-4 pb-12 pt-7 sm:px-8">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-[26px] font-bold tracking-tight">Repositories</h1>
            <p className="mt-1.5 text-sm text-muted">Code the pipeline can read and change. Each repo keeps an embeddings index and a code graph.</p>
          </div>
          <button type="button" className="flex h-11 items-center gap-2 rounded-lg border border-line-2 bg-surface px-4 text-sm font-semibold text-ink hover:border-subtle">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
              <path d="M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"></path>
              <path d="M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"></path>
            </svg>
Connect repository
</button>
        </div>
        <section aria-label="Index summary" className="grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-4">
          <div className="flex flex-col gap-1.5 rounded-xl border border-line bg-surface px-5 py-4.5">
            <span className="text-[13px] font-medium text-muted">Connected repositories</span>
            <span className="text-[26px] font-bold tracking-tight">5</span>
          </div>
          <div className="flex flex-col gap-1.5 rounded-xl border border-line bg-surface px-5 py-4.5">
            <span className="text-[13px] font-medium text-muted">Files indexed</span>
            <span className="text-[26px] font-bold tracking-tight">2,938</span>
          </div>
          <div className="flex flex-col gap-1.5 rounded-xl border border-line bg-surface px-5 py-4.5">
            <span className="text-[13px] font-medium text-muted">Need re-index</span>
            <span className="text-[26px] font-bold tracking-tight">1</span>
          </div>
        </section>
        <section aria-label="Repository list" className="relative overflow-x-auto rounded-xl border border-line bg-surface">
          <table className="w-full min-w-[900px] border-collapse text-sm">
            <thead>
              <tr className="text-left text-xs text-muted">
                <th className="px-5 py-3.5 font-semibold">Repository</th>
                <th className="px-3 py-3.5 font-semibold">Branch</th>
                <th className="px-3 py-3.5 font-semibold">Index</th>
                <th className="px-3 py-3.5 font-semibold">Files</th>
                <th className="px-3 py-3.5 font-semibold">Chunks</th>
                <th className="px-3 py-3.5 font-semibold">Graph nodes</th>
                <th className="px-3 py-3.5 font-semibold">Last indexed</th>
                <th className="py-3.5 pl-3 pr-5 font-semibold">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t border-[#1a2038]">
                <td className="px-5 py-3.5">
                  <div className="flex flex-col gap-0.5">
                    <span className="font-mono text-[13px] font-medium">acme/web-store</span>
                    <span className="text-xs text-subtle">TypeScript · Next.js</span>
                  </div>
                </td>
                <td className="px-3 py-3.5 font-mono text-[13px] text-ink-2">main</td>
                <td className="px-3 py-3.5">
                  <div className="flex min-w-[110px] flex-col gap-1.5">
                    <span>
                      <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#12352a] text-[#6ee7b7]">Indexed</span>
                    </span>
                  </div>
                </td>
                <td className="px-3 py-3.5 font-mono text-ink-2">1,284</td>
                <td className="px-3 py-3.5 font-mono text-ink-2">9,412</td>
                <td className="px-3 py-3.5 font-mono text-ink-2">6,030</td>
                <td className="whitespace-nowrap px-3 py-3.5 text-muted">14 min ago</td>
                <td className="py-3.5 pl-3 pr-5 text-right">
                  <button type="button" className="h-9 whitespace-nowrap rounded-lg border border-line-2 bg-surface px-3 text-[13px] font-semibold text-ink hover:border-subtle disabled:cursor-not-allowed disabled:opacity-50">Re-index</button>
                </td>
              </tr>
              <tr className="border-t border-[#1a2038]">
                <td className="px-5 py-3.5">
                  <div className="flex flex-col gap-0.5">
                    <span className="font-mono text-[13px] font-medium">acme/crm-api</span>
                    <span className="text-xs text-subtle">TypeScript · NestJS</span>
                  </div>
                </td>
                <td className="px-3 py-3.5 font-mono text-[13px] text-ink-2">main</td>
                <td className="px-3 py-3.5">
                  <div className="flex min-w-[110px] flex-col gap-1.5">
                    <span>
                      <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#16264a] text-[#8db4ff]">Indexing</span>
                    </span>
                    <div className="h-1 w-[110px] overflow-hidden rounded bg-[#1e2540]" role="progressbar" aria-valuenow={62} aria-valuemin={0} aria-valuemax={100} aria-label="Indexing acme/crm-api">
                      <div className="h-full rounded bg-accent" style={{ width: "62%" }}></div>
                    </div>
                  </div>
                </td>
                <td className="px-3 py-3.5 font-mono text-ink-2">612</td>
                <td className="px-3 py-3.5 font-mono text-ink-2">4,118</td>
                <td className="px-3 py-3.5 font-mono text-ink-2">2,977</td>
                <td className="whitespace-nowrap px-3 py-3.5 text-muted">In progress</td>
                <td className="py-3.5 pl-3 pr-5 text-right">
                  <button type="button" disabled={true} className="h-9 whitespace-nowrap rounded-lg border border-line-2 bg-surface px-3 text-[13px] font-semibold text-ink hover:border-subtle disabled:cursor-not-allowed disabled:opacity-50">Re-index</button>
                </td>
              </tr>
              <tr className="border-t border-[#1a2038]">
                <td className="px-5 py-3.5">
                  <div className="flex flex-col gap-0.5">
                    <span className="font-mono text-[13px] font-medium">acme/auth-service</span>
                    <span className="text-xs text-subtle">Go</span>
                  </div>
                </td>
                <td className="px-3 py-3.5 font-mono text-[13px] text-ink-2">main</td>
                <td className="px-3 py-3.5">
                  <div className="flex min-w-[110px] flex-col gap-1.5">
                    <span>
                      <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#12352a] text-[#6ee7b7]">Indexed</span>
                    </span>
                  </div>
                </td>
                <td className="px-3 py-3.5 font-mono text-ink-2">348</td>
                <td className="px-3 py-3.5 font-mono text-ink-2">2,204</td>
                <td className="px-3 py-3.5 font-mono text-ink-2">1,512</td>
                <td className="whitespace-nowrap px-3 py-3.5 text-muted">2 h ago</td>
                <td className="py-3.5 pl-3 pr-5 text-right">
                  <button type="button" className="h-9 whitespace-nowrap rounded-lg border border-line-2 bg-surface px-3 text-[13px] font-semibold text-ink hover:border-subtle disabled:cursor-not-allowed disabled:opacity-50">Re-index</button>
                </td>
              </tr>
              <tr className="border-t border-[#1a2038]">
                <td className="px-5 py-3.5">
                  <div className="flex flex-col gap-0.5">
                    <span className="font-mono text-[13px] font-medium">acme/billing</span>
                    <span className="text-xs text-subtle">Python · FastAPI</span>
                  </div>
                </td>
                <td className="px-3 py-3.5 font-mono text-[13px] text-ink-2">develop</td>
                <td className="px-3 py-3.5">
                  <div className="flex min-w-[110px] flex-col gap-1.5">
                    <span>
                      <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#3a2a12] text-[#f5c26b]">Stale</span>
                    </span>
                  </div>
                </td>
                <td className="px-3 py-3.5 font-mono text-ink-2">503</td>
                <td className="px-3 py-3.5 font-mono text-ink-2">3,390</td>
                <td className="px-3 py-3.5 font-mono text-ink-2">2,145</td>
                <td className="whitespace-nowrap px-3 py-3.5 text-muted">6 days ago</td>
                <td className="py-3.5 pl-3 pr-5 text-right">
                  <button type="button" className="h-9 whitespace-nowrap rounded-lg border border-line-2 bg-surface px-3 text-[13px] font-semibold text-ink hover:border-subtle disabled:cursor-not-allowed disabled:opacity-50">Re-index</button>
                </td>
              </tr>
              <tr className="border-t border-[#1a2038]">
                <td className="px-5 py-3.5">
                  <div className="flex flex-col gap-0.5">
                    <span className="font-mono text-[13px] font-medium">acme/gateway</span>
                    <span className="text-xs text-subtle">TypeScript · Express</span>
                  </div>
                </td>
                <td className="px-3 py-3.5 font-mono text-[13px] text-ink-2">main</td>
                <td className="px-3 py-3.5">
                  <div className="flex min-w-[110px] flex-col gap-1.5">
                    <span>
                      <span className="inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold bg-[#12352a] text-[#6ee7b7]">Indexed</span>
                    </span>
                  </div>
                </td>
                <td className="px-3 py-3.5 font-mono text-ink-2">191</td>
                <td className="px-3 py-3.5 font-mono text-ink-2">1,066</td>
                <td className="px-3 py-3.5 font-mono text-ink-2">702</td>
                <td className="whitespace-nowrap px-3 py-3.5 text-muted">Yesterday</td>
                <td className="py-3.5 pl-3 pr-5 text-right">
                  <button type="button" className="h-9 whitespace-nowrap rounded-lg border border-line-2 bg-surface px-3 text-[13px] font-semibold text-ink hover:border-subtle disabled:cursor-not-allowed disabled:opacity-50">Re-index</button>
                </td>
              </tr>
            </tbody>
          </table>
        </section>
      </main>
    </>
  );
}
