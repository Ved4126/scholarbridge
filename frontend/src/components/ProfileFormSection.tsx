import React from "react";

interface ProfileFormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export function ProfileFormSection({ title, description, children }: ProfileFormSectionProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">{title}</h2>
        {description && (
          <p className="text-xs text-slate-500 mt-1">{description}</p>
        )}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 sm:gap-6">
        {children}
      </div>
    </div>
  );
}
