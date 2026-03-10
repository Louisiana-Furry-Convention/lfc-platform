import hmac
import hashlib
from lfc_api.core.config import BADGE_SECRET

def sign_ticket(ticket_id: str) -> str:
    sig = hmac.new(
        BADGE_SECRET.encode(),
        ticket_id.encode(),
        hashlib.sha256
    ).hexdigest()[:16]

    return f"{ticket_id}|{sig}"


def verify_ticket(token: str) -> str | None:

    try:
        ticket_id, sig = token.split("|")
    except ValueError:
        return None

    expected = hmac.new(
        BADGE_SECRET.encode(),
        ticket_id.encode(),
        hashlib.sha256
    ).hexdigest()[:16]

    if sig != expected:
        return None

    return ticket_id
