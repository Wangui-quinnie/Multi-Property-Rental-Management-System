import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { FormSelect } from "@/components/shared/FormSelect";
import { getErrorMessage, parseFieldErrors } from "@/api/errors";
import type { Tenant, TenantUpdate } from "@/api/tenants";

interface TenantEditFormProps {
  tenant: Tenant;
  onSubmit: (data: TenantUpdate) => Promise<void>;
  isSubmitting: boolean;
  submitError: unknown;
}

/**
 * Deliberately small - TenantUpdateSerializer only accepts
 * national_id/emergency_contact_name/emergency_contact_phone/status.
 * Name/email/phone changes go through the tenant's own profile
 * endpoint, not Admin-driven Tenant management (see TenantUpdateSerializer's
 * docstring in apps/tenants/serializers/tenant.py).
 */
export function TenantEditForm({ tenant, onSubmit, isSubmitting, submitError }: TenantEditFormProps) {
  const [nationalId, setNationalId] = useState(tenant.national_id ?? "");
  const [emergencyContactName, setEmergencyContactName] = useState(tenant.emergency_contact_name);
  const [emergencyContactPhone, setEmergencyContactPhone] = useState(tenant.emergency_contact_phone);
  const [status, setStatus] = useState(tenant.status);

  const fieldErrors = parseFieldErrors(submitError);
  const hasFieldErrors = Object.keys(fieldErrors).length > 0;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await onSubmit({
      national_id: nationalId || null,
      emergency_contact_name: emergencyContactName,
      emergency_contact_phone: emergencyContactPhone,
      status,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {!hasFieldErrors && getErrorMessage(submitError, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(submitError)}</AlertDescription>
        </Alert>
      )}

      <FormInput
        label="National ID"
        id="national_id"
        value={nationalId}
        onChange={(e) => setNationalId(e.target.value)}
        error={fieldErrors.national_id}
      />

      <FormInput
        label="Emergency contact name"
        id="emergency_contact_name"
        value={emergencyContactName}
        onChange={(e) => setEmergencyContactName(e.target.value)}
        error={fieldErrors.emergency_contact_name}
      />

      <FormInput
        label="Emergency contact phone"
        id="emergency_contact_phone"
        value={emergencyContactPhone}
        onChange={(e) => setEmergencyContactPhone(e.target.value)}
        error={fieldErrors.emergency_contact_phone}
      />

      <FormSelect
        label="Status"
        id="status"
        value={status}
        onChange={(e) => setStatus(e.target.value as Tenant["status"])}
        error={fieldErrors.status}
      >
        <option value="ACTIVE">Active</option>
        <option value="INACTIVE">Inactive</option>
        <option value="BLACKLISTED">Blacklisted</option>
      </FormSelect>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : "Save changes"}
      </Button>
    </form>
  );
}