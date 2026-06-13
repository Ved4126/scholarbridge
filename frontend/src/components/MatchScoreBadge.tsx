import { Check, AlertCircle, HelpCircle } from "lucide-react";

interface MatchScoreBadgeProps {
  score: number;
  matchLabel: string;
}

export function MatchScoreBadge({ score, matchLabel }: MatchScoreBadgeProps) {
  let badgeClasses = "";
  let icon = null;

  if (matchLabel === "Strong Match") {
    badgeClasses = "bg-emerald-50 text-emerald-800 border-emerald-200";
    icon = <Check className="h-3.5 w-3.5" />;
  } else if (matchLabel === "Good Match") {
    badgeClasses = "bg-blue-50 text-blue-800 border-blue-200";
    icon = <Check className="h-3.5 w-3.5" />;
  } else if (matchLabel === "Possible Match") {
    badgeClasses = "bg-amber-50 text-amber-800 border-amber-200";
    icon = <AlertCircle className="h-3.5 w-3.5" />;
  } else {
    badgeClasses = "bg-slate-50 text-slate-800 border-slate-200";
    icon = <HelpCircle className="h-3.5 w-3.5" />;
  }

  return (
    <div className="flex items-center gap-3">
      <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${badgeClasses}`}>
        {icon}
        {matchLabel}
      </div>
      <span className="text-xl font-bold text-slate-900">{score}%</span>
    </div>
  );
}
