# LFC Platform

LFC Platform is the convention operations backbone for Louisiana Furry Convention, LLC.

It is designed to support:

- attendee registration and ticketing
- attendee badge and QR presentation
- staff/admin check-in operations
- live arrivals and lane analytics
- admin database visibility
- future website/API integration with WordPress

## Current Release

**Version:** `v0.1.2-beta`

## Core Capabilities

### Attendee Features
- account signup and login
- public ticket tier listing
- ticket purchase scaffold
- My Tickets view
- My Badge full-screen QR display
- QR badge PNG rendering

### Staff Features
- camera-based QR scanning
- manual QR token check-in
- duplicate prevention
- recent scan history

### Admin / Operations Features
- admin dashboard
- live arrivals feed
- lane analytics
- surge detection
- tier breakdown
- user role promotion
- admin DB viewer

## Architecture

LFC Platform is intended to operate as a separate application/API from the public website.

Recommended structure:

- `www.example.com` → WordPress public website
- `app.example.com` → LFC attendee/staff/admin app
- `api.example.com` → LFC backend API

WordPress should act as the public-facing content site, while LFC Platform handles:
- auth
- tickets
- orders
- QR badge delivery
- check-in
- analytics
- admin tools

## Tech Stack

- FastAPI
- SQLAlchemy
- SQLite (edge/dev)
- Static web frontend served by API host
- QR generation for attendee badges

## Current Status

`v0.1.2-beta` delivers a working end-to-end prototype for:

- login
- ticket access
- QR badge display
- door scanning
- check-in tracking
- admin analytics

## Planned Next Work

### v0.1.3
- payment/order lifecycle redesign
- stronger public purchase flow
- ticket status polish
- website integration refinement
- scanner workflow polish
- admin UI cleanup

## Development Branches

- `main` → stable release branch
- `dev-0.1.2` → development branch for v0.1.2 work

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
