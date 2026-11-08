import type { Metadata } from "next";
import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { OutputModePicker } from "@/components/OutputModePicker";

export const metadata: Metadata = {
  title: 'New run · Galatus',
};

export default function Page() {
  return (
    <>
      <AppHeader />
      <main className="mx-auto flex max-w-[1360px] flex-col gap-6 px-4 pb-12 pt-7 sm:px-8">
        <div>
          <Link className="inline-flex min-h-8 items-center gap-1.5 text-[13px] text-link hover:text-link-hover" href="/">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
              <path d="M15 18l-6-6 6-6"></path>
            </svg>
Back to runs
</Link>
          <h1 className="mt-1 text-[26px] font-bold tracking-tight">New run</h1>
          <p className="mt-1.5 text-sm text-muted">
Give the pipeline a PRD and a repository. It plans the change, writes the code and opens a pull request.
</p>
        </div>
        <div className="flex flex-wrap items-start gap-6">
          <form className="flex min-w-0 flex-[999_1_560px] flex-col gap-5" action="#" encType="multipart/form-data" method="POST">
            <section className="rounded-xl border border-line bg-surface flex flex-col gap-4 p-6">
              <div className="flex items-center gap-2.5">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-ink text-xs font-bold text-canvas">1</span>
                <h2 className="text-base font-semibold">PRD</h2>
              </div>
              <label className="flex flex-col gap-1.5 text-[13px] font-semibold text-ink-2">
<span>Title</span>
<input type="text" placeholder="e.g. Referral rewards at checkout" className="h-11 rounded-lg border border-line-2 bg-surface px-3 text-sm font-normal text-ink outline-none focus:border-accent" name="title" />
              </label>
              <label className="flex flex-col gap-1.5 text-[13px] font-semibold text-ink-2">
<span>Requirements</span>
<textarea name="requirements" rows={7} placeholder="Paste the PRD here: problem, user stories, acceptance criteria…" className="resize-y rounded-lg border border-line-2 p-3 text-sm font-normal leading-relaxed text-ink outline-none focus:border-accent"></textarea>
              </label>
              <label className="flex cursor-pointer flex-wrap items-center justify-between gap-3 rounded-[10px] border-[1.5px] border-dashed border-[#3a4466] bg-panel p-4.5">
                <span>
                  <span className="block text-sm font-semibold">Or upload a file</span>
                  <span className="block text-xs text-subtle">.md, .pdf or .docx</span>
                </span>
                <input type="file" accept=".md,.pdf,.docx" className="text-[13px] file:mr-3 file:h-10 file:rounded-lg file:border file:border-line-2 file:bg-surface file:px-3.5 file:font-semibold" name="prdFile" />
              </label>
            </section>
            <section className="rounded-xl border border-line bg-surface flex flex-col gap-4 p-6">
              <div className="flex items-center gap-2.5">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-ink text-xs font-bold text-canvas">2</span>
                <h2 className="text-base font-semibold">Repository</h2>
              </div>
              <div className="grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-4">
                <label className="flex flex-col gap-1.5 text-[13px] font-semibold text-ink-2">
<span>Repository</span>
<select name="repo" className="h-11 rounded-lg border border-line-2 bg-surface px-3 text-sm font-normal text-ink outline-none focus:border-accent" defaultValue="acme/web-store">
                    <option>acme/web-store</option>
                    <option>acme/crm-api</option>
                    <option>acme/auth-service</option>
                    <option>acme/billing</option>
                    <option>acme/gateway</option>
                  </select>
                </label>
                <label className="flex flex-col gap-1.5 text-[13px] font-semibold text-ink-2">
<span>Base branch</span>
<input type="text" className="h-11 rounded-lg border border-line-2 bg-surface px-3 text-sm font-normal text-ink outline-none focus:border-accent font-mono" name="baseBranch" defaultValue="main" />
                </label>
              </div>
              <div className="flex items-center gap-2 rounded-lg px-3 py-2.5 text-[13px] bg-[#12352a] text-[#6ee7b7]">Index is up to date for this repository</div>
            </section>
            <section className="rounded-xl border border-line bg-surface flex flex-col gap-4 p-6">
              <div className="flex items-center gap-2.5">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-ink text-xs font-bold text-canvas">3</span>
                <h2 className="text-base font-semibold">Output</h2>
              </div>
              <OutputModePicker />
            </section>
            <div className="flex flex-wrap justify-end gap-2.5">
              <Link className="flex h-11 items-center gap-2 rounded-lg border border-line-2 bg-surface px-4 text-sm font-semibold text-ink hover:border-subtle" href="/">Cancel</Link>
              <button type="submit" className="flex h-11 items-center gap-2 rounded-lg bg-accent px-4 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60">Start run</button>
            </div>
          </form>
          <section className="rounded-xl border border-line bg-surface flex min-w-0 flex-[1_1_320px] flex-col gap-3.5 p-5">
            <h2 className="text-[15px] font-semibold">What happens next</h2>
            <ol className="flex flex-col gap-3">
              <li className="flex items-start gap-3">
                <span className="w-[18px] pt-[3px] font-mono text-[11px] text-subtle">01</span>
                <div>
                  <div className="text-sm font-semibold text-ink">PRD parsed</div>
                  <div className="text-xs leading-snug text-subtle">Requirements and acceptance criteria are extracted</div>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-[18px] pt-[3px] font-mono text-[11px] text-subtle">02</span>
                <div>
                  <div className="text-sm font-semibold text-ink">Repo indexed</div>
                  <div className="text-xs leading-snug text-subtle">Embeddings and code graph are refreshed for changed files</div>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-[18px] pt-[3px] font-mono text-[11px] text-subtle">03</span>
                <div>
                  <div className="text-sm font-semibold text-ink">Edit plan</div>
                  <div className="text-xs leading-snug text-subtle">Files to create or modify, with a reason for each</div>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-[18px] pt-[3px] font-mono text-[11px] text-subtle">04</span>
                <div>
                  <div className="text-sm font-semibold text-ink">Code gen</div>
                  <div className="text-xs leading-snug text-subtle">Changes are written on a new branch</div>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-[18px] pt-[3px] font-mono text-[11px] text-subtle">05</span>
                <div>
                  <div className="text-sm font-semibold text-ink">Tests</div>
                  <div className="text-xs leading-snug text-subtle">Your test suite runs against the branch</div>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-[18px] pt-[3px] font-mono text-[11px] text-subtle">06</span>
                <div>
                  <div className="text-sm font-semibold text-ink">PR opened</div>
                  <div className="text-xs leading-snug text-subtle">A pull request with the plan as its description</div>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-[18px] pt-[3px] font-mono text-[11px] text-subtle">07</span>
                <div>
                  <div className="text-sm font-semibold text-ink">Merged</div>
                  <div className="text-xs leading-snug text-subtle">After review on your Git host</div>
                </div>
              </li>
            </ol>
          </section>
        </div>
      </main>
    </>
  );
}
