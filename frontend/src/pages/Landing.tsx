import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Building2, Users, Receipt, BarChart3 } from "lucide-react";


const features = [
  {
    icon: Building2,
    title: "Property & Unit Management",
    description: "Track properties, units, and occupancy across your entire portfolio in one place.",
  },
  {
    icon: Users,
    title: "Tenant & Lease Lifecycle",
    description: "Onboard tenants, manage leases, renewals, and terminations with a clear audit trail.",
  },
  {
    icon: Receipt,
    title: "Billing & Payments",
    description: "Automated rent invoicing, water billing, M-Pesa payments, and receipts.",
  },
  {
    icon: BarChart3,
    title: "Reporting",
    description: "Rent collection, arrears, occupancy, and cash flow insights at a glance.",
  },
];

export function Landing() {
  return (
    <div className="min-h-screen bg-white">
      <header className="flex items-center justify-between border-b px-6 py-4">
        <span className="text-lg font-semibold">Rental Management</span>
        <Button variant="outline" nativeButton={false} render={<Link to="/login" />}>
          Sign in
        </Button>
      </header>

      <section className="mx-auto max-w-3xl px-6 py-24 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Manage your rental properties, all in one place
        </h1>
        <p className="mt-6 text-lg text-slate-600">
          A complete system for landlords and property managers — properties, tenants,
          leases, billing, and payments, without the spreadsheets.
        </p>
        <div className="mt-10">
          <Button size="lg" nativeButton={false} render={<Link to="/login" />}>
            Get started
          </Button>
        </div>
      </section>
      
      <section className="mx-auto max-w-5xl px-6 pb-24">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {features.map((feature) => (
            <Card key={feature.title}>
              <CardHeader className="flex flex-row items-center gap-3">
                <feature.icon className="h-6 w-6 text-slate-700" />
                <CardTitle className="text-base">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
      
      <footer className="border-t px-6 py-6 text-center text-sm text-slate-500">
        Multi-Property Rental Management System
      </footer>
    </div>
  );
}