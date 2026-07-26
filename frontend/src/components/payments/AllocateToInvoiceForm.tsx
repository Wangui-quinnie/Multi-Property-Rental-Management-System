import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { FormSelect } from "@/components/shared/FormSelect";
import { getErrorMessage } from "@/api/errors";
import { toast } from "@/components/ui/toast";
import { useInvoices } from "@/hooks/useInvoices";
import { useAllocateToInvoice } from "@/hooks/usePayments";

interface AllocateToInvoiceFormProps {
  paymentId: string;
  onSuccess: () => void;
}

/**
 * The invoice picker isn't scoped to this payment's tenant client-side
 * (Invoice's list filters don't include a tenant param - only status/
 * billing_period/lease, see api/invoices.ts) - it shows every invoice
 * with an outstanding balance, tenant name included in each option so
 * the right one can be picked. The backend is the real safety net:
 * PaymentAllocation.clean() rejects (400) an invoice whose lease.tenant
 * doesn't match the payment's tenant, surfaced inline below if hit.
 */
export function AllocateToInvoiceForm({ paymentId, onSuccess }: AllocateToInvoiceFormProps) {
  const { data: invoicesPage } = useInvoices({ page_size: 100 });
  const outstandingInvoices = (invoicesPage?.results ?? []).filter(
    (invoice) => Number(invoice.balance) > 0
  );

  const [invoiceId, setInvoiceId] = useState("");
  const [amount, setAmount] = useState("");

  const allocateToInvoice = useAllocateToInvoice(paymentId);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await allocateToInvoice.mutateAsync({ invoice: invoiceId, amount });
    toast.add({ title: "Payment allocated to invoice.", type: "success" });
    onSuccess();
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-4">
      <h3 className="font-medium">Allocate to invoice</h3>
      {getErrorMessage(allocateToInvoice.error, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(allocateToInvoice.error)}</AlertDescription>
        </Alert>
      )}

      <FormSelect
        label="Invoice"
        id="allocate_invoice"
        required
        value={invoiceId}
        onChange={(e) => setInvoiceId(e.target.value)}
      >
        <option value="">Select an invoice...</option>
        {outstandingInvoices.map((invoice) => (
          <option key={invoice.id} value={invoice.id}>
            {invoice.invoice_number} - {invoice.tenant_name} (balance {invoice.balance})
          </option>
        ))}
      </FormSelect>

      <FormInput
        label="Amount"
        id="allocate_amount"
        type="number"
        min="0.01"
        step="0.01"
        required
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />

      <Button type="submit" disabled={allocateToInvoice.isPending}>
        {allocateToInvoice.isPending ? "Allocating..." : "Allocate"}
      </Button>
    </form>
  );
}
