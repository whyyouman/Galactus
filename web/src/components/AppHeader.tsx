"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Runs" },
  { href: "/repositories", label: "Repositories" },
  { href: "/prds", label: "PRDs" },
  { href: "/settings", label: "Settings" },
] as const;

function navClass(active: boolean) {
  return active
    ? "rounded-lg px-3 py-2.5 text-sm bg-[#1a2038] font-semibold text-ink"
    : "rounded-lg px-3 py-2.5 text-sm font-medium text-muted transition-colors hover:bg-[#1a2038] hover:text-ink";
}

export function AppHeader() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-10 border-b border-[#1e2540] bg-[rgb(7_10_20_/_.85)] backdrop-blur-md">
      <div className="mx-auto flex max-w-[1360px] flex-wrap items-center justify-between gap-4 px-4 py-3.5 sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-center gap-7">
          <Link href="/" className="flex items-center gap-2.5 text-ink">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-sm font-bold text-white">
              G
            </span>
            <span className="font-display text-[17px] font-bold tracking-[0.16em]">GALATUS</span>
          </Link>
          <nav className="flex flex-wrap gap-1" aria-label="Primary">
            {NAV.map((item) => {
              const active =
                item.href === "/"
                  ? pathname === "/"
                  : pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link key={item.href} href={item.href} className={navClass(active)}>
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <label className="flex h-10 min-w-[220px] items-center gap-2 rounded-lg border border-line bg-panel px-3 text-muted">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
            <span className="sr-only">Search runs</span>
            <input
              className="w-full bg-transparent text-sm outline-none placeholder:text-subtle"
              placeholder="Search runs"
              type="search"
            />
          </label>
          <Link
            href="/new-run"
            className="flex h-11 items-center gap-2 rounded-lg bg-accent px-4 text-sm font-semibold text-white transition-colors hover:bg-accent-hover"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M12 5v14M5 12h14" />
            </svg>
            New run
          </Link>
        </div>
      </div>
    </header>
  );
}
