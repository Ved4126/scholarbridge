export function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="bg-white border border-slate-200 rounded-2xl p-6 flex flex-col gap-5 animate-pulse"
        >
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-2.5 w-full sm:w-2/3">
              <div className="h-3 bg-slate-200 rounded-full w-1/4" />
              <div className="h-5 bg-slate-200 rounded-full w-3/4" />
            </div>
            <div className="h-8 bg-slate-200 rounded-full w-24 shrink-0" />
          </div>
          <div className="space-y-2">
            <div className="h-2 bg-slate-200 rounded-full w-full" />
            <div className="h-2 bg-slate-200 rounded-full w-5/6" />
          </div>
          <div className="h-10 bg-slate-100 rounded-xl w-full" />
          <div className="h-10 bg-slate-100 rounded-xl w-full" />
          <div className="flex justify-end pt-2">
            <div className="h-10 bg-slate-200 rounded-xl w-32" />
          </div>
        </div>
      ))}
    </div>
  );
}
