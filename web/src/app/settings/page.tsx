import type { Metadata } from "next";
import { AppHeader } from "@/components/AppHeader";

export const metadata: Metadata = {
  title: 'Settings · Galatus',
};

export default function Page() {
  return (
    <>
      <AppHeader />
      <main className="mx-auto flex max-w-[1360px] flex-col gap-6 px-4 pb-12 pt-7 sm:px-8">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-[26px] font-bold tracking-tight">Settings</h1>
            <p className="mt-1.5 text-sm text-muted">Connections, models and the defaults every new run starts with.</p>
          </div>
        </div>
        <div className="flex flex-wrap items-start gap-6">
          <nav aria-label="Settings sections" className="flex flex-[1_1_200px] flex-col gap-0.5">
            <a href="#git" aria-current="true" className="rounded-lg px-3 py-2.5 text-sm border border-line bg-surface font-semibold text-ink">Git provider</a>
            <a href="#models" className="rounded-lg px-3 py-2.5 text-sm border border-transparent font-medium text-muted hover:text-ink">Models</a>
            <a href="#defaults" className="rounded-lg px-3 py-2.5 text-sm border border-transparent font-medium text-muted hover:text-ink">Pipeline defaults</a>
            <a href="#keys" className="rounded-lg px-3 py-2.5 text-sm border border-transparent font-medium text-muted hover:text-ink">API keys</a>
          </nav>
          <form className="flex min-w-0 flex-[999_1_640px] flex-col gap-5">
            <section className="rounded-xl border border-line bg-surface flex scroll-mt-6 flex-col gap-4 p-6" id="git">
              <h2 className="text-base font-semibold">Git provider</h2>
              <div className="flex flex-wrap items-center justify-between gap-3 rounded-[10px] border border-line bg-panel px-4 py-3.5">
                <div className="flex items-center gap-3">
                  <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#1a2038]">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <circle cx="6" cy="6" r="2.5"></circle>
                      <circle cx="6" cy="18" r="2.5"></circle>
                      <circle cx="18" cy="9" r="2.5"></circle>
                      <path d="M6 8.5v7M18 11.5c0 3-3 3.5-6 4.5"></path>
                    </svg>
                  </span>
                  <div>
                    <div className="text-sm font-semibold">GitHub App</div>
                    <div className="text-xs text-subtle">
Installed on the                       <span className="font-mono">acme</span>
 organization · 5 repositories                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2.5">
                  <span className="rounded-full bg-[#12352a] px-2.5 py-1 text-xs font-semibold text-[#6ee7b7]">Connected</span>
                  <button type="button" className="h-9 rounded-lg border border-line-2 bg-surface px-3 text-[13px] font-semibold">Manage</button>
                </div>
              </div>
              <label className="flex flex-col gap-1.5 text-[13px] font-semibold text-ink-2 max-w-[420px]">
<span>Branch name pattern</span>
<input className="h-11 rounded-lg border border-line-2 bg-surface px-3 text-sm font-normal text-ink outline-none focus:border-accent font-mono" name="branchPattern" defaultValue="prd/{slug}" />
              </label>
            </section>
            <section className="rounded-xl border border-line bg-surface flex scroll-mt-6 flex-col gap-4 p-6" id="models">
              <h2 className="text-base font-semibold">Models</h2>
              <div className="grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-4">
                <label className="flex flex-col gap-1.5 text-[13px] font-semibold text-ink-2">
<span>Planning model</span>
<select name="planningModel" className="h-11 rounded-lg border border-line-2 bg-surface px-3 text-sm font-normal text-ink outline-none focus:border-accent">
                    <option>[YOUR PLANNING MODEL]</option>
                  </select>
                </label>
                <label className="flex flex-col gap-1.5 text-[13px] font-semibold text-ink-2">
<span>Code model</span>
<select name="codeModel" className="h-11 rounded-lg border border-line-2 bg-surface px-3 text-sm font-normal text-ink outline-none focus:border-accent">
                    <option>[YOUR CODE MODEL]</option>
                  </select>
                </label>
                <label className="flex flex-col gap-1.5 text-[13px] font-semibold text-ink-2">
<span>Embedding model</span>
<select name="embeddingModel" className="h-11 rounded-lg border border-line-2 bg-surface px-3 text-sm font-normal text-ink outline-none focus:border-accent">
                    <option>[YOUR EMBEDDING MODEL]</option>
                  </select>
                </label>
              </div>
              <label className="flex flex-col gap-1.5 text-[13px] font-semibold text-ink-2 max-w-[420px]">
<span>Retrieval: chunks per query</span>
<input type="number" min="1" max="200" className="h-11 rounded-lg border border-line-2 bg-surface px-3 text-sm font-normal text-ink outline-none focus:border-accent" name="topK" defaultValue="24" />
              </label>
            </section>
            <section className="rounded-xl border border-line bg-surface flex scroll-mt-6 flex-col p-6" id="defaults">
              <h2 className="mb-2 text-base font-semibold">Pipeline defaults</h2>
              <div className="divide-y divide-[#1a2038] border-t border-[#1a2038]">
                <div className="flex items-center justify-between gap-4 py-3">
                  <div>
                    <div className="text-sm font-semibold">Edit plan only by default</div>
                    <div className="text-xs text-subtle">New runs stop after the edit plan unless changed</div>
                  </div>
                  <input type="hidden" name="planOnly" defaultValue="off" />
                  <button type="button" role="switch" aria-checked={false} aria-label="Edit plan only by default" className="flex h-[26px] w-11 shrink-0 cursor-pointer rounded-full p-[3px] transition-colors justify-start bg-[#3a4466]">
                    <span className="block h-5 w-5 rounded-full bg-[#f4f2ff]"></span>
                  </button>
                </div>
                <div className="flex items-center justify-between gap-4 py-3">
                  <div>
                    <div className="text-sm font-semibold">Run tests before opening a PR</div>
                    <div className="text-xs text-subtle">A failing suite stops the run</div>
                  </div>
                  <input type="hidden" name="tests" defaultValue="on" />
                  <button type="button" role="switch" aria-checked={true} aria-label="Run tests before opening a PR" className="flex h-[26px] w-11 shrink-0 cursor-pointer rounded-full p-[3px] transition-colors justify-end bg-accent">
                    <span className="block h-5 w-5 rounded-full bg-[#f4f2ff]"></span>
                  </button>
                </div>
                <div className="flex items-center justify-between gap-4 py-3">
                  <div>
                    <div className="text-sm font-semibold">Require human review of the plan</div>
                    <div className="text-xs text-subtle">Code generation waits for approval</div>
                  </div>
                  <input type="hidden" name="review" defaultValue="on" />
                  <button type="button" role="switch" aria-checked={true} aria-label="Require human review of the plan" className="flex h-[26px] w-11 shrink-0 cursor-pointer rounded-full p-[3px] transition-colors justify-end bg-accent">
                    <span className="block h-5 w-5 rounded-full bg-[#f4f2ff]"></span>
                  </button>
                </div>
                <div className="flex items-center justify-between gap-4 py-3">
                  <div>
                    <div className="text-sm font-semibold">Open PRs as drafts</div>
                    <div className="text-xs text-subtle">Mark ready for review by hand</div>
                  </div>
                  <input type="hidden" name="draft" defaultValue="on" />
                  <button type="button" role="switch" aria-checked={true} aria-label="Open PRs as drafts" className="flex h-[26px] w-11 shrink-0 cursor-pointer rounded-full p-[3px] transition-colors justify-end bg-accent">
                    <span className="block h-5 w-5 rounded-full bg-[#f4f2ff]"></span>
                  </button>
                </div>
              </div>
            </section>
            <section className="rounded-xl border border-line bg-surface flex scroll-mt-6 flex-col gap-3 p-6" id="keys">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h2 className="text-base font-semibold">API keys</h2>
                <button type="button" className="h-9 rounded-lg border border-line-2 bg-surface px-3 text-[13px] font-semibold">Create key</button>
              </div>
              <p className="text-[13px] text-muted">Use a key to trigger runs from CI or the CLI.</p>
              <div className="flex flex-wrap items-center justify-between gap-3 rounded-[10px] border border-line px-3.5 py-3">
                <div className="flex flex-col gap-0.5">
                  <span className="text-sm font-semibold">CI — GitHub Actions</span>
                  <span className="font-mono text-xs text-subtle">
ptp_••••••••3f9a · created Oct 12
</span>
                </div>
                <button type="button" className="h-9 rounded-lg border border-[#5a2433] bg-surface px-3 text-[13px] font-semibold text-[#ff8fa3]">Revoke</button>
              </div>
              <div className="flex flex-wrap items-center justify-between gap-3 rounded-[10px] border border-line px-3.5 py-3">
                <div className="flex flex-col gap-0.5">
                  <span className="text-sm font-semibold">Local CLI</span>
                  <span className="font-mono text-xs text-subtle">
ptp_••••••••b41c · created Nov 2
</span>
                </div>
                <button type="button" className="h-9 rounded-lg border border-[#5a2433] bg-surface px-3 text-[13px] font-semibold text-[#ff8fa3]">Revoke</button>
              </div>
            </section>
            <div className="flex items-center justify-end gap-3">
              <button type="submit" className="flex h-11 items-center gap-2 rounded-lg bg-accent px-4 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60">Save changes</button>
            </div>
          </form>
        </div>
      </main>
    </>
  );
}
