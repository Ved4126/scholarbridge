import Link from "next/link";
import { GraduationCap } from "lucide-react";

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/80 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Link href="/" className="flex items-center gap-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 rounded-lg p-1">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-600 text-white">
                <GraduationCap className="h-5.5 w-5.5" />
              </div>
              <span className="text-xl font-bold text-slate-900 tracking-tight">
                Scholar<span className="text-emerald-600">Bridge</span>
              </span>
            </Link>
          </div>
          <nav className="flex items-center gap-4">
            <Link
              href="/profile"
              className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 rounded-md px-2 py-1"
            >
              Find Scholarships
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
