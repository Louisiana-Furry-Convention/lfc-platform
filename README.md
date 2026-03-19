# LFC Platform

LFC Platform is a custom-built convention management system designed to support large-scale events with internal operations, applications, ticketing, and staff coordination.

Current focus is **v0.2.x — Applications System**, with future expansion into operations, e-commerce, and client apps.

---

# 🚧 Current Version
**v0.2.1 — Applications Review Workflow Stabilized**

---

# ✅ Current Features

## Authentication
- JWT-based authentication
- Admin login system
- `/auth/login`
- `/auth/me`

## Applications System (Core of v0.2.x)
Supports:
- Staff applications
- Vendor applications
- Panel submissions

### Backend
- Unified `applications` model
- Application status lifecycle:
  - `submitted`
  - `under_review`
  - `approved`
  - `declined`
  - `waitlisted`
  - `withdrawn`

- Stage progression system:
  - staff:
    - submitted → hr_interview → lead_interview → director_review → officer_review → hr_onboarding → complete
  - vendor/panel:
    - submitted → review → complete

### Review System
- Create structured review entries
- Review history per application
- Notes required for actions
- Non-terminal stage updates allowed
- Terminal status lock enforced

Terminal statuses:
- approved
- declined
- waitlisted
- withdrawn

### API Endpoints

GET /health
POST /auth/login
GET /auth/me

GET /admin/applications
GET /admin/applications/{id}
PATCH /admin/applications/{id}/status
PATCH /admin/applications/{id}/stage

GET /admin/applications/{id}/reviews
POST /admin/applications/{id}/reviews


---

# 🖥️ Web UI

## Admin Applications Page
- Table + detail panel layout
- Review-first workflow
- Application detail breakdown
- Review history timeline
- Raw payload toggle
- Terminal status lock message

## Tickets Page
- Cleaned to prevent QR dependency crashes

---

# 🗂️ Project Structure


lfc-platform/

├── apps/

│ ├── api/

│ │ ├── lfc_api/

│ │ │ ├── routers/

│ │ │ ├── models/

│ │ │ ├── core/

│ │ │ └── ...

│ │ └── lfc_edge.db

│ │

│ └── web/

│ ├── admin-apps.html

│ ├── tickets.html

│ ├── assets/

│ │ ├── js/

│ │ ├── css/

│ │ └── ...


---

# 🧪 Quick Start

## Start API
```bash
cd apps/api
source .venv/bin/activate
uvicorn lfc_api.main:app --reload
Health Check
curl http://127.0.0.1:8000/health
Get Token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@lfc.local","password":"admin"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')
Test Applications
curl -H "Authorization: Bearer $TOKEN" \
http://127.0.0.1:8000/admin/applications
Start Web UI
cd apps/web
python3 -m http.server 8080
```
Open:

http://<your-ip>:8080/admin-apps.html

⚠️ Important Rules

Do NOT:

Reintroduce deprecated fields:

reviewed_by

reviewed_at

review_notes

Duplicate ApplicationReview model

Use reviewer_id (use reviewed_by_user_id)

Use denied (use declined)

Modify terminal status behavior

📌 Known Good State

API stable

Admin UI stable

Application review fully functional

Stage transitions working

Review history working

Terminal lock enforced

Tickets page no longer crashes

🚀 Roadmap
v0.2.x — Applications

Unified application engine ✅

Review workflow ✅

UI stabilization ✅

Minor polish (in progress)

v0.3.x — Operations

Inventory system

Asset checkout

Staff tracking

RFID integration (planned)

v0.4.x — E-Commerce

Ticket sales

Payments (Clover integration)

Order management

v0.5.x — Client Apps

Staff web app

Mobile check-in tools

PWA support

v1.0.0 — Full Convention System

Production-ready deployment

Fully integrated convention platform

🎯 Project Direction

Internal-first tooling

Stability over speed

Controlled feature expansion

No operations layer work until v0.3.x+

🧠 Notes

This platform is designed specifically for:

Large-scale conventions

Multi-department operations

Real-time staff coordination

Expandable infrastructure

👤 Maintained By

LFC (Louisiana Furry Convention) Technology Team:

Thor, Co-President & J-CTO
