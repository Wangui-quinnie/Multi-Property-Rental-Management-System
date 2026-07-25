import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface ArchiveConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  itemLabel: string;
  onConfirm: () => void;
  isPending?: boolean;
  /** Extra detail for cases with cascading effects (e.g. archiving a
   * Property also archives its Units). */
  cascadeNote?: string;
}

/**
 * Confirmation for the "archive" action (labelled honestly as Archive,
 * not Delete — DELETE on these endpoints soft-deletes/archives, it
 * never destroys the row).
 */
export function ArchiveConfirmDialog({
  open,
  onOpenChange,
  itemLabel,
  onConfirm,
  isPending,
  cascadeNote,
}: ArchiveConfirmDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Archive {itemLabel}?</AlertDialogTitle>
          <AlertDialogDescription>
            This hides it from the active list, but it isn&apos;t deleted — you can
            restore it later.
            {cascadeNote && <> {cascadeNote}</>}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm} disabled={isPending}>
            {isPending ? "Archiving..." : "Archive"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}