# PRD — InvoiceKit MVP

**Status:** ready-for-agent
**Date:** 2026-06-11

---

## Problem Statement

Freelancers and small businesses need a simple, affordable way to create, send, and collect payment on invoices. Existing solutions like Conta Azul or Nibo are expensive, bloated with features most solo operators never use, and often require complex onboarding. Freelancers end up juggling spreadsheets, manual PDF generation, and disconnected payment links — wasting time on administrative overhead instead of billable work.

## Solution

InvoiceKit is a multi-tenant API-only SaaS that lets each user manage their clients and invoices with minimal friction. Users can create invoices, auto-generate sequential invoice numbers, generate professional PDFs on demand, share Stripe payment links with clients, and have payment status updated automatically via webhooks. The product is a REST API (no frontend in MVP) that freelancers can integrate into their own workflows, CLIs, or scripts.

## User Stories

### Client Management

1. As a freelancer, I want to register an account with email and password, so that I have a secure isolated workspace.
2. As a freelancer, I want to log in and receive a JWT access token, so that I can authenticate API requests.
3. As a freelancer, I want to create a client record with name, email, phone, address, and optional tax ID, so that I can associate invoices with specific recipients.
4. As a freelancer, I want to list all my clients with pagination, so that I can browse my client base efficiently.
5. As a freelancer, I want to filter clients by name or email, so that I can find specific clients quickly.
6. As a freelancer, I want to view a single client's full details, so that I can verify or update information.
7. As a freelancer, I want to update a client's information, so that I can keep records current.
8. As a freelancer, I want to soft-delete a client, so that I can remove inactive clients without losing historical invoice data.
9. As a freelancer, I want to see how many active clients I have relative to my plan limit, so that I know when I need to upgrade.
10. As a freelancer on the free plan, I want to receive a clear error if I try to create a client beyond the 5-client limit, so that I understand why the action failed and what to do about it.

### Invoice Lifecycle

11. As a freelancer, I want to create a draft invoice referencing a client, so that I can start building a bill.
12. As a freelancer, I want to add one or more line items (description, quantity, unit price) to an invoice, so that I can detail the services rendered.
13. As a freelancer, I want the invoice total to be calculated automatically from line items, so that I don't make arithmetic errors.
14. As a freelancer, I want my invoices to be numbered sequentially per tenant (e.g., INV-0001, INV-0002), so that I have professional, traceable invoice identifiers.
15. As a freelancer, I want to set a due date on an invoice, so that clients know when payment is expected.
16. As a freelancer, I want to mark a draft invoice as "sent", so that the system knows the invoice has been delivered to the client.
17. As a freelancer, I want a Celery task to automatically email the invoice PDF to the client when I mark it as sent, so that delivery is immediate and hands-off.
18. As a freelancer, I want to generate a PDF of any invoice on demand via an API endpoint, so that I can download or share it at any time.
19. As a freelancer, I want the PDF to render in A4 format with my business details, client details, line items, totals, and payment instructions, so that it looks professional.
20. As a freelancer, I want the PDF to be generated dynamically (not stored on disk), so that I always get the latest version and don't pay for storage.
21. As a freelancer, I want to create a Stripe Payment Link for a specific invoice, so that I can share it with the client for easy online payment.
22. As a freelancer, I want the payment link to be stored with the invoice record, so that I can retrieve or resend it later.
23. As a freelancer, I want the system to automatically mark an invoice as "overdue" when its due date passes without payment, so that I have visibility into unpaid work.
24. As a freelancer, I want to mark an invoice as paid manually, so that I can record offline payments (cash, bank transfer, etc.).
25. As a freelancer, I want the system to automatically mark an invoice as "paid" and record the `paid_at` timestamp when a Stripe webhook confirms checkout completion, so that I don't have to manually reconcile payments.
26. As a freelancer, I want to list all my invoices with pagination and optional status filter, so that I can manage my receivables.
27. As a freelancer, I want to view a single invoice with all its line items, so that I can review details before sending.
28. As a freelancer, I want to update a draft invoice (client, due date, line items), so that I can correct or adjust before sending.
29. As a freelancer, I want to soft-delete a draft invoice, so that I can remove invoices I no longer need.
30. As a freelancer, I want to receive a clear error if I try to create an invoice beyond my plan's monthly limit, so that I understand the constraint.

### Plan and Limits

31. As a freelancer on the free plan, I want to create up to 5 clients and 10 invoices per month, so that I can use the product at no cost for light usage.
32. As a freelancer on the pro plan, I want unlimited clients and invoices, so that I am not constrained as my business grows.
33. As a freelancer, I want to upgrade to the pro plan via Stripe Billing, so that I can unlock unlimited usage.
34. As a freelancer, I want the system to enforce limits at the service layer (not just the database), so that error messages are clear and actionable.

### Security and Multi-Tenancy

35. As a freelancer, I want every data-accessing endpoint to verify that the resource belongs to my tenant, so that no other user can access my data.
36. As a freelancer, I want JWT tokens to expire and be refreshable, so that my session is secure.
37. As a freelancer, I want the Stripe webhook endpoint to validate the request signature before processing any event, so that spoofed events cannot manipulate my invoice status.

### Observability and Reliability

38. As a freelancer, I want Celery tasks (email sending, overdue checking) to be idempotent, so that retries don't cause duplicate emails or status transitions.
39. As a freelancer, I want the system to handle PDF generation under concurrent load without exhausting memory, so that multiple users can generate PDFs simultaneously.
40. As a freelancer, I want the overdue-check cron job to run every 15 minutes, so that invoices are transitioned to overdue in a timely manner.

## Implementation Decisions

### Architecture

- **Layered architecture** following Repository Pattern: Controllers (FastAPI routers) → Services → Repositories → Database (SQLAlchemy async).
- Controllers validate input via Pydantic schemas and delegate to services. No business logic in controllers. No SQL outside repositories.
- Dependency injection via `Depends()` for DB session and `current_user`.

### Modules

- **Users/Auth**: Registration, login, JWT issuance and refresh, current user extraction.
- **Clients**: CRUD with tenant isolation and plan limit enforcement.
- **Invoices**: CRUD, status state machine, sequential numbering per tenant, plan limit enforcement.
- **InvoiceItems**: Inline with invoice creation/update (nested in invoice endpoints).
- **PDF Generation**: On-demand WeasyPrint + Jinja2 template rendering, returning `StreamingResponse`.
- **Payments**: Stripe Payment Link creation per invoice, webhook handler for `checkout.session.completed`.
- **Email**: Celery task triggered on invoice sent status, attaches PDF.
- **Scheduled Tasks**: Celery Beat job every 15 minutes to check overdue invoices.
- **Plans**: Free/Pro plan definitions, limit checking logic.

### Database Schema

All tables include `id` (UUID PK), `tenant_id` (FK to users), `created_at`, `updated_at`, `deleted_at` (nullable, for soft delete).

- **users**: `id`, `email` (unique), `password_hash`, `plan` (enum: free, pro), `business_name`, `business_address`, `business_tax_id`, `created_at`, `updated_at`, `deleted_at`.
- **clients**: `id`, `tenant_id`, `name`, `email`, `phone`, `address`, `tax_id`, `created_at`, `updated_at`, `deleted_at`.
- **invoices**: `id`, `tenant_id`, `client_id` (FK), `invoice_number` (e.g. INV-0001), `status` (enum: draft, sent, paid, overdue), `due_date`, `paid_at`, `stripe_payment_link`, `created_at`, `updated_at`, `deleted_at`.
- **invoice_items**: `id`, `invoice_id` (FK, cascade delete), `description`, `quantity` (numeric), `unit_price` (numeric), `created_at`, `updated_at`, `deleted_at`.

Constraints:
- `invoice_number` unique per tenant (composite unique on tenant_id + invoice_number).
- `invoice_items.invoice_id` ON DELETE CASCADE.
- Index on `invoices(tenant_id, status)` for filtered queries.
- Index on `invoices(tenant_id, due_date)` for overdue checking.

### Invoice Status State Machine

```
draft → sent → paid
                → overdue
```

Transitions:
- `draft → sent`: When user explicitly marks as sent. Triggers email Celery task.
- `sent → paid`: When Stripe webhook confirms payment (`checkout.session.completed`) or when user manually marks as paid.
- `sent → overdue`: When Celery Beat job detects `due_date < now()` and status is still `sent`.

Invalid transitions return HTTP 400 with a descriptive message.

### Sequential Invoice Numbering

- Invoice numbers are formatted as `INV-{NNNN}` where `NNNN` is zero-padded to 4 digits, starting from `0001` per tenant.
- The next number is determined by querying the max invoice number for the tenant and incrementing. This is done within a database transaction to prevent race conditions.

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login, returns access + refresh tokens |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/users/me` | Get current user profile |
| PUT | `/users/me` | Update current user profile |
| GET | `/clients` | List clients (paginated, filterable) |
| POST | `/clients` | Create client (limit check) |
| GET | `/clients/{id}` | Get client by ID |
| PUT | `/clients/{id}` | Update client |
| DELETE | `/clients/{id}` | Soft-delete client |
| GET | `/invoices` | List invoices (paginated, filterable by status) |
| POST | `/invoices` | Create invoice with items (limit check) |
| GET | `/invoices/{id}` | Get invoice with items |
| PUT | `/invoices/{id}` | Update invoice (draft only) |
| DELETE | `/invoices/{id}` | Soft-delete invoice (draft only) |
| POST | `/invoices/{id}/send` | Mark as sent, triggers email |
| POST | `/invoices/{id}/pay` | Manually mark as paid |
| GET | `/invoices/{id}/pdf` | Generate and stream PDF |
| POST | `/invoices/{id}/payment-link` | Create Stripe payment link |
| POST | `/webhooks/stripe` | Stripe webhook handler |
| GET | `/plans/usage` | Get current usage vs limits |

### Request/Response Contracts (key endpoints)

**POST /invoices**
```json
{
  "client_id": "uuid",
  "due_date": "2026-07-01",
  "items": [
    { "description": "Web development", "quantity": 1, "unit_price": 500.00 }
  ]
}
```
Response: 201 with invoice object including calculated `total`, `invoice_number`, `status: "draft"`.

**POST /invoices/{id}/send**
Response: 200 with updated invoice. Celery task dispatched asynchronously to email PDF.

**GET /invoices/{id}/pdf**
Response: 200 with `Content-Type: application/pdf`, `StreamingResponse`.

**POST /webhooks/stripe**
Validates signature, processes `checkout.session.completed`, updates invoice status to `paid`, sets `paid_at`.

### PDF Generation

- WeasyPrint renders HTML/CSS template to PDF in memory (BytesIO).
- Template includes: business name/address/tax_id from user, client details, invoice number, due date, line item table, subtotal, total, payment instructions with Stripe link if available.
- Returns `StreamingResponse` with `media_type="application/pdf"`.
- No disk storage in MVP.

### Stripe Integration

- Payment Links created via Stripe API, associated with invoice record.
- Webhook endpoint validates signature using `stripe.Webhook.construct_event()`.
- Processes `checkout.session.completed` event: looks up invoice by session metadata, marks as paid.

### Error Handling

- Plan limit exceeded: HTTP 402 with message "Free plan limit reached. Upgrade to Pro for unlimited clients/invoices."
- Invalid status transition: HTTP 400 with message "Cannot transition invoice from {current} to {requested}."
- Tenant isolation violation: HTTP 404 (resource not found — do not reveal existence).
- Stripe webhook signature mismatch: HTTP 400, no processing.

## Testing Decisions

- **What makes a good test**: Tests exercise external behavior through the API contract. No mocking of internal repository methods. Integration tests hit a real PostgreSQL test database.
- **Modules to test**:
  - Auth flow (register, login, refresh, current user).
  - Client CRUD with limit enforcement (free plan at 5, then upgrade, then unlimited).
  - Invoice CRUD with status transitions (valid and invalid).
  - Invoice numbering (sequential per tenant, no gaps under normal operation).
  - PDF generation endpoint (verify HTTP 200, content-type is PDF, response body is valid PDF bytes).
  - Stripe webhook handler (mock Stripe event with valid signature, verify invoice status change).
  - Celery tasks (email sending with PDF attachment, overdue checking).
  - Tenant isolation (verify user A cannot access user B's resources).
- **Prior art**: Pytest + httpx for async API tests. Testcontainers or docker-compose for PostgreSQL. Factory fixtures for users, clients, invoices.

## Out of Scope

- Frontend / UI of any kind.
- Logo upload or custom branding on invoices.
- Multi-currency support.
- Revenue reports or dashboards.
- Accounting integrations.
- Push notifications or SMS.
- File storage for generated PDFs (on-demand only).
- Invoice editing after sent status (immutable once sent).

## Further Notes

- **PDF under load**: WeasyPrint is CPU-intensive. Under high concurrency, PDF generation could become a bottleneck. Mitigation options for post-MVP: offload to Celery task with result polling, or cache rendered PDFs briefly in Redis. For MVP, on-demand generation should be acceptable given the target audience size.
- **Webhook reliability**: Stripe retries webhook delivery for up to 3 days. The handler must be idempotent — if `checkout.session.completed` is received for an already-paid invoice, return 200 without side effects.
- **Invoice immutability**: Once an invoice is sent, it should not be editable. This prevents confusion where a client has a PDF but the numbers change. Only draft invoices can be updated or deleted.
- **Sequential numbering race condition**: The max-number query + increment must happen in a serializable transaction or use `SELECT ... FOR UPDATE` to prevent duplicate numbers under concurrent invoice creation.
