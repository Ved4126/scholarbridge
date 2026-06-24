import { ScoringResult } from "@/lib/api";
import { MatchScoreBadge } from "./MatchScoreBadge";
import { DeadlineBadge } from "./DeadlineBadge";
import { ExternalLink, AlertTriangle, CheckSquare, ShieldCheck } from "lucide-react";
import { useState } from "react";

interface ScholarshipCardProps {
  result: ScoringResult;
}

export function ScholarshipCard({ result }: ScholarshipCardProps) {
  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});

  // 1. Deterministic explanation logic based on score
  let explanationText = "";
  if (result.score >= 80) {
    explanationText = "This scholarship is a strong fit based on your profile and eligibility signals.";
  } else if (result.score >= 60) {
    explanationText = "You match several important eligibility signals, but a few items may need review.";
  } else {
    explanationText = "This scholarship may be worth reviewing, but your profile has some gaps or missing information.";
  }

  const toggleCheck = (index: number) => {
    setCheckedItems((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  return (
    <article className="bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow duration-200 p-6 flex flex-col gap-6">
      {/* Header Info */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            {result.org_name}
          </span>
          <h3 className="text-xl sm:text-2xl font-bold text-slate-900 leading-snug">
            {result.name}
          </h3>
        </div>
        <div className="flex flex-col sm:items-end gap-2 shrink-0">
          <MatchScoreBadge score={result.score} matchLabel={result.match_label} />
          <DeadlineBadge deadline={result.deadline} />
        </div>
      </div>

      {/* Visual score bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-slate-600 font-semibold">
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

      {/* Why this matched */}
      <div className="bg-slate-50 border border-slate-200/60 rounded-xl p-4 space-y-2">
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
          <ShieldCheck className="h-4 w-4 text-emerald-600" />
          Why this matched
        </h4>
        <p className="text-sm text-slate-600 leading-relaxed">
          {explanationText} Based on your submitted profile, this scholarship passed the required eligibility filters and reached a {result.score}% compatibility score. Review the preparation checklist and official source before applying.
        </p>
      </div>

      {/* What to review (Gap Analysis) */}
      <div className="space-y-3">
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
          <AlertTriangle className="h-4 w-4 text-amber-500" />
          What to review
        </h4>
        {result.gap_analysis && result.gap_analysis.length > 0 ? (
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {result.gap_analysis.map((gap, index) => (
              <li key={index} className="bg-amber-50/50 border border-amber-200/60 rounded-xl p-3 text-xs sm:text-sm text-slate-700 space-y-1.5">
                <span className="font-bold text-slate-800 block">{gap.label}</span>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="bg-white/80 border border-amber-200 px-2 py-0.5 rounded text-[11px] text-slate-600">
                    Required: {gap.requirement}
                  </span>
                  <span className="bg-red-50 border border-red-100 text-red-700 px-2 py-0.5 rounded text-[11px]">
                    Your profile: {gap.student_value !== null && gap.student_value !== undefined ? String(gap.student_value) : "not provided"}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500 italic pl-1">
            No missing scored requirements were detected.
          </p>
        )}
      </div>

      {/* Preparation Checklist */}
      <div className="space-y-3">
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
          <CheckSquare className="h-4 w-4 text-emerald-600" />
          Preparation checklist
        </h4>
        {result.action_checklist && result.action_checklist.length > 0 ? (
          <div className="border border-slate-200 rounded-xl p-4 bg-white space-y-3">
            <p className="text-xs text-slate-500">
              These application requirements cannot be matched automatically. Use this checklist to prepare your materials:
            </p>
            <ul className="space-y-2.5">
              {result.action_checklist.map((item, index) => {
                if (!item || !item.trim()) return null;
                return (
                  <li key={index} className="flex items-start gap-2.5">
                    <input
                      type="checkbox"
                      id={`checklist-item-${result.scholarship_id}-${index}`}
                      checked={!!checkedItems[index]}
                      onChange={() => toggleCheck(index)}
                      className="mt-0.5 h-4.5 w-4.5 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 focus:outline-none"
                    />
                    <label
                      htmlFor={`checklist-item-${result.scholarship_id}-${index}`}
                      className={`text-xs sm:text-sm cursor-pointer select-none transition-all duration-150 ${
                        checkedItems[index] ? "text-slate-400 line-through" : "text-slate-700"
                      }`}
                    >
                      {item}
                    </label>
                  </li>
                );
              })}
            </ul>
          </div>
        ) : (
          <p className="text-sm text-slate-500 italic pl-1">
            No additional preparation items were detected from the scholarship record.
          </p>
        )}
      </div>

      {/* Action Button & Trust Note */}
      <div className="border-t border-slate-100 pt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <span className="text-[11px] text-slate-400 italic">
          * Always verify final eligibility on the official source.
        </span>
        {result.source_url ? (
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
        ) : (
          <button
            disabled
            className="inline-flex items-center gap-2 rounded-xl bg-slate-200 px-5 py-3 text-sm font-semibold text-slate-400 cursor-not-allowed"
          >
            Source Link Unavailable
          </button>
        )}
      </div>
    </article>
  );
}
