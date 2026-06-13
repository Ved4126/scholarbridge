import { ScoringResult } from "@/lib/api";
import { MatchScoreBadge } from "./MatchScoreBadge";
import { DeadlineBadge } from "./DeadlineBadge";
import { GapAnalysisPanel } from "./GapAnalysisPanel";
import { ActionChecklistPanel } from "./ActionChecklistPanel";
import { ExternalLink } from "lucide-react";

interface ScholarshipCardProps {
  result: ScoringResult;
}

export function ScholarshipCard({ result }: ScholarshipCardProps) {
  // Determine matched features to display "Why you matched"
  // If a feature is not in gap_analysis and not an output feature, it matched!
  // However, we only display a few clean bullet points.
  const matchedPoints: string[] = [];
  if (result.score >= 90) {
    matchedPoints.push("Strong fit across all academic and financial fields.");
  } else if (result.score >= 70) {
    matchedPoints.push("Good alignment with most academic requirements.");
  } else {
    matchedPoints.push("Partial match based on student demographics.");
  }

  return (
    <article className="bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow duration-200 p-6 flex flex-col gap-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            {result.org_name}
          </span>
          <h3 className="text-lg sm:text-xl font-bold text-slate-900 leading-snug">
            {result.name}
          </h3>
        </div>
        <div className="flex flex-col sm:items-end gap-2 shrink-0">
          <MatchScoreBadge score={result.score} matchLabel={result.match_label} />
          <DeadlineBadge deadline={result.deadline} />
        </div>
      </div>

      {/* Visual score bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs text-slate-500 font-semibold">
          <span>Match Compatibility</span>
          <span>{result.score}%</span>
        </div>
        <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              result.match_label === "Strong Match"
                ? "bg-emerald-600"
                : result.match_label === "Good Match"
                ? "bg-blue-600"
                : "bg-amber-500"
            }`}
            style={{ width: `${result.score}%` }}
          />
        </div>
      </div>

      {/* Why you matched */}
      <div className="space-y-2">
        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
          Why you matched
        </h4>
        <ul className="text-xs sm:text-sm text-slate-600 space-y-1">
          {matchedPoints.map((point, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="text-emerald-600 font-bold shrink-0">✓</span>
              <span>{point}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Panels */}
      <div className="grid grid-cols-1 gap-4">
        <GapAnalysisPanel items={result.gap_analysis} />
        <ActionChecklistPanel items={result.action_checklist} />
      </div>

      {/* Action Button */}
      <div className="border-t border-slate-100 pt-4 mt-1 flex justify-end">
        <a
          href={result.source_url}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`${result.name} - official source (opens in a new tab)`}
          className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 active:bg-slate-950 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
        >
          Apply / Official Source
          <ExternalLink className="h-4 w-4" />
        </a>
      </div>
    </article>
  );
}
