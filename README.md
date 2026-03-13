# LFC Platform

Convention Operations Platform for Frosty Fur Fest

---

# Version Status

## v0.1.3-beta (Current Development Snapshot)

This version establishes the **core ticketing and purchase backbone** for the platform. The goal of 0.1.3 was to ensure that tickets can be created, cataloged, and prepared for payment processing safely.

### Major Features Implemented

#### Ticket Catalog

* Public ticket catalog endpoint
* Internal ticket types hidden from public purchase
* Support for multiple ticket tiers

Endpoint:

```
GET /tickets/public/ticket_types
```

Returns only ticket types where:

```
is_active = true
is_public = true
```

This prevents internal tickets (staff/vendor/etc) from appearing in the public store.

---

#### Order Creation

Authenticated users can create ticket purchase orders.

Endpoint:

```
POST /tickets/orders/create
```

Creates an order in **pending** state.

Order fields:

* order_id
* event_id
* ticket_type_id
* total_cents
* status

---

#### Payment Router (Clover Integration Skeleton)

Payment router created and wired into the API.

Endpoints:

```
POST /payments/clover/checkout
POST /payments/clover/webhook
```

Capabilities:

* Creates Clover hosted checkout session
* Associates checkout session with platform order
* Webhook verifies Clover signature
* Marks order as paid

Ticket issuance hook prepared but not fully wired to production payment flow.

---

#### Admin Ticket Controls

Admins can modify ticket types via API.

Endpoint:

```
PATCH /admin/ticket_types/{ticket_type_id}
```

Fields that can be updated:

* name
* price_cents
* is_active

This allows convention leadership to adjust ticket availability and pricing without direct database access.

---

#### Ticket Issuance

Tickets are created when an order transitions to **paid**.

Ticket includes:

* ticket_id
* qr_token
* order_id
* ticket_type_id

QR tokens are generated securely and can be rendered via:

```
GET /tickets/qr/{qr_token}
```

---

#### RFID Foundation

RFID band model exists for future integration.

Table:

```
rfid_bands
```

Designed to support:

* attendee wristbands
* room access
* panel attendance tracking

Full usage planned for a later version.

---

# Current System Architecture

```
Website
   ↓
API (FastAPI)
   ↓
Orders
   ↓
Clover Checkout
   ↓
Webhook
   ↓
Ticket Issuance
```

---

# Known Limitations in v0.1.3

These are intentionally deferred:

* Clover credentials not yet configured
* Website purchase page not implemented
* Ticket purchase UI missing
* Admin dashboard improvements pending

Backend functionality is ready for integration.

---

# Goals for v0.1.4

Version 0.1.4 focuses on **public ticket sales and website integration**.

### Primary Objectives

1. Implement public purchase page
2. Connect website purchase flow to API
3. Complete Clover payment integration
4. Automatic ticket issuance after webhook payment confirmation

---

### Website Purchase Flow

Target flow for website:

```
1. Load available tickets
GET /tickets/public/ticket_types

2. User selects ticket

3. Create order
POST /tickets/orders/create

4. Start checkout
POST /payments/clover/checkout

5. Redirect to Clover hosted checkout

6. Clover webhook confirms payment

7. Ticket issued

8. Website displays ticket
```

---

# Website Team Handoff Notes

The backend API is now stable enough for frontend integration.

## Ticket Catalog

Endpoint:

```
GET /tickets/public/ticket_types
```

Example response:

```
[
 {
  "id": "lfc-2027-regular",
  "name": "Regular Registration",
  "price_cents": 7000,
  "currency": "USD"
 }
]
```

Prices are returned in **cents**.

Frontend should display:

```
price_cents / 100
```

---

## Creating an Order

Endpoint:

```
POST /tickets/orders/create
```

Body:

```
{
 "ticket_type_id": "lfc-2027-regular"
}
```

Returns:

```
{
 "order_id": "uuid",
 "price_cents": 7000
}
```

---

## Starting Checkout

Endpoint:

```
POST /payments/clover/checkout
```

Body:

```
{
 "order_id": "uuid"
}
```

Response:

```
{
 "checkout_url": "https://checkout.clover.com/..."
}
```

Frontend should redirect the user to this URL.

---

## After Payment

Clover will redirect the user back to the website.

Redirect URLs are configured in API config.

Possible endpoints:

```
/purchase/success
/purchase/cancel
```

Website should then query the user's tickets.

---

# Security Notes

Key protections already implemented:

* Only authenticated users can create orders
* Orders belong to the authenticated user
* Internal ticket types cannot be purchased
* Payment confirmation handled via Clover webhook

This prevents most common ticket fraud patterns.

---

# Development Notes

Current development environment:

```
Python 3.11
FastAPI
SQLite (edge deployment)
Docker-ready architecture
```

Planned future upgrades:

* PostgreSQL production database
* Redis caching
* containerized deployment

---

# Next Major Milestones

After v0.1.4:

* RFID wristband issuance
* panel attendance tracking
* queue analytics
* real-time event dashboards

---

# Project Vision

The long term goal is a **full convention operating system** including:

* registration
* ticketing
* staff management
* attendance analytics
* queue management
* live event telemetry

---

End of v0.1.3-beta documentation.

## Release Notes

### v0.1.2-beta
- added real check-in timestamps
- fixed live arrivals to use true timestamps
- added lane analytics
- added surge detection
- added admin DB viewer
- added public event info endpoint
- added public ticket tier listing endpoint
- added attendee My Tickets page
- added attendee My Badge full-screen QR page
- added QR PNG rendering endpoint
- stabilized dashboard refresh behavior
