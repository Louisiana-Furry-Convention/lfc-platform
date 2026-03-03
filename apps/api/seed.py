import uuid
import secrets
from lfc_api.db.session import SessionLocal
from lfc_api.models.event import ConventionEvent
from lfc_api.models.ticketing import TicketType

db = SessionLocal()

event_id = "lfc-2027"
event_name = "Louisiana Furry Convention 2027"

if not db.query(ConventionEvent).filter(ConventionEvent.id == event_id).first():
    db.add(ConventionEvent(id=event_id, name=event_name))

tiers = [
    ("lfc-2027-early", "Early Registration", 4500),
    ("lfc-2027-regular", "Regular Registration", 6000),
    ("lfc-2027-supporter", "Supporter Registration", 8000),
    ("lfc-2027-gold", "Gold Registration", 10000),
    ("lfc-2027-ultimate", "Ultimate Registration", 15000),
]

for tid, name, price in tiers:
    if not db.query(TicketType).filter(TicketType.id == tid).first():
        db.add(TicketType(id=tid, event_id=event_id, name=name, price_cents=price, currency="USD"))

db.commit()
db.close()
print("Seeded baseline event and ticket types.")
