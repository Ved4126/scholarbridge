import { useState } from "react";
import { ChevronDown, ChevronUp, CheckSquare } from "lucide-react";

interface ActionChecklistPanelProps {
  items: string[];
}

export function ActionChecklistPanel({ items }: ActionChecklistPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});

  if (!items || items.length === 0) {
    return null;
  }

  const toggleCheck = (index: number) => {
    setCheckedItems((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden bg-white">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3.5 bg-slate-50 hover:bg-slate-100 transition-colors focus:outline-none"
      >
        <span className="text-xs sm:text-sm font-semibold text-slate-800 flex items-center gap-2">
          <CheckSquare className="h-4 w-4 text-emerald-600" />
          Preparation checklist ({items.length})
        </span>
        {isOpen ? (
          <ChevronUp className="h-4 w-4 text-slate-500" />
        ) : (
          <ChevronDown className="h-4 w-4 text-slate-500" />
        )}
      </button>

      {isOpen && (
        <div className="px-4 py-3 border-t border-slate-200 bg-white">
          <p className="text-xs text-slate-500 mb-3">
            These application requirements cannot be matched automatically. Use this checklist to prepare your materials.
          </p>
          <ul className="space-y-2.5">
            {items.map((item, index) => (
              <li key={index} className="flex items-start gap-2.5">
                <input
                  type="checkbox"
                  id={`checklist-item-${index}`}
                  checked={!!checkedItems[index]}
                  onChange={() => toggleCheck(index)}
                  className="mt-0.5 h-4.5 w-4.5 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 focus:outline-none"
                />
                <label
                  htmlFor={`checklist-item-${index}`}
                  className={`text-xs sm:text-sm cursor-pointer select-none transition-all duration-150 ${
                    checkedItems[index] ? "text-slate-400 line-through" : "text-slate-700"
                  }`}
                >
                  {item}
                </label>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
