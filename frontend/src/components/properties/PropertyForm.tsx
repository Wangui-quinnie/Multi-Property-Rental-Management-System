import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { FormSelect } from "@/components/shared/FormSelect";
import { useAuth } from "@/auth/useAuth";
import { useLandlords } from "@/hooks/useLandlords";
import { getErrorMessage, parseFieldErrors } from "@/api/errors";
import type { Property, PropertyCreate, PropertyUpdate } from "@/api/properties";

interface PropertyFormProps {
  /** Present when editing an existing property; absent when creating. */
  property?: Property;
  onSubmit: (data: PropertyCreate | PropertyUpdate) => Promise<void>;
  isSubmitting: boolean;
  submitError: unknown;
}

export function PropertyForm({ property, onSubmit, isSubmitting, submitError }: PropertyFormProps) {
  const isEdit = !!property;
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN";

  // landlord and code are only settable at creation time (see
  // PropertyUpdateSerializer, which excludes both) — the picker is
  // Admin-only since Landlords are always auto-assigned as the owner.
  const { data: landlords } = useLandlords({ enabled: !isEdit && isAdmin });

  const [name, setName] = useState(property?.name ?? "");
  const [code, setCode] = useState(property?.code ?? "");
  const [location, setLocation] = useState(property?.location ?? "");
  const [address, setAddress] = useState(property?.address ?? "");
  const [status, setStatus] = useState(property?.status ?? "ACTIVE");
  const [landlordId, setLandlordId] = useState("");

  const fieldErrors = parseFieldErrors(submitError);
  // Only show the generic banner when there's no field to attach the
  // message to. Otherwise, for plain DRF validation errors (which have
  // no top-level `message`/`detail`), getErrorMessage falls back to the
  // first field error - showing it in the banner AND next to the field
  // would just duplicate the same text.
  const hasFieldErrors = Object.keys(fieldErrors).length > 0;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (isEdit) {
      await onSubmit({ name, location, address, status });
    } else {
      await onSubmit({
        name,
        code,
        location,
        address,
        status,
        ...(isAdmin && landlordId ? { landlord: landlordId } : {}),
      });
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {!hasFieldErrors && getErrorMessage(submitError, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(submitError)}</AlertDescription>
        </Alert>
      )}

      <FormInput
        label="Name"
        id="name"
        required
        value={name}
        onChange={(e) => setName(e.target.value)}
        error={fieldErrors.name}
      />

      {!isEdit && (
        <FormInput
          label="Code"
          id="code"
          required
          value={code}
          onChange={(e) => setCode(e.target.value)}
          error={fieldErrors.code}
        />
      )}

      <FormInput
        label="Location"
        id="location"
        required
        value={location}
        onChange={(e) => setLocation(e.target.value)}
        error={fieldErrors.location}
      />

      <FormInput
        label="Address"
        id="address"
        value={address}
        onChange={(e) => setAddress(e.target.value)}
        error={fieldErrors.address}
      />

      <FormSelect
        label="Status"
        id="status"
        value={status}
        onChange={(e) => setStatus(e.target.value as "ACTIVE" | "INACTIVE")}
        error={fieldErrors.status}
      >
        <option value="ACTIVE">Active</option>
        <option value="INACTIVE">Inactive</option>
      </FormSelect>

      {!isEdit && isAdmin && (
        <FormSelect
          label="Landlord"
          id="landlord"
          value={landlordId}
          onChange={(e) => setLandlordId(e.target.value)}
          error={fieldErrors.landlord}
        >
          <option value="">Select a landlord...</option>
          {landlords?.map((l) => (
            <option key={l.id} value={l.id}>
              {l.full_name || l.email}
            </option>
          ))}
        </FormSelect>
      )}

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : isEdit ? "Save changes" : "Create property"}
      </Button>
    </form>
  );
}