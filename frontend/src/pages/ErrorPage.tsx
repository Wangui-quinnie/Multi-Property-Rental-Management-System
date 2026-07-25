import { Button } from "@/components/ui/button";

interface ErrorPageProps {
  onReset?: () => void;
}

export function ErrorPage({ onReset }: ErrorPageProps) {
  function handleReload() {
    if (onReset) {
      onReset();
    }
    window.location.href = "/";
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50 px-4 text-center">
      <p className="text-sm font-medium text-slate-500">Something went wrong</p>
      <h1 className="text-3xl font-semibold tracking-tight">
        An unexpected error occurred
      </h1>
      <p className="max-w-sm text-slate-600">
        Please try reloading the page. If the problem persists, contact support.
      </p>
      <Button onClick={handleReload} className="mt-2">
        Reload
      </Button>
    </div>
  );
}
