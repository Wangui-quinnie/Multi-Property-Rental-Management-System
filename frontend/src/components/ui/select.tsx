import * as React from "react"

import { cn } from "@/lib/utils"

// NOTE: this is a plain native <select>, styled to match Input, rather
// than a Base UI Select wrapper. The project's convention for new ui/
// primitives is to pull them via `npm run add-ui <component>` (see
// scripts/add-shadcn.sh) so they match shadcn's Base UI patterns
// exactly — that wasn't available in the environment this was written
// in (no network access to the npm registry), so this is a deliberate,
// lower-risk stand-in. Swap it for the real `npm run add-ui select`
// output later if/when the richer popup-based version is needed.
function Select({ className, ...props }: React.ComponentProps<"select">) {
  return (
    <select
      data-slot="select"
      className={cn(
        "h-8 w-full min-w-0 rounded-lg border border-input bg-transparent px-2.5 py-1 text-base transition-colors outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:cursor-not-allowed disabled:bg-input/50 disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 md:text-sm dark:bg-input/30 dark:disabled:bg-input/80 dark:aria-invalid:border-destructive/50 dark:aria-invalid:ring-destructive/40",
        className
      )}
      {...props}
    />
  )
}

export { Select }