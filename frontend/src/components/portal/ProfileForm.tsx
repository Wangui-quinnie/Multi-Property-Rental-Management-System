import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { FormField } from "@/components/shared/FormField";
import { Input } from "@/components/ui/input";
import { getErrorMessage } from "@/api/errors";
import { toast } from "@/components/ui/toast";
import { useUpdateProfile } from "@/hooks/useProfile";
import type { Profile } from "@/api/profile";

interface ProfileFormProps {
  profile: Profile;
}

// Account fields only (first_name/last_name/phone_number) - matches the
// generic /auth/profile/ PATCH payload. Email and role are shown read-only;
// there is no self-service endpoint for Tenant-specific fields
// (national_id, emergency contact) so those stay out of this form.
export function ProfileForm({ profile }: ProfileFormProps) {
  const [firstName, setFirstName] = useState(profile.first_name ?? "");
  const [lastName, setLastName] = useState(profile.last_name ?? "");
  const [phoneNumber, setPhoneNumber] = useState(profile.phone_number ?? "");

  const updateProfile = useUpdateProfile();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      await updateProfile.mutateAsync({
        first_name: firstName,
        last_name: lastName,
        phone_number: phoneNumber,
      });
      toast.add({ title: "Profile updated.", type: "success" });
    } catch (error) {
      toast.add({ title: getErrorMessage(error), type: "error" });
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-4">
      {getErrorMessage(updateProfile.error, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(updateProfile.error)}</AlertDescription>
        </Alert>
      )}

      <FormField label="Email" htmlFor="profile_email">
        <Input id="profile_email" value={profile.email} disabled readOnly />
      </FormField>

      <FormInput
        label="First name"
        id="profile_first_name"
        required
        value={firstName}
        onChange={(e) => setFirstName(e.target.value)}
      />

      <FormInput
        label="Last name"
        id="profile_last_name"
        required
        value={lastName}
        onChange={(e) => setLastName(e.target.value)}
      />

      <FormInput
        label="Phone number"
        id="profile_phone_number"
        value={phoneNumber}
        onChange={(e) => setPhoneNumber(e.target.value)}
      />

      <Button type="submit" disabled={updateProfile.isPending}>
        {updateProfile.isPending ? "Saving..." : "Save changes"}
      </Button>
    </form>
  );
}
