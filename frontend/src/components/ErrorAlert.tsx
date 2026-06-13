import { AlertCircle } from "lucide-react";

interface ErrorAlertProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorAlert({ message, onRetry }: ErrorAlertProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-2xl p-6 shadow-sm my-6 max-w-xl mx-auto">
      <div className="flex gap-3 items-start">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-red-100 text-red-700">
          <AlertCircle className="h-5 w-5" />
        </div>
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-bold text-red-800">Submission Error</h3>
            <p className="text-xs sm:text-sm text-red-700 mt-1 leading-relaxed whitespace-pre-wrap">
              {message}
            </p>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center justify-center rounded-xl bg-red-600 px-4 py-2 text-xs font-semibold text-white hover:bg-red-500 active:bg-red-700 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-red-50"
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
