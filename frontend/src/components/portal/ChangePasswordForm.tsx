import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { getErrorMessage } from "@/api/errors";
import { toast } from "@/components/ui/toast";
import { useChangePassword } from "@/hooks/useProfile";

export function ChangePasswordForm() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const changePassword = useChangePassword();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast.add({ title: "New password and confirmation do not match.", type: "error" });
      return;
    }
    try {
      await changePassword.mutateAsync({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      toast.add({ title: "Password changed.", type: "success" });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error) {
      toast.add({ title: getErrorMessage(error), type: "error" });
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-4">
      <h3 className="font-medium">Change password</h3>
      {getErrorMessage(changePassword.error, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(changePassword.error)}</AlertDescription>
        </Alert>
      )}

      <FormInput
        label="Current password"
        id="current_password"
        type="password"
        required
        value={currentPassword}
        onChange={(e) => setCurrentPassword(e.target.value)}
      />

      <FormInput
        label="New password"
        id="new_password"
        type="password"
        required
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
      />

      <FormInput
        label="Confirm new password"
        id="confirm_password"
        type="password"
        required
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
      />

      <Button type="submit" disabled={changePassword.isPending}>
        {changePassword.isPending ? "Changing..." : "Change password"}
      </Button>
    </form>
  );
}
