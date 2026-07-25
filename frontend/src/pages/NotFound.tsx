import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50 px-4 text-center">
      <p className="text-sm font-medium text-slate-500">404</p>
      <h1 className="text-3xl font-semibold tracking-tight">Page not found</h1>
      <p className="max-w-sm text-slate-600">
        The page you're looking for doesn't exist or may have been moved.
      </p>
      <Button render={<Link to="/" />} nativeButton={false} className="mt-2">
        Back to home
      </Button>
    </div>
  );
}
