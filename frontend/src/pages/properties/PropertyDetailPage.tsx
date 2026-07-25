import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { PageLoader } from "@/components/shared/PageLoader";
import { ArchiveConfirmDialog } from "@/components/shared/ArchiveConfirmDialog";
import { UnitTable } from "@/components/properties/UnitTable";
import { UnitFormDialog } from "@/components/properties/UnitFormDialog";
import { toast } from "@/components/ui/toast";
import { useProperty, useArchiveProperty } from "@/hooks/useProperties";
import { useUnits, useArchiveUnit, useRestoreUnit } from "@/hooks/useUnits";
import type { Unit } from "@/api/properties";

export function PropertyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [showArchivedUnits, setShowArchivedUnits] = useState(false);
  const [unitDialogOpen, setUnitDialogOpen] = useState(false);
  const [editingUnit, setEditingUnit] = useState<Unit | undefined>();
  const [unitToArchive, setUnitToArchive] = useState<Unit | null>(null);
  const [propertyArchiveOpen, setPropertyArchiveOpen] = useState(false);
  const [restoringUnitId, setRestoringUnitId] = useState<string | undefined>();

  const { data: property, isLoading } = useProperty(id);
  const { data: unitsPage, isLoading: unitsLoading } = useUnits({
    property: id,
    archived: showArchivedUnits ? "true" : undefined,
  });

  const archiveProperty = useArchiveProperty();
  const archiveUnit = useArchiveUnit();
  const restoreUnit = useRestoreUnit();

  function openAddUnit() {
    setEditingUnit(undefined);
    setUnitDialogOpen(true);
  }

  function openEditUnit(unit: Unit) {
    setEditingUnit(unit);
    setUnitDialogOpen(true);
  }

  async function handleConfirmArchiveUnit() {
    if (!unitToArchive) return;
    await archiveUnit.mutateAsync(unitToArchive.id);
    toast.add({ title: `Unit ${unitToArchive.unit_number} archived.`, type: "success" });
    setUnitToArchive(null);
  }

  async function handleRestoreUnit(unit: Unit) {
    setRestoringUnitId(unit.id);
    try {
      await restoreUnit.mutateAsync(unit.id);
      toast.add({ title: `Unit ${unit.unit_number} restored.`, type: "success" });
    } finally {
      setRestoringUnitId(undefined);
    }
  }

  async function handleConfirmArchiveProperty() {
    if (!id) return;
    await archiveProperty.mutateAsync(id);
    toast.add({ title: "Property archived.", type: "success" });
    navigate("/properties");
  }

  if (isLoading) return <PageLoader />;
  if (!property || !id) return <p className="text-muted-foreground">Property not found.</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{property.name}</h1>
          <p className="text-sm text-muted-foreground">
            {property.code} · {property.location}
          </p>
        </div>
        <div className="flex gap-2">
          <Button render={<Link to={`/properties/${id}/edit`} />} nativeButton={false} variant="outline">
            Edit
          </Button>
          <Button variant="outline" onClick={() => setPropertyArchiveOpen(true)}>
            Archive
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <div>
            <p className="text-xs text-muted-foreground">Landlord</p>
            <p className="text-sm font-medium">{property.landlord_name}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Units</p>
            <p className="text-sm font-medium">
              {property.occupied_units}/{property.total_units} occupied
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Occupancy</p>
            <p className="text-sm font-medium">{property.occupancy_rate}%</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Potential monthly rent</p>
            <p className="text-sm font-medium">
              KES {Number(property.potential_monthly_rent).toLocaleString()}
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Units</h2>
        <div className="flex items-center gap-2">
          <Button
            variant={showArchivedUnits ? "outline" : "secondary"}
            size="sm"
            onClick={() => setShowArchivedUnits(false)}
          >
            Active
          </Button>
          <Button
            variant={showArchivedUnits ? "secondary" : "outline"}
            size="sm"
            onClick={() => setShowArchivedUnits(true)}
          >
            Archived
          </Button>
          <Button size="sm" onClick={openAddUnit}>
            Add unit
          </Button>
        </div>
      </div>

      <UnitTable
        units={unitsPage?.results ?? []}
        isLoading={unitsLoading}
        showArchived={showArchivedUnits}
        showPropertyColumn={false}
        onEdit={openEditUnit}
        onArchive={setUnitToArchive}
        onRestore={handleRestoreUnit}
        restoringId={restoringUnitId}
      />

      <UnitFormDialog
        open={unitDialogOpen}
        onOpenChange={setUnitDialogOpen}
        propertyId={id}
        unit={editingUnit}
      />

      <ArchiveConfirmDialog
        open={!!unitToArchive}
        onOpenChange={(open) => !open && setUnitToArchive(null)}
        itemLabel={unitToArchive ? `Unit ${unitToArchive.unit_number}` : ""}
        onConfirm={handleConfirmArchiveUnit}
        isPending={archiveUnit.isPending}
      />

      <ArchiveConfirmDialog
        open={propertyArchiveOpen}
        onOpenChange={setPropertyArchiveOpen}
        itemLabel={property.name}
        onConfirm={handleConfirmArchiveProperty}
        isPending={archiveProperty.isPending}
        cascadeNote="Its units will be archived too."
      />
    </div>
  );
}