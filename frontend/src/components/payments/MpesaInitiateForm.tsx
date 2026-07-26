import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { FormSelect } from "@/components/shared/FormSelect";
import { getErrorMessage } from "@/api/errors";
import { toast } from "@/components/ui/toast";
import { useTenants } from "@/hooks/useTenants";
import { useInitiateStkPush } from "@/hooks/useMpesa";

interface MpesaInitiateFormProps {
  onSuccess: () => void;
}

/**
 * STK Push is mocked server-side (call_safaricom_stk_push is stubbed,
 * see apps/payments/services/mpesa.py) - this always creates a PENDING
 * transaction immediately; the SUCCESS/FAILED transition only happens
 * once the (separate, unauthenticated) callback endpoint is hit, which
 * in this environment never arrives on its own. The transaction stays
 * PENDING until that's simulated - this is a known limitation of the
 * mocked integration, not a frontend bug.
 */
export function MpesaInitiateForm({ onSuccess }: MpesaInitiateFormProps) {
  const { data: tenantsPage } = useTenants({ page_size: 100 });

  const [tenantId, setTenantId] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [amount, setAmount] = useState("");

  const initiateStkPush = useInitiateStkPush();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await initiateStkPush.mutateAsync({ tenant: tenantId, phone_number: phoneNumber, amount });
    toast.add({ title: "STK Push initiated. Awaiting customer confirmation.", type: "success" });
    onSuccess();
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {getErrorMessage(initiateStkPush.error, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(initiateStkPush.error)}</AlertDescription>
        </Alert>
      )}

      <FormSelect
        label="Tenant"
        id="mpesa_tenant"
        required
        value={tenantId}
        onChange={(e) => setTenantId(e.target.value)}
      >
        <option value="">Select a tenant...</option>
        {tenantsPage?.results.map((t) => (
          <option key={t.id} value={t.id}>
            {t.full_name || t.email}
          </option>
        ))}
      </FormSelect>

      <FormInput
        label="Phone number"
        id="mpesa_phone_number"
        required
        placeholder="2547XXXXXXXX"
        value={phoneNumber}
        onChange={(e) => setPhoneNumber(e.target.value)}
      />

      <FormInput
        label="Amount"
        id="mpesa_amount"
        type="number"
        min="1"
        step="0.01"
        required
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />

      <Button type="submit" disabled={initiateStkPush.isPending}>
        {initiateStkPush.isPending ? "Sending..." : "Send STK Push"}
      </Button>
    </form>
  );
}
