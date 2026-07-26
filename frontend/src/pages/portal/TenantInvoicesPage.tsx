import { useState } from "react";
import { InvoiceTable } from "@/components/billing/InvoiceTable";
import { TenantInvoiceDetailDialog } from "@/components/portal/TenantInvoiceDetailDialog";
import { useInvoices } from "@/hooks/useInvoices";
import type { Invoice } from "@/api/invoices";

// InvoiceTable is reused as-is (it's already just a display + onViewDetail
// callback, no admin-only actions baked in) - only the detail dialog needs
// a Tenant-specific read-only variant since InvoiceDetailDialog renders
// ApplyLateFeeForm.
export function TenantInvoicesPage() {
  const [viewingInvoice, setViewingInvoice] = useState<Invoice | undefined>();

  const { data: invoicesPage, isLoading } = useInvoices();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Invoices</h1>

      <InvoiceTable
        invoices={invoicesPage?.results ?? []}
        isLoading={isLoading}
        onViewDetail={setViewingInvoice}
      />

      {viewingInvoice && (
        <TenantInvoiceDetailDialog
          open={!!viewingInvoice}
          onOpenChange={(open) => !open && setViewingInvoice(undefined)}
          invoice={viewingInvoice}
        />
      )}
    </div>
  );
}
