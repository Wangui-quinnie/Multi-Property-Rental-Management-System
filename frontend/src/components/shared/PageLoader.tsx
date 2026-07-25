import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface PageLoaderProps {
  /** Renders as a full-viewport loader instead of filling its parent container. */
  fullScreen?: boolean;
  label?: string;
  className?: string;
}

export function PageLoader({ fullScreen, label, className }: PageLoaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-2 py-16 text-muted-foreground",
        fullScreen && "min-h-screen",
        className
      )}
    >
      <Loader2 className="size-6 animate-spin" />
      {label && <p className="text-sm">{label}</p>}
    </div>
  );
}
