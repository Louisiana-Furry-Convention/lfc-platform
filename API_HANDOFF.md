LouisiAnthro Convention Platform
Backend Version: v0.1.4

Organization: Louisiana Furry Convention LLC (LFC)
Event: LouisiAnthro 2027

This document describes how the website frontend integrates with the LFC ticketing backend.

API Base

Example development URL:

http://127.0.0.1:8000

Production will be something like:

https://api.louisianthro.org
Authentication

Authentication uses JWT Bearer tokens.

Login
POST /auth/login
Request
{
  "email": "user@example.com",
  "password": "password123"
}
Response
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer",
  "role": "attendee",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "display_name": "User Name",
    "role": "attendee"
  }
}

Frontend should store:

access_token

and include it in requests:

Authorization: Bearer TOKEN
Create Account
POST /auth/signup
Request
{
  "email": "user@example.com",
  "password": "password123",
  "display_name": "User Name"
}
Response
{
  "ok": true
}
Current User
GET /auth/me

Header:

Authorization: Bearer TOKEN
Response
{
  "ok": true,
  "id": "uuid",
  "email": "user@example.com",
  "role": "attendee",
  "is_active": true
}
Ticket Types (Public)

Used to display registration options.

GET /tickets/public/ticket_types
Response
[
  {
    "id": "lfc-2027-early",
    "event_id": "lfc-2027",
    "name": "Early Registration",
    "price_cents": 4500,
    "currency": "USD"
  },
  {
    "id": "lfc-2027-regular",
    "event_id": "lfc-2027",
    "name": "Regular Registration",
    "price_cents": 7000,
    "currency": "USD"
  }
]

Frontend should convert:

price_cents / 100

Example:

7000 → $70.00
Create Order

User must be authenticated.

POST /tickets/orders/create

Header:

Authorization: Bearer TOKEN
Request
{
  "event_id": "lfc-2027",
  "ticket_type_id": "lfc-2027-regular"
}
Response
{
  "ok": true,
  "order_id": "uuid",
  "event_id": "lfc-2027",
  "ticket_type_id": "lfc-2027-regular",
  "status": "pending",
  "price_cents": 7000,
  "currency": "USD"
}

The frontend should store the order_id.

User Orders
GET /me/orders

Header:

Authorization: Bearer TOKEN
Response
[
  {
    "order_id": "uuid",
    "event_id": "lfc-2027",
    "ticket_type_id": "lfc-2027-regular",
    "ticket_type_name": "Regular Registration",
    "status": "pending",
    "total_cents": 7000,
    "currency": "USD",
    "clover_checkout_id": null,
    "clover_payment_id": null,
    "created_at": "2026-03-13T09:35:51",
    "paid_at": null
  }
]

Status values:

pending
paid
paid_test
User Tickets
GET /me/tickets

Header:

Authorization: Bearer TOKEN
Response
[
  {
    "ticket_id": "uuid",
    "order_id": "uuid",
    "event_id": "lfc-2027",
    "ticket_type_id": "lfc-2027-regular",
    "ticket_type_name": "Regular Registration",
    "status": "issued",
    "qr_token": "ticketid|signature",
    "issued_at": "2026-03-13T09:42:41"
  }
]
QR Code Generation

The QR code for a ticket can be rendered via:

GET /tickets/qr/{qr_token}

Example:

/tickets/qr/d7cf0442-4aa6-4579-b6e3-af2ec3f0b23e|83b77fe723a45973

Returns:

PNG image

The website can embed it as:

<img src="/tickets/qr/{qr_token}" />
Ticket Purchase Flow

Frontend should follow this flow.

Step 1

Display available registrations

GET /tickets/public/ticket_types
Step 2

User logs in or creates account

POST /auth/login
or
POST /auth/signup
Step 3

Create order

POST /tickets/orders/create

Store:

order_id
Step 4

Redirect to payment (Clover integration coming)

Example future flow:

POST /payments/clover/create_checkout

Return:

checkout_url

Frontend redirects user.

Step 5

After successful payment

Payment webhook marks order:

status = paid

Ticket is automatically issued.

Step 6

User dashboard loads tickets

GET /me/tickets

Display:

ticket_type_name
QR code
issued_at
Ticket Dashboard Example

Display something like:

LouisiAnthro 2027
Regular Registration

[ QR CODE ]

Ticket ID
Issued Date
Security Notes

Frontend must not trust ticket data from client state.

Always reload tickets from:

GET /me/tickets
Admin Notes

Admin endpoints exist for:

order completion

live analytics

check-in scanning

These are not used by the public website.

Backend Version

Current backend version:

v0.1.4

Supports:

authentication

attendee accounts

ticket orders

ticket issuance

QR generation

admin completion
