import { useState } from "react";
import { PaymentTable } from "@/components/payments/PaymentTable";
import { TenantPaymentDetailDialog } from "@/components/portal/TenantPaymentDetailDialog";
import { usePayments } from "@/hooks/usePayments";
import type { Payment } from "@/api/payments";

// PaymentTable is reused as-is - only the "Manage" dialog needs a
// Tenant-specific read-only variant since PaymentDetailDialog exposes
// Allocate/Remove/Reconcile actions.
export function TenantPaymentsPage() {
  const [viewingPayment, setViewingPayment] = useState<Payment | undefined>();

  const { data: paymentsPage, isLoading } = usePayments();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Payments</h1>

      <PaymentTable
        payments={paymentsPage?.results ?? []}
        isLoading={isLoading}
        onManage={setViewingPayment}
      />

      {viewingPayment && (
        <TenantPaymentDetailDialog
          open={!!viewingPayment}
          onOpenChange={(open) => !open && setViewingPayment(undefined)}
          payment={viewingPayment}
        />
      )}
    </div>
  );
}
