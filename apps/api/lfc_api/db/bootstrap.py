import uuid

from sqlalchemy.orm import Session

from lfc_api.core.security import hash_password
from lfc_api.db.init_db import init_db
from lfc_api.db.session import SessionLocal
from lfc_api.models.event import ConventionEvent
from lfc_api.models.ticketing import TicketType
from lfc_api.models.user import User


def bootstrap() -> None:
    # Ensure tables exist before querying anything
    init_db()

    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@lfc.local").first()
        if not admin:
            admin = User(
                id=str(uuid.uuid4()),
                email="admin@lfc.local",
                display_name="LFC Admin",
                password_hash=hash_password("admin"),
                role="admin",
                is_active=True,
            )
            db.add(admin)

        event = db.query(ConventionEvent).filter(ConventionEvent.id == "lfc-2027").first()
        if not event:
            event = ConventionEvent(
                id="lfc-2027",
                name="LouisiAnthro 2027",
            )
            db.add(event)

        db.flush()

        defaults = [
            {
                "id": "lfc-2027-early",
                "name": "Early Registration",
                "price_cents": 4500,
                "currency": "USD",
                "is_active": True,
                "is_public": True,
            },
            {
                "id": "lfc-2027-regular",
                "name": "Regular Registration",
                "price_cents": 7000,
                "currency": "USD",
                "is_active": True,
                "is_public": True,
            },
        ]

        for item in defaults:
            tt = db.query(TicketType).filter(TicketType.id == item["id"]).first()
            if not tt:
                tt = TicketType(
                    id=item["id"],
                    event_id="lfc-2027",
                    name=item["name"],
                    price_cents=item["price_cents"],
                    currency=item["currency"],
                    is_active=item["is_active"],
                    is_public=item["is_public"],
                )
                db.add(tt)

        db.commit()
        print("bootstrap complete")
    finally:
        db.close()


if __name__ == "__main__":
    bootstrap()
