import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/shared/StatCard";
import { getErrorMessage } from "@/api/errors";
import { toast } from "@/components/ui/toast";
import { useAuth } from "@/auth/useAuth";

import { BillingPeriodTable } from "@/components/billing/BillingPeriodTable";
import { BillingPeriodDialog } from "@/components/billing/BillingPeriodDialog";
import { ApplyLateFeesBatchDialog } from "@/components/billing/ApplyLateFeesBatchDialog";
import { useBillingPeriods } from "@/hooks/useBillingPeriods";
import type { BillingPeriod } from "@/api/billingPeriods";

import { InvoiceTable } from "@/components/billing/InvoiceTable";
import { InvoiceDetailDialog } from "@/components/billing/InvoiceDetailDialog";
import { useInvoices, useMarkOverdueInvoices } from "@/hooks/useInvoices";
import type { Invoice, InvoiceListParams } from "@/api/invoices";

import { WaterReadingTable } from "@/components/billing/WaterReadingTable";
import { WaterReadingDialog } from "@/components/billing/WaterReadingDialog";
import { useWaterReadings } from "@/hooks/useWaterReadings";
import type { WaterMeterReading } from "@/api/waterReadings";

import { ArrearsByLeaseTable } from "@/components/billing/ArrearsByLeaseTable";
import { ArrearsByTenantTable } from "@/components/billing/ArrearsByTenantTable";
import { useArrearsDashboard } from "@/hooks/useInvoices";

type BillingTab = "periods" | "invoices" | "water" | "arrears";

const TABS: { value: BillingTab; label: string }[] = [
  { value: "periods", label: "Billing Periods" },
  { value: "invoices", label: "Invoices" },
  { value: "water", label: "Water Readings" },
  { value: "arrears", label: "Arrears" },
];

const INVOICE_STATUSES = ["ALL", "UNPAID", "PARTIALLY_PAID", "OVERDUE", "PAID", "CANCELLED"] as const;

export function BillingPage() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = (searchParams.get("tab") as BillingTab) || "periods";

  function setActiveTab(tab: BillingTab) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.set("tab", tab);
      return next;
    });
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Billing</h1>

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

      {activeTab === "periods" && <BillingPeriodsTab canWrite={user?.role === "ADMIN"} />}
      {activeTab === "invoices" && <InvoicesTab />}
      {activeTab === "water" && <WaterReadingsTab />}
      {activeTab === "arrears" && <ArrearsTab />}
    </div>
  );
}

function BillingPeriodsTab({ canWrite }: { canWrite: boolean }) {
  const [statusFilter, setStatusFilter] = useState<"ALL" | "OPEN" | "CLOSED">("ALL");
  const [editingPeriod, setEditingPeriod] = useState<BillingPeriod | undefined>();
  const [creating, setCreating] = useState(false);
  const [feeBatchPeriod, setFeeBatchPeriod] = useState<BillingPeriod | undefined>();

  const params = statusFilter === "ALL" ? undefined : { status: statusFilter };
  const { data: periodsPage, isLoading } = useBillingPeriods(params);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex flex-wrap items-center gap-2">
          {(["ALL", "OPEN", "CLOSED"] as const).map((status) => (
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
        {canWrite && <Button onClick={() => setCreating(true)}>New billing period</Button>}
      </div>

      <BillingPeriodTable
        periods={periodsPage?.results ?? []}
        isLoading={isLoading}
        canWrite={canWrite}
        onEdit={setEditingPeriod}
        onApplyLateFees={setFeeBatchPeriod}
      />

      {(creating || editingPeriod) && (
        <BillingPeriodDialog
          open={creating || !!editingPeriod}
          onOpenChange={(open) => {
            if (!open) {
              setCreating(false);
              setEditingPeriod(undefined);
            }
          }}
          period={editingPeriod}
        />
      )}

      {feeBatchPeriod && (
        <ApplyLateFeesBatchDialog
          open={!!feeBatchPeriod}
          onOpenChange={(open) => !open && setFeeBatchPeriod(undefined)}
          period={feeBatchPeriod}
        />
      )}
    </div>
  );
}

function InvoicesTab() {
  const [statusFilter, setStatusFilter] = useState<(typeof INVOICE_STATUSES)[number]>("ALL");
  const [viewingInvoice, setViewingInvoice] = useState<Invoice | undefined>();

  const params: InvoiceListParams | undefined =
    statusFilter === "ALL" ? undefined : { status: statusFilter };
  const { data: invoicesPage, isLoading } = useInvoices(params);
  const markOverdueInvoices = useMarkOverdueInvoices();

  async function handleMarkOverdue() {
    try {
      const result = await markOverdueInvoices.mutateAsync();
      toast.add({
        title: `Marked ${result.invoices_marked_overdue} invoice(s) as overdue.`,
        type: "success",
      });
    } catch (error) {
      toast.add({ title: getErrorMessage(error), type: "error" });
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex flex-wrap items-center gap-2">
          {INVOICE_STATUSES.map((status) => (
            <Button
              key={status}
              variant={statusFilter === status ? "secondary" : "outline"}
              size="sm"
              onClick={() => setStatusFilter(status)}
            >
              {status === "ALL" ? "All" : status.charAt(0) + status.slice(1).toLowerCase().replace("_", " ")}
            </Button>
          ))}
        </div>
        <Button variant="outline" disabled={markOverdueInvoices.isPending} onClick={handleMarkOverdue}>
          Mark overdue invoices
        </Button>
      </div>

      <InvoiceTable
        invoices={invoicesPage?.results ?? []}
        isLoading={isLoading}
        onViewDetail={setViewingInvoice}
      />

      {viewingInvoice && (
        <InvoiceDetailDialog
          open={!!viewingInvoice}
          onOpenChange={(open) => !open && setViewingInvoice(undefined)}
          invoice={viewingInvoice}
        />
      )}
    </div>
  );
}

function WaterReadingsTab() {
  const [editingReading, setEditingReading] = useState<WaterMeterReading | undefined>();
  const [creating, setCreating] = useState(false);

  const { data: readingsPage, isLoading } = useWaterReadings();

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => setCreating(true)}>Add reading</Button>
      </div>

      <WaterReadingTable
        readings={readingsPage?.results ?? []}
        isLoading={isLoading}
        onEdit={setEditingReading}
      />

      {(creating || editingReading) && (
        <WaterReadingDialog
          open={creating || !!editingReading}
          onOpenChange={(open) => {
            if (!open) {
              setCreating(false);
              setEditingReading(undefined);
            }
          }}
          reading={editingReading}
        />
      )}
    </div>
  );
}

function ArrearsTab() {
  const { data: dashboard, isLoading } = useArrearsDashboard();

  return (
    <div className="space-y-6">
      {dashboard && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatCard label="Portfolio arrears" value={dashboard.portfolio_total_arrears} />
          <StatCard label="Leases in arrears" value={dashboard.leases_in_arrears} />
          <StatCard label="Tenants in arrears" value={dashboard.tenants_in_arrears} />
        </div>
      )}

      <div className="space-y-2">
        <h2 className="text-lg font-medium">By lease</h2>
        <ArrearsByLeaseTable entries={dashboard?.by_lease ?? []} isLoading={isLoading} />
      </div>

      <div className="space-y-2">
        <h2 className="text-lg font-medium">By tenant</h2>
        <ArrearsByTenantTable entries={dashboard?.by_tenant ?? []} isLoading={isLoading} />
      </div>
    </div>
  );
}
