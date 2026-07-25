import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PropertyForm } from "@/components/properties/PropertyForm";
import { useCreateProperty } from "@/hooks/useProperties";
import { toast } from "@/components/ui/toast";
import type { PropertyCreate, PropertyUpdate } from "@/api/properties";

export function PropertyCreatePage() {
  const navigate = useNavigate();
  const createProperty = useCreateProperty();

  // PropertyForm is shared between create/edit, so its onSubmit prop
  // accepts either shape — this page only ever renders in create mode
  // (no `property` passed to PropertyForm below), so it's always
  // actually a PropertyCreate at runtime.
  async function handleSubmit(data: PropertyCreate | PropertyUpdate) {
    await createProperty.mutateAsync(data as PropertyCreate);
    // The create response has no `id` (see api/properties.ts), so we
    // can't navigate straight to a detail page — back to the list,
    // which will show the new property once its query refetches.
    toast.add({ title: "Property created.", type: "success" });
    navigate("/properties");
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">New property</h1>
      <Card>
        <CardHeader>
          <CardTitle>Details</CardTitle>
        </CardHeader>
        <CardContent>
          <PropertyForm
            onSubmit={handleSubmit}
            isSubmitting={createProperty.isPending}
            submitError={createProperty.error}
          />
        </CardContent>
      </Card>
    </div>
  );
}