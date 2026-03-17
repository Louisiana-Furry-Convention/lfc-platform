# LFC Platform

Convention operations platform for **Louisiana Furry Convention (LouisiAnthro)**.

The LFC Platform is designed to become the **central operating system for the convention**, powering ticketing, staff management, vendor management, panel scheduling, inventory, and operations tools.

Repository:
https://github.com/Thorthedefender/lfc-platform

---

# Current Version


v0.1.5


Environment example:

```json
{
  "ok": true,
  "app": "lfc-platform",
  "version": "v0.1.5",
  "environment": "dev"
}
Platform Status

Core backend ticketing system is operational.

Verified workflow:

signup
login
create order
admin complete order
ticket issued
ticket visible in /me/tickets
QR generated
check-in endpoint operational

Current development environment:

Raspberry Pi
Ubuntu Server
FastAPI
SQLite
Quick Start

Clone repository

git clone https://github.com/Thorthedefender/lfc-platform.git
cd lfc-platform/apps/api

Create virtual environment

python3 -m venv .venv
source .venv/bin/activate

Install dependencies

pip install -r requirements.txt

Run development server

uvicorn lfc_api.main:app --reload

API available at:

http://127.0.0.1:8000

Interactive docs:

http://127.0.0.1:8000/docs
System Endpoints

Health check

GET /health

Example response

{
  "ok": true,
  "service": "lfc-platform-api",
  "database": "ok",
  "environment": "dev"
}

Version info

GET /version

Example response

{
  "ok": true,
  "app": "lfc-platform",
  "version": "v0.1.5",
  "environment": "dev",
  "commit": "abc123"
}
Authentication

Signup

POST /auth/signup

Example request

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "Example User"
}

Login

POST /auth/login

Example request

{
  "email": "user@example.com",
  "password": "password123"
}

Response returns a JWT token used for authenticated endpoints.

Ticketing

Public ticket catalog

GET /tickets/public/ticket_types

Example response

[
  {
    "id": "lfc-2027-early",
    "event_id": "lfc-2027",
    "name": "Early Registration",
    "price_cents": 4500
  }
]

Create order

POST /tickets/orders

Example request

{
  "ticket_type_id": "lfc-2027-early",
  "quantity": 1
}

Complete order (admin)

POST /tickets/orders/complete
Tickets

User tickets

GET /me/tickets

Tickets include QR tokens used for check-in.

Check-in System

Validate ticket QR code

POST /checkin

Example request

{
  "qr_token": "TOKEN_VALUE"
}

Possible responses

checked_in
already_checked_in
invalid_ticket
Scanner UI

Basic check-in scanner interface

GET /scan

Designed for:

registration desk
event room checkpoints
RFID/QR scanning stations
Payments

Clover integration scaffold implemented.

Endpoints:

POST /payments/clover/create-order
POST /payments/clover/webhook
GET  /payments/clover/config-test

Clover credentials are configured via environment variables.

CLOVER_MERCHANT_ID
CLOVER_API_KEY
CLOVER_WEBHOOK_SECRET
Environment Configuration

Environment files:

.env.dev
.env.staging
.env.prod

Example:

APP_ENV=dev
APP_VERSION=v0.1.5

DATABASE_URL=sqlite:///./lfc.db

SECRET_KEY=change-me

API_BASE_URL=http://127.0.0.1:8000
FRONTEND_BASE_URL=http://127.0.0.1:3000
Deployment

Deployment is release-driven.

Rules:

Development machines never auto-update
Tagged releases deploy to staging
Published releases deploy to production

Deployment script

scripts/deploy_release.sh

Example usage

./scripts/deploy_release.sh staging v0.1.5

GitHub Actions workflows

.github/workflows/deploy-staging.yml
.github/workflows/deploy-production.yml
Project Roadmap
v0.1.x   Ticketing foundation + deployment hardening
v0.2.x   Applications system
v0.3.x   Operations modules
v0.4.x   E-commerce
v0.5.x   Client-side apps
v1.0.0   Full convention deployment
Release History
v0.1.0-alpha
Initial platform deployment
Basic API structure

v0.1.1-alpha
Authentication
check-in system
ticket issuance

v0.1.2
API stability improvements
database migrations

v0.1.3-beta
ticket catalog
order creation
payment preparation

v0.1.4
complete ticket lifecycle
QR generation
admin order completion

v0.1.5
deployment automation
environment configuration
system health/version endpoints
clover payment scaffold
scanner UI
auth cleanup
Next Milestone
v0.2.0
Applications System

Planned features

staff applications
vendor applications
panel submissions
application review system
attachment uploads
status workflows
Long-Term Vision

The LFC Platform will become the central operating system for the convention.

Future modules

ticketing
staff management
vendor management
panel scheduling
inventory management
merchandise
e-commerce
RFID attendance tracking
operations analytics

Accessible via

public website
staff/admin web interface
mobile operations tools
future desktop client
License

Internal project for Louisiana Furry Convention LLC.


---
