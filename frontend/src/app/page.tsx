import { AppShell } from "@/components/AppShell";
import { Navbar } from "@/components/Navbar";
import { HeroSection } from "@/components/HeroSection";
import { TrustIndicatorStrip } from "@/components/TrustIndicatorStrip";

export default function Home() {
  return (
    <AppShell>
      <Navbar />
      <main id="main-content" className="flex-grow">
        <HeroSection />
        <TrustIndicatorStrip />
      </main>
      <footer className="bg-slate-900 border-t border-slate-800 py-8 text-center text-xs text-slate-400">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p>© {new Date().getFullYear()} ScholarBridge. Built for international student discovery.</p>
        </div>
      </footer>
    </AppShell>
  );
}
