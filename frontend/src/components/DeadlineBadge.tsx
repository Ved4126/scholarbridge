import { Calendar } from "lucide-react";

interface DeadlineBadgeProps {
  deadline: string | null;
}

export function DeadlineBadge({ deadline }: DeadlineBadgeProps) {
  if (!deadline) {
    return (
      <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
        <Calendar className="h-4 w-4" />
        No deadline listed
      </div>
    );
  }

  const deadlineDate = new Date(deadline);
  const today = new Date();
  const diffTime = deadlineDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  let text = "";
  let badgeColor = "text-slate-600 bg-slate-100 border-slate-200";

  if (diffDays < 0) {
    text = "Expired";
    badgeColor = "text-red-700 bg-red-50 border-red-200";
  } else if (diffDays === 0) {
    text = "Due today";
    badgeColor = "text-red-700 bg-red-50 border-red-200";
  } else if (diffDays <= 30) {
    text = `Due in ${diffDays} day${diffDays > 1 ? "s" : ""} (${deadline})`;
    badgeColor = "text-red-700 bg-red-50 border-red-200";
  } else if (diffDays <= 60) {
    text = `Due in ${diffDays} days (${deadline})`;
    badgeColor = "text-amber-700 bg-amber-50 border-amber-200";
  } else {
    text = `Due in ${diffDays} days (${deadline})`;
    badgeColor = "text-slate-700 bg-slate-50 border-slate-200";
  }

  return (
    <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border ${badgeColor}`}>
      <Calendar className="h-3.5 w-3.5" />
      {text}
    </div>
  );
}
