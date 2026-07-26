import { apiClient } from "./client";
import type { components } from "@/types/api";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

function unwrap<T>(promise: Promise<{ data: Envelope<T> }>): Promise<T> {
  return promise.then((res) => res.data.data);
}

export type Profile = components["schemas"]["User"];
export type ProfileUpdate = components["schemas"]["PatchedProfileUpdate"];

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

// Generic to every role (Admin/Landlord/Tenant) - not Tenant-specific.
// Only exposes account fields (name/phone/email/role) - the Tenant
// profile record itself (national_id, emergency contact) has no
// self-service endpoint; that stays Admin/Landlord-managed.
export function getProfile() {
  return unwrap<Profile>(apiClient.get("/auth/profile/"));
}

export function updateProfile(data: ProfileUpdate) {
  return unwrap<Profile>(apiClient.patch("/auth/profile/", data));
}

export function changePassword(data: ChangePasswordPayload) {
  return apiClient.post("/auth/change-password/", data).then(() => undefined);
}
