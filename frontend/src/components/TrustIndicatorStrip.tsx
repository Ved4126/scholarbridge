import { CheckCircle2, ShieldAlert, Award, FileSpreadsheet } from "lucide-react";

export function TrustIndicatorStrip() {
  const indicators = [
    {
      icon: <Award className="h-5 w-5 text-emerald-600" />,
      title: "Profile-based matching",
      desc: "Matches evaluated directly against your specific academic achievements and circumstances.",
    },
    {
      icon: <CheckCircle2 className="h-5 w-5 text-emerald-600" />,
      title: "Transparent eligibility scores",
      desc: "See exact match percentages and a detailed analysis of any requirements you missed.",
    },
    {
      icon: <FileSpreadsheet className="h-5 w-5 text-emerald-600" />,
      title: "Official source links",
      desc: "Every scholarship links directly to the official external application site.",
    },
    {
      icon: <ShieldAlert className="h-5 w-5 text-emerald-600" />,
      title: "No applications taken here",
      desc: "We never take applications or charge fees. ScholarBridge is purely a discovery tool.",
    },
  ];

  return (
    <section className="bg-white border-y border-slate-200 py-12">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {indicators.map((item, index) => (
            <div key={index} className="flex gap-4 items-start">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-50">
                {item.icon}
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 text-sm mb-1">{item.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
