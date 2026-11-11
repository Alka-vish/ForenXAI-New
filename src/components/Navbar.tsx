import React from "react";
import { ShieldCheck, Activity, Sun, UserRound } from "lucide-react";

export type PageId =
  | "dashboard"
  | "new-investigation"
  | "workspace"
  | "history"
  | "reports"
  | "result";

interface NavbarProps {
  currentPage: PageId;
  onNavigate: (page: PageId) => void;
}

interface NavLinkItem {
  id: PageId;
  label: string;
}

const NAV_LINKS: NavLinkItem[] = [
  { id: "dashboard", label: "Dashboard" },
  { id: "new-investigation", label: "New Investigation" },
  { id: "workspace", label: "Workspace" },
  { id: "history", label: "History" },
  { id: "reports", label: "Reports" },
];

export const Navbar: React.FC<NavbarProps> = ({ currentPage, onNavigate }) => {
  return (
    <header
      id="top-navbar"
      className="
        sticky top-0 z-50 w-full
        border-b border-red-500/20
        bg-[#050608]/90 text-white
        backdrop-blur-2xl
      "
    >
      {/* Neon bottom border */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-red-500 to-transparent opacity-80" />

      <div className="mx-auto flex h-[86px] max-w-[1500px] items-center justify-between gap-6 px-5 sm:px-8">
        {/* =====================================================
            BRAND
        ===================================================== */}

        <button
          id="nav-brand"
          type="button"
          onClick={() => onNavigate("dashboard")}
          className="
            group flex shrink-0 items-center gap-3
            cursor-pointer
          "
        >
          {/* Shield Logo */}
          <div
            className="
              relative flex h-14 w-14 items-center justify-center
              rounded-xl border border-red-500
              bg-gradient-to-br from-red-500/20 to-red-950/30
              shadow-[0_0_22px_rgba(255,23,68,0.18)]
              transition-all duration-300
              group-hover:border-red-400
              group-hover:shadow-[0_0_32px_rgba(255,23,68,0.4)]
            "
          >
            <div className="absolute inset-1 rounded-lg border border-red-500/20" />

            <ShieldCheck
              className="
                relative z-10 h-8 w-8
                text-red-500
                transition-transform duration-300
                group-hover:scale-110
              "
              strokeWidth={1.8}
            />
          </div>

          {/* Wordmark */}
          <div className="text-left">
            <span className="block text-[24px] font-black leading-none tracking-tight">
              <span className="text-white">Foren</span>
              <span className="text-red-500">XAI</span>
            </span>

            <span
              className="
                mt-1 block text-[9px] font-semibold
                uppercase tracking-[0.24em]
                text-slate-400
              "
            >
              Forensic Intelligence
            </span>
          </div>
        </button>

        {/* =====================================================
            NAVIGATION
        ===================================================== */}

        <nav
          id="nav-links"
          className="
            hidden items-center gap-1
            overflow-x-auto py-2
            lg:flex
          "
        >
          {NAV_LINKS.map((link) => {
            const isActive =
              currentPage === link.id ||
              (link.id === "new-investigation" && currentPage === "result");

            return (
              <button
                key={link.id}
                id={`nav-link-${link.id}`}
                type="button"
                onClick={() => onNavigate(link.id)}
                className={`
                  relative whitespace-nowrap
                  rounded-xl px-4 py-3
                  text-sm font-semibold
                  transition-all duration-300

                  ${
                    isActive
                      ? `
                        border border-red-500/40
                        bg-red-500/10
                        text-red-400
                        shadow-[0_0_18px_rgba(255,23,68,0.08)]
                      `
                      : `
                        border border-transparent
                        text-slate-400
                        hover:border-white/10
                        hover:bg-white/[0.04]
                        hover:text-white
                      `
                  }
                `}
              >
                {link.label}

                {isActive && (
                  <span
                    className="
                      absolute -bottom-[1px]
                      left-1/2 h-[2px] w-8
                      -translate-x-1/2
                      rounded-full bg-red-500
                      shadow-[0_0_10px_rgba(255,23,68,0.8)]
                    "
                  />
                )}
              </button>
            );
          })}
        </nav>

        {/* =====================================================
            RIGHT STATUS CONTROLS
        ===================================================== */}

        <div className="flex items-center gap-3">
          {/* System Status */}
          <div
            className="
              hidden items-center gap-2
              rounded-xl border border-emerald-400/20
              bg-emerald-400/[0.04]
              px-4 py-2.5
              text-xs text-slate-300
              sm:flex
            "
          >
            <span
              className="
                h-2.5 w-2.5 rounded-full
                bg-emerald-400
                shadow-[0_0_12px_rgba(52,211,153,0.8)]
              "
            />

            <span>System Online</span>
          </div>

          {/* Theme Indicator */}
          <button
            type="button"
            aria-label="Theme"
            className="
              hidden h-11 w-11 items-center justify-center
              rounded-full border border-white/10
              text-slate-400
              transition-all
              hover:border-red-500/40
              hover:bg-red-500/10
              hover:text-red-400
              sm:flex
            "
          >
            <Sun className="h-5 w-5" strokeWidth={1.6} />
          </button>

          {/* Profile */}
          <button
            type="button"
            aria-label="Profile"
            className="
              flex h-11 w-11 items-center justify-center
              rounded-full border border-white/10
              text-slate-400
              transition-all
              hover:border-red-500/40
              hover:bg-red-500/10
              hover:text-red-400
            "
          >
            <UserRound className="h-5 w-5" strokeWidth={1.6} />
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      <nav
        className="
          flex gap-1 overflow-x-auto
          border-t border-white/5
          px-4 py-2
          lg:hidden
        "
      >
        {NAV_LINKS.map((link) => {
          const isActive =
            currentPage === link.id ||
            (link.id === "new-investigation" && currentPage === "result");

          return (
            <button
              key={link.id}
              type="button"
              onClick={() => onNavigate(link.id)}
              className={`
                whitespace-nowrap rounded-lg
                px-3 py-2 text-xs font-semibold
                transition-colors

                ${
                  isActive
                    ? "bg-red-500/10 text-red-400"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                }
              `}
            >
              {link.label}
            </button>
          );
        })}
      </nav>
    </header>
  );
};
