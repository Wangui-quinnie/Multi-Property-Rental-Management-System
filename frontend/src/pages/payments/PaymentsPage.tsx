import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/shared/StatCard";

import { PaymentTable } from "@/components/payments/PaymentTable";
import { PaymentDialog } from "@/components/payments/PaymentDialog";
import { PaymentDetailDialog } from "@/components/payments/PaymentDetailDialog";
import { usePayments } from "@/hooks/usePayments";
import type { Payment, PaymentListParams } from "@/api/payments";

import { MpesaTransactionTable } from "@/components/payments/MpesaTransactionTable";
import { MpesaInitiateDialog } from "@/components/payments/MpesaInitiateDialog";
import { useMpesaTransactions } from "@/hooks/useMpesa";

import { UnallocatedPaymentsTable } from "@/components/payments/UnallocatedPaymentsTable";
import { StalePendingMpesaTable } from "@/components/payments/StalePendingMpesaTable";
import { IntegrityMismatchesTable } from "@/components/payments/IntegrityMismatchesTable";
import { useReconciliationDashboard } from "@/hooks/useReconciliation";

type PaymentsTab = "payments" | "mpesa" | "reconciliation";

const TABS: { value: PaymentsTab; label: string }[] = [
  { value: "payments", label: "Payments" },
  { value: "mpesa", label: "M-Pesa" },
  { value: "reconciliation", label: "Reconciliation" },
];

const PAYMENT_STATUSES = ["ALL", "PENDING", "CONFIRMED", "FAILED", "REVERSED"] as const;

export function PaymentsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = (searchParams.get("tab") as PaymentsTab) || "payments";

  function setActiveTab(tab: PaymentsTab) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.set("tab", tab);
      return next;
    });
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Payments</h1>

      <div className="flex flex-wrap items-center gap-2">
        {TABS.map((tab) => (
          <Button
            key={tab.value}
            variant={activeTab === tab.value ? "secondary" : "outline"}
            size="sm"
            onClick={() => setActiveTab(tab.value)}
          >
            {tab.label}
          </Button>
        ))}
      </div>

      {activeTab === "payments" && <PaymentsTab />}
      {activeTab === "mpesa" && <MpesaTab />}
      {activeTab === "reconciliation" && <ReconciliationTab />}
    </div>
  );
}

function PaymentsTab() {
  const [statusFilter, setStatusFilter] = useState<(typeof PAYMENT_STATUSES)[number]>("ALL");
  const [managingPayment, setManagingPayment] = useState<Payment | undefined>();
  const [creating, setCreating] = useState(false);

  const params: PaymentListParams | undefined =
    statusFilter === "ALL" ? undefined : { status: statusFilter };
  const { data: paymentsPage, isLoading } = usePayments(params);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex flex-wrap items-center gap-2">
          {PAYMENT_STATUSES.map((status) => (
            <Button
              key={status}
              variant={statusFilter === status ? "secondary" : "outline"}
              size="sm"
              onClick={() => setStatusFilter(status)}
            >
              {status === "ALL" ? "All" : status.charAt(0) + status.slice(1).toLowerCase()}
            </Button>
          ))}
        </div>
        <Button onClick={() => setCreating(true)}>Record payment</Button>
      </div>

      <PaymentTable
        payments={paymentsPage?.results ?? []}
        isLoading={isLoading}
        onManage={setManagingPayment}
      />

      {creating && <PaymentDialog open={creating} onOpenChange={setCreating} />}

      {managingPayment && (
        <PaymentDetailDialog
          open={!!managingPayment}
          onOpenChange={(open) => !open && setManagingPayment(undefined)}
          payment={managingPayment}
        />
      )}
    </div>
  );
}

function MpesaTab() {
  const [initiating, setInitiating] = useState(false);
  const { data: transactionsPage, isLoading } = useMpesaTransactions();

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => setInitiating(true)}>Initiate STK Push</Button>
      </div>

      <MpesaTransactionTable transactions={transactionsPage?.results ?? []} isLoading={isLoading} />

      {initiating && <MpesaInitiateDialog open={initiating} onOpenChange={setInitiating} />}
    </div>
  );
}

function ReconciliationTab() {
  const { data: dashboard, isLoading } = useReconciliationDashboard();

  return (
    <div className="space-y-6">
      {dashboard && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatCard label="Unallocated payments" value={dashboard.unallocated_payments.length} />
          <StatCard label="Stale pending M-Pesa" value={dashboard.stale_pending_mpesa.length} />
          <StatCard label="Integrity mismatches" value={dashboard.integrity_mismatches.length} />
        </div>
      )}

      <div className="space-y-2">
        <h2 className="text-lg font-medium">Unallocated payments</h2>
        <UnallocatedPaymentsTable entries={dashboard?.unallocated_payments ?? []} isLoading={isLoading} />
      </div>

      <div className="space-y-2">
        <h2 className="text-lg font-medium">Stale pending M-Pesa</h2>
        <StalePendingMpesaTable entries={dashboard?.stale_pending_mpesa ?? []} isLoading={isLoading} />
      </div>

      <div className="space-y-2">
        <h2 className="text-lg font-medium">Integrity mismatches</h2>
        <IntegrityMismatchesTable entries={dashboard?.integrity_mismatches ?? []} isLoading={isLoading} />
      </div>
    </div>
  );
}
