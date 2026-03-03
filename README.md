# LFC Platform

Internal registration and operations backend for Louisiana Furry Convention.

This repository contains the backend system that will power:

- Ticket issuance
- QR token generation
- Staff-controlled check-in
- Role-based access control
- Event ledger logging
- Future registration dashboard

This is currently in **active development** and running on a Raspberry Pi edge node for testing.

---

# CURRENT DEVELOPMENT STATUS

## Version: v0.1 – Edge Check-In Foundation

Working Features:

- Event model
- User model with roles
- Ticket issuance endpoint
- QR token generation
- Staff-only check-in enforcement
- Duplicate scan prevention
- Role promotion endpoint
- SQLite database
- Alembic migrations
- Ledger logging (DomainEvent)
- Deployed via systemd on Raspberry Pi

API is operational and health-checked.

---

# ARCHITECTURE

Backend:
FastAPI

Database:
SQLite (edge testing)
PostgreSQL planned for production

ORM:
SQLAlchemy

Migrations:
Alembic

Authentication:
Role-based (no JWT yet)

Password Hashing:
PBKDF2 (bcrypt removed for ARM compatibility)

Deployment:
systemd service (`lfc-api.service`) on Raspberry Pi

---

# ROLE SYSTEM

Current roles:

- attendee
- staff
- checkin
- admin

Check-in requires:
- Active user
- Role in {staff, checkin, admin}

Promotion endpoint allows upgrading users.

JWT login system not implemented yet.

---

# HOW TO RUN (DEVELOPMENT)

## Clone
# LFC Platform

Internal registration and operations backend for Louisiana Furry Convention.

This repository contains the backend system that will power:

- Ticket issuance
- QR token generation
- Staff-controlled check-in
- Role-based access control
- Event ledger logging
- Future registration dashboard

This is currently in **active development** and running on a Raspberry Pi edge node for testing.

---

# CURRENT DEVELOPMENT STATUS

## Version: v0.1 – Edge Check-In Foundation

Working Features:

- Event model
- User model with roles
- Ticket issuance endpoint
- QR token generation
- Staff-only check-in enforcement
- Duplicate scan prevention
- Role promotion endpoint
- SQLite database
- Alembic migrations
- Ledger logging (DomainEvent)
- Deployed via systemd on Raspberry Pi

API is operational and health-checked.

---

# ARCHITECTURE

Backend:
FastAPI

Database:
SQLite (edge testing)
PostgreSQL planned for production

ORM:
SQLAlchemy

Migrations:
Alembic

Authentication:
Role-based (no JWT yet)

Password Hashing:
PBKDF2 (bcrypt removed for ARM compatibility)

Deployment:
systemd service (`lfc-api.service`) on Raspberry Pi

---

# ROLE SYSTEM

Current roles:

- attendee
- staff
- checkin
- admin

Check-in requires:
- Active user
- Role in {staff, checkin, admin}

Promotion endpoint allows upgrading users.

JWT login system not implemented yet.

---

# HOW TO RUN (DEVELOPMENT)

## Clone

git clone https://github.com/Thorthedefender/lfc-platform.git


## Enter API directory


cd apps/api


## Create virtual environment


python3 -m venv .venv
source .venv/bin/activate


## Install dependencies


pip install -r requirements.txt


## Run migrations


alembic upgrade head


## Seed database


python seed.py


## Start locally


uvicorn lfc_api.main:app --reload


Swagger UI:
http://127.0.0.1:8000/docs

---

# EDGE NODE (Raspberry Pi)

Service:
lfc-api.service

Restart:

sudo systemctl restart lfc-api


Health check:

curl http://127.0.0.1:8000/health


---

# CURRENT WORKFLOW

1. Create Event (seeded)
2. Issue ticket via `/tickets/issue_test`
3. Promote staff via `/admin/promote_user_role`
4. Perform check-in via `/checkin`
5. DomainEvent logged

---

# WHAT IS NOT BUILT YET

- JWT login / authentication tokens
- Staff login session system
- Front-end dashboard
- Payment processing
- Capacity enforcement
- Refund logic
- Vendor module
- Financial reporting
- Occupancy tracking
- Production-level database

---

# NEXT DEVELOPMENT TARGETS

Immediate:

- Basic frontend dashboard (HTML or React)
- Ticket lookup endpoint
- Staff login system (JWT)
- Role-based route protection decorator

Mid-Term:

- Tier capacity limits
- Live check-in counter
- Financial reporting endpoints
- Better audit logging

Long-Term:

- Multi-event support
- Vendor management
- Production asset tracking
- Executive analytics dashboard

---

# CONTRIBUTION GUIDELINES

Changes affecting:

- Database schema
- Role logic
- Check-in logic
- Financial models
- Ticket validation

Should be reviewed before deployment to edge.

---

# OWNERS

Executive Authority:
Thor

Technical Director:
Cache

This repository represents the operational backbone of the event and should be treated as production infrastructure in progress.
