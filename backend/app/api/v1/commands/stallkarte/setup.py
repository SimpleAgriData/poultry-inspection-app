from fastapi import HTTPException

from app import domain
from app.services.database import Database


def setup_stallkarte(
    db: Database,
    owner_id: str,
    stallkarte_id: int,
) -> tuple[domain.Stallkarte, domain.AgriculturalHolding]:
    holding = db.agricultural_holding_repository.get_holding_by_owner(owner_id)
    if holding is None:
        raise HTTPException(400, "user has no associated agricultural holding")

    stallkarte = db.stallkarte_repository.get_stallkarte_by_id(stallkarte_id)
    if stallkarte is None:
        raise HTTPException(404, f"stallkarte ID '{stallkarte_id}' not found")

    if stallkarte.holding_id != holding.id:
        raise HTTPException(
            403,
            f"stallkarte ID '{stallkarte_id}' does not belong to the user's holding",
        )

    return stallkarte, holding
