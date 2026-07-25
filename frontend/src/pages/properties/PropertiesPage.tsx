import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/shared/StatCard";
import { PropertyTable } from "@/components/properties/PropertyTable";
import { ArchiveConfirmDialog } from "@/components/shared/ArchiveConfirmDialog";
import { toast } from "@/components/ui/toast";
import { useProperties, usePropertyDashboard, useArchiveProperty, useRestoreProperty } from "@/hooks/useProperties";
import type { Property } from "@/api/properties";

export function PropertiesPage() {
  const [showArchived, setShowArchived] = useState(false);
  const [propertyToArchive, setPropertyToArchive] = useState<Property | null>(null);
  const [restoringId, setRestoringId] = useState<string | undefined>();

  const { data: dashboard } = usePropertyDashboard();
  const { data: propertiesPage, isLoading } = useProperties(
    showArchived ? { archived: "true" } : undefined
  );

  const archiveMutation = useArchiveProperty();
  const restoreMutation = useRestoreProperty();

  async function handleConfirmArchive() {
    if (!propertyToArchive) return;
    await archiveMutation.mutateAsync(propertyToArchive.id);
    toast.add({ title: `${propertyToArchive.name} archived.`, type: "success" });
    setPropertyToArchive(null);
  }

  async function handleRestore(property: Property) {
    setRestoringId(property.id);
    try {
      await restoreMutation.mutateAsync(property.id);
      toast.add({ title: `${property.name} restored.`, type: "success" });
    } finally {
      setRestoringId(undefined);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Properties</h1>
        <Button render={<Link to="/properties/new" />} nativeButton={false}>
          New property
        </Button>
      </div>

      {dashboard && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatCard label="Properties" value={dashboard.total_properties} />
          <StatCard label="Units" value={dashboard.total_units} />
          <StatCard label="Occupancy" value={`${dashboard.occupancy_rate}%`} />
          <StatCard
            label="Potential monthly rent"
            value={`KES ${Number(dashboard.potential_monthly_rent).toLocaleString()}`}
          />
        </div>
      )}

      <div className="flex items-center gap-2">
        <Button
          variant={showArchived ? "outline" : "secondary"}
          size="sm"
          onClick={() => setShowArchived(false)}
        >
          Active
        </Button>
        <Button
          variant={showArchived ? "secondary" : "outline"}
          size="sm"
          onClick={() => setShowArchived(true)}
        >
          Archived
        </Button>
      </div>

      <PropertyTable
        properties={propertiesPage?.results ?? []}
        isLoading={isLoading}
        showArchived={showArchived}
        onArchive={setPropertyToArchive}
        onRestore={handleRestore}
        restoringId={restoringId}
      />

      <ArchiveConfirmDialog
        open={!!propertyToArchive}
        onOpenChange={(open) => !open && setPropertyToArchive(null)}
        itemLabel={propertyToArchive?.name ?? ""}
        onConfirm={handleConfirmArchive}
        isPending={archiveMutation.isPending}
        cascadeNote="Its units will be archived too."
      />
    </div>
  );
}