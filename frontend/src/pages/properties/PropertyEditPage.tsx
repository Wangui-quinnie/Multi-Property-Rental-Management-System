import { useNavigate, useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageLoader } from "@/components/shared/PageLoader";
import { PropertyForm } from "@/components/properties/PropertyForm";
import { useProperty, useUpdateProperty } from "@/hooks/useProperties";
import { toast } from "@/components/ui/toast";
import type { PropertyCreate, PropertyUpdate } from "@/api/properties";

export function PropertyEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: property, isLoading } = useProperty(id);
  const updateProperty = useUpdateProperty(id ?? "");

  async function handleSubmit(data: PropertyCreate | PropertyUpdate) {
    await updateProperty.mutateAsync(data as PropertyUpdate);
    toast.add({ title: "Property updated.", type: "success" });
    navigate(`/properties/${id}`);
  }

  if (isLoading) return <PageLoader />;
  if (!property) return <p className="text-muted-foreground">Property not found.</p>;

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Edit {property.name}</h1>
      <Card>
        <CardHeader>
          <CardTitle>Details</CardTitle>
        </CardHeader>
        <CardContent>
          <PropertyForm
            property={property}
            onSubmit={handleSubmit}
            isSubmitting={updateProperty.isPending}
            submitError={updateProperty.error}
          />
        </CardContent>
      </Card>
    </div>
  );
}
