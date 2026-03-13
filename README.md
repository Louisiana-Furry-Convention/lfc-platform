# LFC Platform

Backend platform for **LouisiAnthro**, operated by **Louisiana Furry Convention LLC (LFC)**.

This repository contains the backend API responsible for:

- attendee authentication
- ticket sales and issuance
- QR ticket generation
- order management
- staff check-in infrastructure
- future RFID support
- operational analytics

Primary backend framework:

```
FastAPI
SQLAlchemy
SQLite (dev)
```

The platform is designed to eventually support:

```
- ticket sales
- attendee dashboard
- QR badge system
- RFID wristband integration
- check-in scanners
- operations analytics
- convention infrastructure tooling
```

---

# Project Status

Current stable backend tag:

```
v0.1.4
```

Status:

```
Backend ticketing system complete
Ready for website integration
Pending Clover payment credentials
```

---

# Repository Structure

```
apps/
 └── api/
      ├── lfc_api/
      │    ├── core/
      │    │    ├── authz.py
      │    │    ├── badge.py
      │    │    ├── security.py
      │    │    └── ticketing.py
      │    │
      │    ├── db/
      │    │    ├── session.py
      │    │    └── bootstrap.py
      │    │
      │    ├── models/
      │    │    ├── user.py
      │    │    ├── ticketing.py
      │    │    ├── event.py
      │    │    └── ledger.py
      │    │
      │    ├── routers/
      │    │    ├── auth.py
      │    │    ├── tickets.py
      │    │    ├── checkin.py
      │    │    └── payments.py
      │    │
      │    └── main.py
      │
      └── requirements.txt
```

---

# Local Development

## 1. Create environment

```
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install dependencies

```
pip install -r requirements.txt
```

## 3. Initialize database

```
python -m lfc_api.db.bootstrap
```

This creates:

```
events
users
orders
tickets
ticket_types
checkins
rfid_bands
domain_events
```

---

# Run API

```
uvicorn lfc_api.main:app --reload
```

API default:

```
http://127.0.0.1:8000
```

Health check:

```
GET /health
```

---

# Core API Endpoints

## Authentication

```
POST /auth/signup
POST /auth/login
GET  /auth/me
```

## Ticket Catalog

```
GET /tickets/public/ticket_types
```

Returns available registrations.

Example:

```
[
  {
    "id": "lfc-2027-regular",
    "name": "Regular Registration",
    "price_cents": 7000
  }
]
```

---

## Order Creation

```
POST /tickets/orders/create
```

Example request:

```
{
  "event_id": "lfc-2027",
  "ticket_type_id": "lfc-2027-regular"
}
```

---

## User Orders

```
GET /me/orders
```

---

## User Tickets

```
GET /me/tickets
```

Example:

```
[
  {
    "ticket_id": "uuid",
    "ticket_type_name": "Regular Registration",
    "status": "issued",
    "qr_token": "ticketid|signature"
  }
]
```

---

## QR Ticket Rendering

```
GET /tickets/qr/{qr_token}
```

Returns:

```
PNG QR image
```

---

# Check-In System

Staff scanning endpoint:

```
POST /checkin/
```

Request:

```
{
  "qr_token": "ticketid|signature"
}
```

Possible responses:

```
checked_in
already_checked_in
invalid
```

---

# Ticket Issuance Logic

Tickets are issued through:

```
lfc_api.core.ticketing.issue_ticket_for_order()
```

Behavior:

```
1 order = 1 ticket
```

Duplicate issuance protection is enforced:

```
existing_ticket = db.query(Ticket).filter(Ticket.order_id == order.id).first()
```

---

# Database Bootstrap

Bootstrap script:

```
python -m lfc_api.db.bootstrap
```

Creates:

```
default admin
default event
default ticket types
```

Current event:

```
lfc-2027
LouisiAnthro 2027
```

---

# Release Notes

## v0.1.4

Major backend milestone.

Implemented:

```
attendee authentication
ticket catalog endpoint
order creation
attendee order dashboard
ticket issuance system
QR ticket generation
admin order completion
duplicate-safe ticket issuance
database bootstrap initialization
API documentation for web integration
```

Status:

```
Backend feature complete for ticket flow
Waiting on website integration
Waiting on Clover production credentials
```

---

## v0.1.3-beta

Implemented:

```
ticket types
basic order model
QR token system
initial ticket issuance logic
admin tooling
```

Focus:

```
ticketing foundation
```

---

## v0.1.2-alpha

Implemented:

```
staff role promotion tools
secure check-in endpoint
JWT authentication wiring
database seeding fixes
```

Focus:

```
internal admin infrastructure
```

---

## v0.1.1-alpha

Implemented:

```
initial admin panel endpoints
staff check-in routing
live analytics stubs
```

Focus:

```
operations backbone
```

---

## v0.1.0-alpha

Initial platform foundation.

Implemented:

```
FastAPI backend skeleton
SQLAlchemy models
user authentication
database session management
initial event structure
```

Focus:

```
core architecture
```

---

# Planned Features

Next milestone:

```
v0.1.5
```

Planned work:

```
Clover checkout integration
payment webhook processing
staff check-in scanner UI
RFID assignment endpoints
```

Longer term goals:

```
RFID wristband tracking
room attendance analytics
dealer/vendor management
panel scheduling integration
operations dashboards
```

---

# License

Internal project for:

```
Louisiana Furry Convention LLC
```

---

# Maintainer

Primary developer:

```
Joe / Thor
Co-Founder / CEO, CFO, CSO, J-CTO
Louisiana Furry Convention LLC
```

Project repository:

```
https://github.com/Thorthedefender/lfc-platform
```

---
