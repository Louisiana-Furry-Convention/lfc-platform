# LFC Platform API Handoff
## For WordPress / Website Integration

This document describes the current public-facing and authenticated API endpoints intended for website integration.

## Integration Model

LFC Platform is intended to run separately from the WordPress website.

### Recommended Structure
- `www.domain.com` → WordPress website
- `app.domain.com` → LFC attendee/staff/admin app
- `api.domain.com` → LFC Platform API

WordPress can:
- link users into the app
- directly call public API endpoints
- optionally use a plugin or custom JavaScript to integrate API responses into pages

---

## Base URL

Example:

```text
https://api.domain.com
Authentication

Authenticated endpoints use bearer token auth.

Header format:

Authorization: Bearer <access_token>
Public Endpoints
1. Get Public Event Info
GET /events/public/{event_id}
Example
GET /events/public/lfc-2027
Response
{
  "event_id": "lfc-2027",
  "name": "LFC 2027",
  "location": "Baton Rouge Marriott",
  "start_date": "2027-01-29",
  "end_date": "2027-01-31"
}
2. Get Public Ticket Tiers
GET /tickets/public/ticket_types?event_id=lfc-2027
Response
[
  {
    "id": "lfc-2027-regular",
    "event_id": "lfc-2027",
    "name": "Regular",
    "price_cents": 10000,
    "currency": "USD"
  }
]
Auth Endpoints
3. Signup
POST /auth/signup
Request
{
  "email": "user@example.com",
  "password": "password123",
  "display_name": "Thor"
}
Response
{
  "ok": true
}
4. Login
POST /auth/login
Request
{
  "email": "user@example.com",
  "password": "password123"
}
Response
{
  "access_token": "TOKEN_HERE",
  "token_type": "bearer",
  "role": "attendee",
  "user": {
    "id": "USER_ID",
    "email": "user@example.com",
    "display_name": "Thor",
    "role": "attendee"
  }
}
Authenticated Attendee Endpoints
5. Create Order / Issue Ticket Scaffold
POST /tickets/orders/create
Authorization: Bearer <token>
Request
{
  "event_id": "lfc-2027",
  "ticket_type_id": "lfc-2027-regular"
}
Response
{
  "ok": true,
  "order_id": "ORDER_ID",
  "ticket_id": "TICKET_ID",
  "ticket_type_id": "lfc-2027-regular",
  "qr_token": "QR_TOKEN_HERE",
  "price_cents": 10000,
  "currency": "USD"
}
6. Get My Tickets
GET /me/tickets
Authorization: Bearer <token>
Response
[
  {
    "ticket_id": "TICKET_ID",
    "event_id": "lfc-2027",
    "ticket_type_id": "lfc-2027-regular",
    "ticket_type_name": "Regular",
    "status": "issued",
    "qr_token": "QR_TOKEN_HERE"
  }
]
7. Render QR Badge PNG
GET /tickets/qr/{qr_token}

This returns a PNG image suitable for attendee display.

Example
GET /tickets/qr/QR_TOKEN_HERE
Staff / Admin Endpoints

These are internal and should not be exposed publicly in WordPress.

POST /checkin

GET /admin/live_feed

GET /admin/lane_analytics

GET /admin/arrival_surge

GET /admin/db/table

Recommended WordPress Use
Public Website Pages

WordPress should call:

GET /events/public/{event_id}

GET /tickets/public/ticket_types

to build pages like:

event info

ticket pricing

buy tickets

Login / Attendee Portal

WordPress may:

redirect users into the LFC app

or call /auth/login, /auth/signup, /me/tickets directly

Recommended Initial Deployment

Best first deployment:

WordPress for public content

LFC Platform app for account/ticket/badge flow

This keeps convention logic separate from WordPress and makes long-term scaling easier.

Notes
Current Version

v0.1.2-beta

Current Status

This API currently supports:

attendee auth

public event info

public ticket tier listing

ticket issuance scaffold

attendee QR badge display

internal admin operations

Planned Later Additions

payment provider integration

full order lifecycle

refined public purchase flow

improved ticket status model
