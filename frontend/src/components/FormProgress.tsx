import React from "react";

interface FormProgressProps {
  completed: number;
  total: number;
}

export function FormProgress({ completed, total }: FormProgressProps) {
  const percentage = Math.round((completed / total) * 100);

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h3 className="text-sm font-semibold text-slate-900">Form Progress</h3>
        <p className="text-xs text-slate-500 mt-0.5">
          {completed} of {total} sections completed
        </p>
      </div>
      <div className="flex items-center gap-3 w-full sm:w-64">
        <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-emerald-600 rounded-full transition-all duration-300"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <span className="text-sm font-semibold text-slate-700 w-10 text-right">
          {percentage}%
        </span>
      </div>
    </div>
  );
}
