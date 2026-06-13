import { useState } from "react";
import { ChevronDown, ChevronUp, AlertTriangle } from "lucide-react";
import { FeatureMatchDetail } from "@/lib/api";

interface GapAnalysisPanelProps {
  items: FeatureMatchDetail[];
}

export function GapAnalysisPanel({ items }: GapAnalysisPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!items || items.length === 0) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs font-semibold text-emerald-800 flex items-center gap-2">
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
        No missing requirements! You fully match the non-output features.
      </div>
    );
  }

  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden bg-white">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3.5 bg-slate-50 hover:bg-slate-100 transition-colors focus:outline-none"
      >
        <span className="text-xs sm:text-sm font-semibold text-slate-800 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-500" />
          Unmet eligibility criteria ({items.length})
        </span>
        {isOpen ? (
          <ChevronUp className="h-4 w-4 text-slate-500" />
        ) : (
          <ChevronDown className="h-4 w-4 text-slate-500" />
        )}
      </button>

      {isOpen && (
        <div className="px-4 py-3 border-t border-slate-200 bg-white">
          <ul className="space-y-2.5">
            {items.map((item, index) => (
              <li key={index} className="text-xs sm:text-sm text-slate-700 flex flex-col gap-1">
                <span className="font-semibold text-slate-800">{item.label}</span>
                <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-slate-600">
                  <span className="bg-slate-100 px-1.5 py-0.5 rounded">Requirement: {item.requirement}</span>
                  {item.student_value !== null && item.student_value !== undefined && (
                    <span className="bg-red-50 text-red-700 px-1.5 py-0.5 rounded">
                      Your profile: {String(item.student_value)}
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
