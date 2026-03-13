CHECKIN_API.md

LouisiAnthro Convention Platform
Backend Version: v0.1.4

Organization: Louisiana Furry Convention LLC (LFC)
Event: LouisiAnthro 2027

This document describes the QR check-in and future RFID check-in API behavior for convention operations.

Purpose

This API supports:

attendee badge/ticket validation

front-door check-in

lane tracking

future RFID wristband assignment

future room/panel attendance tracking

Current live-capable focus:

QR ticket validation

staff-performed attendee check-in

admin visibility into check-in flow

Authentication

Check-in endpoints are authenticated.

Staff must log in and send a bearer token:

Authorization: Bearer TOKEN
Staff Login
POST /auth/login
Request
{
  "email": "staff@example.com",
  "password": "password123"
}
Response
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer",
  "role": "staff",
  "user": {
    "id": "uuid",
    "email": "staff@example.com",
    "display_name": "Staff Name",
    "role": "staff"
  }
}
QR / Ticket Check-In

Primary endpoint:

POST /checkin/

This endpoint is used by the staff-facing check-in station after scanning a QR token.

Request
{
  "qr_token": "ticketid|signature"
}

If lane support is active in the current router version, the request may also include:

{
  "qr_token": "ticketid|signature",
  "lane": "main"
}

If your current version only accepts qr_token, use only that field.

Authentication
Authorization: Bearer TOKEN
Successful first-time check-in response

Example shape:

{
  "ok": true,
  "ticket_id": "uuid",
  "status": "checked_in"
}

Some builds may return more details, for example:

{
  "ok": true,
  "ticket_id": "uuid",
  "ticket_status": "issued",
  "checkin_status": "checked_in",
  "already_checked_in": false
}

Use the actual returned values from your deployment, but operationally the key state is:

checked_in
Already checked in response

Example shape:

{
  "ok": true,
  "ticket_id": "uuid",
  "status": "already_checked_in"
}

or:

{
  "ok": true,
  "already_checked_in": true
}

Operational meaning:

ticket is valid

attendee has already been processed

do not issue a second physical check-in

Invalid / rejected responses

Examples:

{
  "detail": "Invalid ticket"
}
{
  "detail": "Ticket not found"
}
{
  "detail": "Forbidden"
}

Treat any non-200 or explicit error as a failed scan requiring staff review.

Recommended Check-In UI Behavior
Green state

Show when response indicates successful first-time check-in:

CHECK-IN SUCCESSFUL

Suggested display:

attendee accepted

lane recorded

timestamp recorded

Yellow state

Show when response indicates already checked in:

ALREADY CHECKED IN

Suggested staff action:

verify attendee identity/badge

escalate only if duplicate-use is suspected

Red state

Show when response indicates invalid token or failure:

INVALID OR REJECTED TICKET

Suggested staff action:

move attendee to problem-solving desk

do not manually wave through without verification

Ticket Source

Tickets come from:

GET /me/tickets

Each ticket includes:

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

That qr_token is what is encoded in the QR image.

QR Image Rendering

QR image endpoint:

GET /tickets/qr/{qr_token}

Returns:

PNG image

This is used by:

attendee dashboard

digital ticket display

possible print workflows

Check-In Operational Flow
Step 1

Staff logs into the check-in station.

POST /auth/login
Step 2

Scanner reads attendee QR.

The scanned value should be the raw qr_token.

Example:

d7cf0442-4aa6-4579-b6e3-af2ec3f0b23e|83b77fe723a45973
Step 3

Station sends token to backend.

POST /checkin/
Step 4

Backend validates:

ticket exists

token is valid

ticket belongs to event

ticket has not already been checked in

Step 5

Backend records:

check-in timestamp

staff user performing the scan

lane if supported

Step 6

UI displays result:

checked in

already checked in

invalid / rejected

Suggested Check-In Station Payload

Use this payload shape if supported by your current router:

{
  "qr_token": "ticketid|signature",
  "lane": "main"
}

Suggested lane values:

main
vip
staff
vendor
problem

If your current backend only accepts qr_token, lane can be added in a later version.

Check-In Data Model

Current check-in table stores:

id

ticket_id

lane

checked_in_at

performed_by_user_id

created_at

This enables:

arrival tracking

lane analytics

live feed

audit trail

Staff Permissions

Check-in should only be available to authorized users.

Recommended allowed roles:

admin
staff
operations
registration
safety

Actual enforcement depends on current role wiring in the backend.

If a staff user gets:

{
  "detail": "Forbidden"
}

their role or access configuration needs adjustment.

Admin / Operations Visibility

Related admin endpoints may include:

GET /admin/live_feed?limit=20
GET /admin/arrival_surge?event_id=lfc-2027
GET /admin/lane_analytics?event_id=lfc-2027

These are useful for operations dashboards, not public attendee pages.

RFID Foundation

RFID support is planned and partially modeled.

Current table:

rfid_bands

Fields include:

id

tag_uid

event_id

user_id

ticket_id

status

is_active

issued_at

revoked_at

created_at

Planned uses:

wristband assignment at registration

room entry tracking

panel attendance

crowd analytics

checkpoint flow measurement

Future RFID Flow

Planned operational flow:

Registration desk

attendee checks in via QR

RFID band is assigned to ticket/user

RFID band becomes active

Room checkpoints

scanner reads RFID tag

backend records attendance event

analytics dashboard updates traffic counts

Future likely endpoints

Examples only, not final:

POST /rfid/assign
POST /rfid/revoke
POST /attendance/scan
GET /attendance/room_counts
Frontend / Scanner App Guidance

Scanner app should:

stay logged in as staff

accept USB/Bluetooth scanner input

immediately submit scanned token

show large color-coded result

optionally play distinct success/failure sounds

avoid displaying unnecessary attendee data on public-facing screens

Recommended on-screen fields:

result state

short status message

lane

timestamp

operator identity if useful for audit

Error Handling Guidance
Invalid token

Show:

INVALID TICKET
Already checked in

Show:

ALREADY CHECKED IN
Network/API failure

Show:

CHECK-IN SYSTEM ERROR

Staff action:

pause line if widespread

route attendee to manual resolution if isolated

Security Notes

Check-in stations must:

require authenticated staff session

never trust client-side validation

always verify through API

avoid exposing admin controls in public station UI

QR tokens should be treated as access credentials for entry purposes.

Current Version Scope

Validated in v0.1.4 backend work:

ticket issuance

QR token generation

check-in table foundation

authenticated backend structure

Primary live-ready path:

attendee ticket exists

QR displays

staff station submits scan

backend records check-in

