import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { getErrorMessage, parseFieldErrors } from "@/api/errors";
import type { TenantCreatePayload } from "@/api/tenants";

interface TenantCreateFormProps {
  onSubmit: (data: TenantCreatePayload) => Promise<void>;
  isSubmitting: boolean;
  submitError: unknown;
}

/**
 * Creation only - editing a Tenant is a separate, much smaller form
 * (TenantEditForm) since TenantUpdateSerializer intentionally excludes
 * all User fields (email/name/phone/password). Those belong to a
 * user's own profile endpoint, not Admin-driven Tenant management, and
 * there's no "change a tenant's email" flow in this app.
 */
export function TenantCreateForm({ onSubmit, isSubmitting, submitError }: TenantCreateFormProps) {
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [nationalId, setNationalId] = useState("");
  const [emergencyContactName, setEmergencyContactName] = useState("");
  const [emergencyContactPhone, setEmergencyContactPhone] = useState("");

  const fieldErrors = parseFieldErrors(submitError);
  // See PropertyForm.tsx for why this guards the generic banner - plain
  // DRF validation errors have no top-level message, so getErrorMessage
  // falls back to (and would duplicate) the first field error.
  const hasFieldErrors = Object.keys(fieldErrors).length > 0;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await onSubmit({
      email,
      first_name: firstName,
      last_name: lastName,
      phone_number: phoneNumber,
      password,
      national_id: nationalId || undefined,
      emergency_contact_name: emergencyContactName,
      emergency_contact_phone: emergencyContactPhone,
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
        label="Email"
        id="email"
        type="email"
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        error={fieldErrors.email}
      />

      <FormInput
        label="Password"
        id="password"
        type="password"
        required
        minLength={8}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        error={fieldErrors.password}
      />

      <FormInput
        label="First name"
        id="first_name"
        value={firstName}
        onChange={(e) => setFirstName(e.target.value)}
        error={fieldErrors.first_name}
      />

      <FormInput
        label="Last name"
        id="last_name"
        value={lastName}
        onChange={(e) => setLastName(e.target.value)}
        error={fieldErrors.last_name}
      />

      <FormInput
        label="Phone number"
        id="phone_number"
        value={phoneNumber}
        onChange={(e) => setPhoneNumber(e.target.value)}
        error={fieldErrors.phone_number}
      />

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

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Create tenant"}
      </Button>
    </form>
  );
}