# Conversation Memory Log — Multi-Property Rental Management System

Reference document for re-establishing context in a future conversation. Paste or attach this to quickly restore working patterns and project state.

## 1. Original Problem and How It Evolved

The project is a Django REST + React/TypeScript multi-property rental management system, built incrementally phase by phase rather than all at once. Each phase follows a fixed workflow: Design → Sync API Types → API Hooks → Components → Pages → Tests → Integration Checkpoint → Commit.

The conversation picked up mid-project (already past Phase 3: Tenant/Lease/Occupancy/Vacancy) and progressed sequentially through:

- Phase 3 close-out — a tenant-visibility bug fix (Landlord couldn't see tenants when creating a lease).
- Phase 4 — Billing (billing periods, invoices, water readings, late fees, arrears).
- Phase 5 — Payments (payments, M-Pesa integration, allocation, reconciliation, receipts).
- Phase 6 — Reports & Dashboards (portfolio, vacancy, arrears, rent, water, cash flow reporting).
- Phase 7 — Tenant Portal (read-only self-service views for Tenant-role users: lease, invoices, payments, receipts, profile).

The scope never changed; each phase was additive and the user drove progress with short continuation cues ("let's go on", "i am ready", "phase 3 verified let's go on") rather than re-explaining requirements each time.

## 2. Key Insights, Recommendations, and Solutions

- **Recurring backend gap**: several ViewSets were missing `filterset_fields`, which (thanks to a globally-registered `DjangoFilterBackend`) is a zero-code way to add exact-match query filters. This exact gap was found and fixed identically across Lease/Occupancy, Invoice/WaterMeterReading/BillingPeriod, and Payment/MpesaTransaction — always flagged via a clarifying question first, always paired with a new pytest test.
- **Envelope pattern**: many custom `@action`/APIView endpoints return a `{success, message, data}` envelope that drf-spectacular's generated schema describes incorrectly. Every API file (`leases.ts`, `invoices.ts`, `payments.ts`, `reports.ts`, `profile.ts`, etc.) defines its own `Envelope<T>`/`unwrap()` helper to compensate.
- **Real bug found and fixed**: a Reports page showed "-25 days" average vacancy duration. Root cause traced through four layers (reports selector → vacancy selector → vacancy model → vacancy/occupancy services) to `close_vacancy_period()` having no chronological validation against a user-typed move-in date. Fixed with a `ValidationError` guard plus a regression test. Existing bad data in the dev DB still needs manual cleanup via Django admin (flagged, not automated).
- **Auth-protected downloads**: since a plain `<a href>` can't carry a JWT header, PDF receipt downloads fetch as a blob via axios and trigger the browser download manually through a throwaway anchor element.
- **Tenant Portal design calls**: read-only variants of Invoice/Payment detail dialogs were built fresh rather than stripping actions out of the Admin/Landlord versions, to eliminate any risk of accidentally exposing Allocate/Reconcile/Apply-Late-Fee actions to a Tenant. `ReceiptDialog` and the plain `InvoiceTable`/`PaymentTable` were reused as-is since they were already action-free display components.
- **Post-login redirect bug** (found proactively, not reported by the user): `Login.tsx` always navigated to `/dashboard`, which silently bounced Tenants back to the public landing page. Fixed by having `AuthContext.login` return the logged-in user and routing by role.

## 3. Working Style, Preferences, and Communication Patterns

- Wants responses **extremely concise and direct** — minimal explanation, no filler, no re-summarizing steps already visible.
- Confirms integration checkpoints (`npx tsc -b --force`, `npm test`, `pytest`) by **pasting real terminal output themselves** — the assistant's shell tool cannot reach their WSL path, so this is a hard constraint, not a preference.
- After each manual smoke test, gives a compact one-line confirmation (e.g. "it works", "verified") rather than a detailed report — treat that as sufficient signal to proceed.
- Comfortable with the assistant making senior-engineer default calls on clear-cut design decisions (e.g. hiding a field, choosing single-page vs tabs) without stopping to ask, but expects a **flagged, explicit callout** when such a call was made.
- When something is ambiguous or a genuine fork exists (not a default), expects to be asked directly and briefly — via structured options — rather than a paragraph of pros/cons.
- Will explicitly correct scope when the assistant over-restricts something (e.g. "sorry let it be all tenants not just active tenants") — corrections are short and final; no back-and-forth needed once given.
- Comfortable deferring lower-priority items explicitly ("just let it be as is right now we can circle back to it later") rather than having them solved immediately — the assistant should note the deferral and move on, not push back.
- Standing instruction: **share the full current content of every file edited or created**, going forward — not just a description of the change.

## 4. Effective Collaboration Approaches

- Fixed per-phase pipeline (Design → Types → Hooks → Components → Pages → Tests → Checkpoint → Commit) kept a large, multi-week-feeling project organized without needing to re-derive structure each session.
- Recurring bug classes (asterisk-suffixed required-field labels breaking `getByLabelText`, Base UI polymorphic `Button` producing `role="button"` instead of an implicit link role) were documented once and then applied as fixes immediately when they recurred, without re-investigating from scratch.
- Every new phase reused already-established TypeScript types and dashboard shapes instead of re-declaring them (e.g. Phase 6 reused `PortfolioDashboard`/`VacancyDashboard`/`ArrearsDashboard` types from earlier phases).
- Backend filterset gaps and other small clarifications were always surfaced via a structured clarifying question with a clearly marked recommended option, which the user consistently approved — this pattern can be reused directly for any future backend/frontend contract ambiguity.
- The assistant proactively looked for design-log-flagged known gaps (like the login redirect bug) rather than waiting to be told, and fixed them inline during the relevant phase.

## 5. Clarifications or Corrections That Changed Direction

- Tenant visibility: initial fix scoped Landlord's tenant list to ACTIVE-only tenants; user corrected this to "all tenants regardless of status" — final implementation and tests reflect the correction.
- Reports page layout: initial stat-grid columns were inconsistent per section (4/2/3/4); user flagged this as visually unpleasing and it was standardized to `grid-cols-2 sm:grid-cols-4` everywhere.
- `payment_reference` auto-generation: two options were proposed; user deferred the decision entirely rather than picking one — left as a required manual field, open for a future session.
- Tenant Profile scope: user chose "account fields only" over exposing Tenant-specific fields (national_id, emergency contact) — this closed off a design fork cleanly with no follow-up needed.

## 6. Specific Project Context and Examples

- Stack: React 19 + TypeScript + Vite + Tailwind v4 + shadcn/ui (Base UI, not Radix) + TanStack Query v5 + React Router v7 + Axios on the frontend; Django REST Framework on the backend.
- Roles: ADMIN, LANDLORD, TENANT — with meaningfully different permission scopes per endpoint (e.g. Tenants list is Admin-only; Billing periods are write-restricted for Landlord; everything in the Tenant Portal is read-only).
- Environment constraint: the assistant's shell sandbox cannot reach the user's native WSL path at all (confirmed repeatedly) — file Read/Write/Edit/Grep tools work fine against the Windows UNC path, but the assistant can never run `tsc`/`npm test`/`pytest` itself. The user always runs and pastes these.
- A full recursive `Glob`/`Grep` from the repo root times out (~20s ripgrep limit) — searches must be scoped to a specific app or subfolder.
- Business-workflow phase roadmap (from the project's own memory log): Phase 4 = Billing, Phase 5 = Payments, Phase 6 = Reports & Dashboards, Phase 7 = Tenant Portal, Phase 8 = Polish/Docs/Deployment.

## 7. Templates, Frameworks, and Processes Established

**Per-phase workflow (reuse for Phase 8 and beyond):**
1. Design step — confirm scope/decisions via clarifying questions where genuinely ambiguous.
2. Sync API types from the backend schema.
3. Write API client functions + TanStack Query hooks (with correct cross-namespace cache invalidation).
4. Build components (with co-located tests).
5. Build pages/routes.
6. Write/fix tests.
7. Integration checkpoint — user runs `tsc`/`npm test`/`pytest` and pastes output; assistant fixes any failures found.
8. Manual smoke test by the user, then commit with a detailed message covering everything built that phase.

**Envelope/unwrap pattern** for any endpoint where drf-spectacular's generated schema misdescribes a custom action's real `{success, message, data}` response shape.

**Read-only component pattern** for role-restricted views: build a fresh minimal variant rather than stripping actions from an existing privileged component, unless the existing component is already action-free (in which case, reuse it directly).

**Known recurring test bugs to check for immediately when a test fails:**
- Required-field labels get a trailing " *" — use `getByLabelText(/^label text/i)` instead of an exact string match.
- Base UI's polymorphic `Button` rendered via `render={<Link .../>}` produces `role="button"`, not `role="link"`.

## 8. Next Steps / Follow-Up Areas

- **Immediate**: Phase 7 (Tenant Portal) frontend code is complete — waiting on the user to run `npx tsc -b --force` and `npm test` and paste output, then do a manual smoke test, then commit. No backend changes were needed this phase.
- **Phase 8**: Polish / Docs / Deployment — not yet started.
- **Deferred decision**: whether/how to auto-generate `payment_reference` instead of requiring manual entry — explicitly parked for a later session.
- **Known manual cleanup**: at least one pre-existing bad `VacancyPeriod` record (the "-25 days" case) still needs to be found and corrected/deleted via Django admin in the user's dev database — the code fix only prevents new occurrences.
