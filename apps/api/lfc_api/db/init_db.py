from lfc_api.db.session import engine
from lfc_api.models.base import Base

# Import all model modules so Base.metadata knows every table
import lfc_api.models.user
import lfc_api.models.event
import lfc_api.models.ticketing

try:
    import lfc_api.models.ledger
except Exception:
    pass


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
