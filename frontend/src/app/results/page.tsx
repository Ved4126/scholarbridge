"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { Navbar } from "@/components/Navbar";
import { ScholarshipCard } from "@/components/ScholarshipCard";
import { EmptyState } from "@/components/EmptyState";
import { ErrorAlert } from "@/components/ErrorAlert";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { ScoringResult, scoreAll } from "@/lib/api";
import { ArrowLeft, Edit2 } from "lucide-react";

export default function ResultsPage() {
  const router = useRouter();
  const [results, setResults] = useState<ScoringResult[] | null>(null);
  const [completeness, setCompleteness] = useState<number | null>(null);
  const [profileId, setProfileId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Read from session storage on mount
    const cachedResults = sessionStorage.getItem("scholarship_results");
    const cachedCompleteness = sessionStorage.getItem("profile_completeness");
    const cachedProfileId = sessionStorage.getItem("profile_id");

    if (cachedProfileId) {
      setProfileId(cachedProfileId);
    }
    if (cachedCompleteness) {
      setCompleteness(parseFloat(cachedCompleteness));
    }

    const fetchMatches = async (id: string) => {
      try {
        const matches = await scoreAll(id);
        setResults(matches);
        sessionStorage.setItem("scholarship_results", JSON.stringify(matches));
      } catch (err: unknown) {
        console.error(err);
        setError(err instanceof Error ? err.message : "Failed to load scholarship matches.");
      } finally {
        setLoading(false);
      }
    };

    if (cachedResults) {
      try {
        setResults(JSON.parse(cachedResults));
        setLoading(false);
      } catch {
        if (cachedProfileId) {
          fetchMatches(cachedProfileId);
        } else {
          setLoading(false);
        }
      }
    } else if (cachedProfileId) {
      fetchMatches(cachedProfileId);
    } else {
      setLoading(false);
    }
  }, []);

  const handleEditProfile = () => {
    router.push("/profile");
  };

  const handleRetry = () => {
    if (!profileId) return;
    setLoading(true);
    setError(null);
    scoreAll(profileId)
      .then((matches) => {
        setResults(matches);
        sessionStorage.setItem("scholarship_results", JSON.stringify(matches));
      })
      .catch((err: unknown) => {
        console.error(err);
        setError(err instanceof Error ? err.message : "Failed to load scholarship matches.");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <AppShell>
      <Navbar />
      <main id="main-content" className="flex-grow max-w-4xl mx-auto w-full px-4 sm:px-6 py-10">
        {/* Navigation & Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <button
              onClick={handleEditProfile}
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors focus:outline-none mb-2"
            >
              <ArrowLeft className="h-4.5 w-4.5" />
              Back to form
            </button>
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Your Scholarship Matches</h1>
            <p className="text-sm text-slate-600 mt-1">
              Deterministic compatibility matches based on your profile inputs.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            {completeness !== null && (
              <div className="bg-white border border-slate-200 rounded-xl px-4 py-2 text-right">
                <span className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                  Profile Completeness
                </span>
                <span className="text-base font-bold text-slate-900">{completeness}%</span>
              </div>
            )}
            <button
              onClick={handleEditProfile}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 active:bg-slate-100 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
            >
              <Edit2 className="h-4 w-4" />
              Edit Profile
            </button>
          </div>
        </div>

        {/* Content Area */}
        {loading ? (
          <LoadingSkeleton />
        ) : error ? (
          <ErrorAlert message={error} onRetry={handleRetry} />
        ) : !results || results.length === 0 ? (
          <EmptyState
            message="No scholarships matched your current profile above the 40% compatibility threshold. Try editing your profile to add optional achievements or fill in missing fields."
            actionLabel="Edit Profile"
            onAction={handleEditProfile}
          />
        ) : (
          <div className="space-y-6">
            <p className="text-sm font-semibold text-slate-700">
              {results.length} scholarship{results.length > 1 ? "s" : ""} matched your profile
            </p>
            <div className="space-y-6">
              {results.map((result) => (
                <ScholarshipCard key={result.scholarship_id} result={result} />
              ))}
            </div>
          </div>
        )}

        {/* Essential Notice Footer */}
        <div className="mt-12 pt-6 border-t border-slate-200 text-center text-xs text-slate-500 max-w-2xl mx-auto leading-relaxed">
          <p>
            Match scores are based on the information provided in your profile.
            Always verify eligibility criteria and application deadlines directly on the official scholarship website before applying.
          </p>
        </div>
      </main>
      <footer className="bg-slate-900 border-t border-slate-800 py-8 text-center text-xs text-slate-400">
        <p>© {new Date().getFullYear()} ScholarBridge. Built for international student discovery.</p>
      </footer>
    </AppShell>
  );
}
