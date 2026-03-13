RFID_OPERATIONS_PLAN.md

LouisiAnthro Convention Platform
Backend Version: v0.1.4
Organization: Louisiana Furry Convention LLC (LFC)
Event: LouisiAnthro 2027

Purpose

This document defines how RFID wristbands will be used during LouisiAnthro for:

• attendee identification
• entry validation
• panel attendance tracking
• crowd analytics
• operational awareness

RFID supplements QR tickets but does not replace ticket issuance.

Tickets remain the authoritative purchase record.

RFID System Overview

RFID wristbands are issued after ticket validation at registration.

Each wristband contains:

RFID UID

The UID is mapped to:

user_id
ticket_id
event_id

Once assigned, the wristband becomes the attendee's primary physical credential.

RFID Lifecycle
1 — Ticket Purchased

User receives digital ticket with QR code.

2 — Arrival at Registration

Staff scans QR ticket.

POST /checkin/

Ticket is validated.

3 — Wristband Issued

Registration desk assigns RFID band.

POST /rfid/assign

Band is now linked to the attendee.

4 — Wristband Activated

Attendee uses band for:

• room entry
• panel attendance
• crowd tracking
• optional perks

5 — Event Ends

RFID bands automatically expire.

RFID Data Model

Current database table:

rfid_bands

Fields:

Field	Description
id	unique record id
tag_uid	RFID chip UID
event_id	event identifier
user_id	linked attendee
ticket_id	linked ticket
status	active / revoked
is_active	true/false
issued_at	timestamp issued
revoked_at	timestamp revoked
created_at	database timestamp
RFID Assignment Endpoint

Planned endpoint:

POST /rfid/assign
Request
{
  "ticket_id": "uuid",
  "tag_uid": "RFID_CHIP_UID"
}
Response
{
  "ok": true,
  "rfid_id": "uuid",
  "tag_uid": "RFID_CHIP_UID",
  "ticket_id": "uuid",
  "status": "active"
}
RFID Scan Endpoint

Used for room entry or checkpoints.

POST /attendance/scan
Request
{
  "tag_uid": "RFID_CHIP_UID",
  "location": "main_stage"
}
Response
{
  "ok": true,
  "user_id": "uuid",
  "ticket_type": "Regular Registration",
  "status": "accepted"
}
Possible Response States
Accepted
accepted

Valid attendee.

Unknown Band
unknown_band

Band UID not registered.

Revoked Band
revoked

Band was disabled.

Duplicate Entry
duplicate_scan

Band already scanned recently.

Location Identifiers

Locations should use standardized IDs.

Example list:

registration
main_stage
panel_room_1
panel_room_2
dance_floor
dealers_den
vip_lounge
staff_area
Panel Attendance Tracking

Panels may optionally scan RFID at the door.

Benefits:

• attendance statistics
• capacity monitoring
• panel popularity analytics

Example flow:

POST /attendance/scan

location:

panel_room_2
Crowd Analytics

RFID scans allow operations to view:

• real-time room occupancy
• attendee traffic flow
• surge detection

Example dashboards:

GET /admin/room_counts
GET /admin/traffic_flow
GET /admin/popular_panels
Registration Desk Workflow

Staff workflow should be:

Scan attendee QR ticket

Confirm valid ticket

Issue wristband

Scan RFID tag to assign

Hand wristband to attendee

This creates a permanent link:

ticket → user → RFID band
Lost Wristband Procedure

If a band is lost:

Verify attendee identity

Revoke previous band

POST /rfid/revoke

Issue new band

POST /rfid/assign
Example Revoke Request
{
  "tag_uid": "RFID_CHIP_UID"
}

Response:

{
  "ok": true,
  "status": "revoked"
}
Hardware Recommendations

RFID Type:

NFC Type A
ISO 14443

Typical tags:

NTAG213
NTAG215
NTAG216
Reader Options

Recommended scanner types:

USB Readers

Plug into check-in computers.

Example:

ACR122U
Embedded Readers

Used for automated stations.

Example:

PN532
Checkpoint Setup

Each checkpoint should have:

• RFID reader
• laptop/tablet
• staff monitor
• network access

Scanner software sends:

POST /attendance/scan
Security Considerations

RFID UID alone should never grant privileges without backend verification.

Always verify:

tag_uid → rfid_bands → ticket → event

Backend must enforce:

• event validity
• band status
• duplicate prevention

Privacy

RFID should not broadcast personal information.

Only UID should be stored on the chip.

All identity mapping happens server-side.

Operational Benefits

RFID enables:

• faster entry scanning
• panel attendance analytics
• crowd heatmaps
• security auditing
• capacity monitoring

Future Expansion

Possible future uses:

Cashless Payments

Food / merch purchases.

VIP Access Control

Room permissions.

Interactive Experiences

Games or scavenger hunts.

Live Traffic Heatmaps

Convention flow visualization.

Operational Policy

RFID wristbands should be:

• worn visibly
• non-transferable
• required for event access

Staff may request verification if misuse is suspected.

Event Configuration

Example event config:

event_id: lfc-2027
event_name: LouisiAnthro 2027
organizer: Louisiana Furry Convention LLC
Summary

RFID provides the foundation for:

• real-time convention awareness
• smoother attendee movement
• scalable event management

It integrates with the LFC backend as a secondary identity layer on top of tickets.
