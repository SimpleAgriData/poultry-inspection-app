import datetime
from enum import StrEnum

from pydantic import BaseModel


class NoteType(StrEnum):
    VACCINATION = "vaccination"
    TREATMENT = "treatment"
    FEEDING = "feeding"
    RELOCATION = "relocation"
    SOCK_TEST = "sock_test"
    OTHER = "other"
    SLAUGHTER = "slaughter"
    CATCHING = "catching"

    def to_label(self) -> str:
        labels: dict["NoteType", str] = {
            NoteType.VACCINATION: "Impfung",
            NoteType.TREATMENT: "Behandlung",
            NoteType.FEEDING: "Fütterung",
            NoteType.RELOCATION: "Umstallung",
            NoteType.SOCK_TEST: "Sockenprobe",
            NoteType.OTHER: "Sonstiges",
            NoteType.SLAUGHTER: "Schlachtung",
            NoteType.CATCHING: "Fangen",
        }
        return labels[self]


class VaccinationCode(StrEnum):
    ND = "nd"
    GUMBORO = "gumboro"
    IB = "ib"
    KOKZIDIEN = "kokzidien"


class TreatmentCode(StrEnum):
    AMPROLINE = "amproline"
    PYANOSID = "pyanosid"
    LINCOSPECTIN = "lincospectin"
    PHENOXYPEN_WSP = "phenoxypen_wsp"
    BAYTRIL = "baytril"
    LANFLOX = "lanflox"
    AMOXICILLIN = "amoxicillin"
    AVIAPEN = "aviapen"
    BAYCOX = "baycox"
    BIOCILLIN = "biocillin"
    DOZURIL = "dozuril"
    ENRO_SLEECOL = "enro_sleecol"
    ENROXAL = "enroxal"
    NEOMYCINSULFAT = "neomycinsulfat"
    OCTACILLIN = "octacillin"
    PAROFOR = "parofor"
    PHARMASIN = "pharmasin"
    RHEMOX_FORTE = "rhemox_forte"
    SOLOMOCTA = "solomocta"
    T_S_SOL = "t_s_sol"
    TOLTRA_K = "toltra_k"


class WaitingTimeUnit(StrEnum):
    DAY = "day"
    WEEK = "week"


class TreatmentAmountUnit(StrEnum):
    L_PER_1000 = "l/1000"
    G_PER_1000 = "g/1000"
    ML = "ml"
    MG = "mg"
    L = "l"
    KG = "kg"


class SockTestResult(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class NoteEntry(BaseModel):
    id: str
    note_type: NoteType
    note_text: str | None = None
    delivery_receipt_number: str | None = None
    batch_number: str | None = None
    vaccination_code: VaccinationCode | None = None
    treatment_code: TreatmentCode | None = None
    treatment_amount_value: float | None = None
    treatment_amount_unit: TreatmentAmountUnit | None = None
    treatment_waiting_time_value: int | None = None
    treatment_waiting_time_unit: WaitingTimeUnit | None = None
    sock_test_result: SockTestResult | None = None
    slaughter_date: datetime.date | None = None
    slaughter_animals_count: int | None = None
    slaughter_final_weight_kg: float | None = None
    slaughterer_name: str | None = None
    catching_time: str | None = None
    catcher_name: str | None = None
