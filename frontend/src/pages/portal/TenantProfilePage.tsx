import { PageLoader } from "@/components/shared/PageLoader";
import { ProfileForm } from "@/components/portal/ProfileForm";
import { ChangePasswordForm } from "@/components/portal/ChangePasswordForm";
import { useProfile } from "@/hooks/useProfile";

export function TenantProfilePage() {
  const { data: profile, isLoading } = useProfile();

  if (isLoading) return <PageLoader />;
  if (!profile) return null;

  return (
    <div className="max-w-lg space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Profile</h1>
      <ProfileForm profile={profile} />
      <ChangePasswordForm />
    </div>
  );
}
