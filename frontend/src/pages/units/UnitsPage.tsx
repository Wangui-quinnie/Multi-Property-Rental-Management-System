import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { StatCard } from "@/components/shared/StatCard";
import { UnitTable } from "@/components/properties/UnitTable";
import { ArchiveConfirmDialog } from "@/components/shared/ArchiveConfirmDialog";
import { UnitFormDialog } from "@/components/properties/UnitFormDialog";
import { toast } from "@/components/ui/toast";
import { useProperties } from "@/hooks/useProperties";
import { useUnits, useUnitDashboard, useArchiveUnit, useRestoreUnit } from "@/hooks/useUnits";
import type { Unit } from "@/api/properties";

export function UnitsPage() {
  const [showArchived, setShowArchived] = useState(false);
  const [propertyFilter, setPropertyFilter] = useState("");
  const [editingUnit, setEditingUnit] = useState<Unit | undefined>();
  const [unitToArchive, setUnitToArchive] = useState<Unit | null>(null);
  const [restoringId, setRestoringId] = useState<string | undefined>();

  const { data: dashboard } = useUnitDashboard();
  const { data: properties } = useProperties();
  const { data: unitsPage, isLoading } = useUnits({
    property: propertyFilter || undefined,
    archived: showArchived ? "true" : undefined,
  });

  const archiveUnit = useArchiveUnit();
  const restoreUnit = useRestoreUnit();

  async function handleConfirmArchive() {
    if (!unitToArchive) return;
    await archiveUnit.mutateAsync(unitToArchive.id);
    toast.add({ title: `Unit ${unitToArchive.unit_number} archived.`, type: "success" });
    setUnitToArchive(null);
  }

  async function handleRestore(unit: Unit) {
    setRestoringId(unit.id);
    try {
      await restoreUnit.mutateAsync(unit.id);
      toast.add({ title: `Unit ${unit.unit_number} restored.`, type: "success" });
    } finally {
      setRestoringId(undefined);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Units</h1>

      {dashboard && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatCard label="Total units" value={dashboard.total_units} />
          <StatCard label="Occupied" value={dashboard.occupied_units} />
          <StatCard label="Vacant" value={dashboard.vacant_units} />
          <StatCard label="Avg. rent" value={`KES ${Number(dashboard.average_rent).toLocaleString()}`} />
        </div>
      )}

      <div className="flex flex-wrap items-center gap-2">
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
        <Select
          className="w-auto"
          value={propertyFilter}
          onChange={(e) => setPropertyFilter(e.target.value)}
        >
          <option value="">All properties</option>
          {properties?.results.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </Select>
      </div>

      <UnitTable
        units={unitsPage?.results ?? []}
        isLoading={isLoading}
        showArchived={showArchived}
        onEdit={setEditingUnit}
        onArchive={setUnitToArchive}
        onRestore={handleRestore}
        restoringId={restoringId}
      />

      {editingUnit && (
        <UnitFormDialog
          open={!!editingUnit}
          onOpenChange={(open) => !open && setEditingUnit(undefined)}
          propertyId={editingUnit.property}
          unit={editingUnit}
        />
      )}

      <ArchiveConfirmDialog
        open={!!unitToArchive}
        onOpenChange={(open) => !open && setUnitToArchive(null)}
        itemLabel={unitToArchive ? `Unit ${unitToArchive.unit_number}` : ""}
        onConfirm={handleConfirmArchive}
        isPending={archiveUnit.isPending}
      />
    </div>
  );
}