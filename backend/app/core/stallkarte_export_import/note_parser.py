from __future__ import annotations

import re
import uuid

from app.domain.stallkarte.events import models


def parse_general_notes(value: str | None) -> list[models.NoteEntry]:
    if value is None or value.strip() == "":
        return []

    notes: list[models.NoteEntry] = []
    for line in value.replace("\r\n", "\n").split("\n"):
        line = line.strip()
        if not line:
            continue

        line_notes = _parse_general_note_line(line)
        if len(line_notes) > 1:
            notes.append(
                _build_note_entry(
                    models.NoteType.OTHER,
                    f"Original Bemerkung zur Überprüfung: {line}",
                )
            )

        notes.extend(line_notes)

    return notes


def _parse_general_note_line(value: str) -> list[models.NoteEntry]:
    fragments: list[str] = []

    fragments.extend(_split_on_slashes(value))

    expanded_fragments: list[str] = []
    for fragment in fragments:
        expanded_fragments.extend(_split_on_commas(fragment))

    parsed_notes: list[models.NoteEntry] = []
    for fragment in [
        fragment.strip() for fragment in expanded_fragments if fragment.strip()
    ]:
        parsed_notes.extend(_parse_general_note_fragment(fragment))

    return parsed_notes


def _split_on_slashes(value: str) -> list[str]:
    fragments: list[str] = []
    current: list[str] = []
    index = 0

    while index < len(value):
        character = value[index]
        if character == "/" and _should_split_on_slash(value, index):
            fragment = "".join(current).strip()
            if fragment:
                fragments.append(fragment)
            current = []
            index += 1
            continue

        current.append(character)
        index += 1

    fragment = "".join(current).strip()
    if fragment:
        fragments.append(fragment)

    return fragments


def _should_split_on_slash(value: str, index: int) -> bool:
    left_index = index - 1
    while left_index >= 0 and value[left_index].isspace():
        left_index -= 1

    right_index = index + 1
    while right_index < len(value) and value[right_index].isspace():
        right_index += 1

    if right_index >= len(value):
        return False

    right_character = value[right_index]
    left_character = value[left_index] if left_index >= 0 else ""

    if right_character.isdigit():
        return False

    if left_character.isdigit() and right_character.isdigit():
        return False

    return right_character.isalpha() or right_character == "<"


def _split_on_commas(value: str) -> list[str]:
    if "," not in value:
        return [value]

    fragments = re.split(r"(?<!\d),\s*(?=\d|[A-Za-zÄÖÜäöü<])", value)
    return [fragment for fragment in fragments if fragment.strip()]


def _parse_general_note_fragment(fragment: str) -> list[models.NoteEntry]:
    fragment = fragment.strip().strip("-")
    if not fragment:
        return []

    if "+" in fragment:
        parts = [part.strip() for part in re.split(r"\s*\+\s*", fragment) if part.strip()]
        if len(parts) > 1:
            notes: list[models.NoteEntry] = []
            for part in parts:
                notes.extend(_parse_general_note_fragment(part))
            return notes

    explicit_type, explicit_payload = _parse_explicit_note_type(fragment)
    if explicit_type is not None:
        return _build_note_entries_from_explicit_type(explicit_type, explicit_payload)

    if _looks_like_relocation(fragment):
        relocation, remainder = _split_after_marker(fragment, ("umstallung",))
        notes = [_build_note_entry(models.NoteType.RELOCATION, relocation)]
        if remainder:
            notes.extend(_parse_general_note_fragment(remainder))
        return notes

    if _contains_vaccination_marker(fragment):
        split_fragment = _split_feeding_and_vaccination_fragment(fragment)
        if split_fragment is not None:
            feeding_part, vaccination_part = split_fragment
            notes: list[models.NoteEntry] = []
            if feeding_part.strip():
                notes.extend(_parse_general_note_fragment(feeding_part))
            if vaccination_part.strip():
                notes.extend(_parse_general_note_fragment(vaccination_part))
            return notes

        return _build_vaccination_entries(fragment)

    if _looks_like_feeding(fragment):
        return [_build_note_entry(models.NoteType.FEEDING, fragment)]

    if _contains_treatment_marker(fragment):
        return [_build_treatment_entry(fragment)]

    return [_build_note_entry(models.NoteType.OTHER, fragment)]


def _parse_explicit_note_type(fragment: str) -> tuple[models.NoteType | None, str]:
    match = re.match(r"^\s*(?P<label>[^-:]+?)\s*(?:-|:)\s*(?P<payload>.+)$", fragment)
    if match is None:
        return None, fragment

    label = match.group("label").strip()
    payload = match.group("payload").strip()
    note_type = _note_type_from_label(label)
    if note_type is None:
        return None, fragment

    return note_type, payload


def _note_type_from_label(label: str) -> models.NoteType | None:
    normalized_label = label.strip().lower()
    normalized_label = normalized_label.replace("ü", "ue")
    normalized_label = normalized_label.replace("ä", "ae")
    normalized_label = normalized_label.replace("ö", "oe")

    label_map: dict[str, models.NoteType] = {
        "impfung": models.NoteType.VACCINATION,
        "vaccination": models.NoteType.VACCINATION,
        "behandlung": models.NoteType.TREATMENT,
        "futterung": models.NoteType.FEEDING,
        "fuetterung": models.NoteType.FEEDING,
        "futter": models.NoteType.FEEDING,
        "futterumstellung": models.NoteType.FEEDING,
        "umstallung": models.NoteType.RELOCATION,
        "sonstiges": models.NoteType.OTHER,
        "sockenprobe": models.NoteType.SOCK_TEST,
        "schlachtung": models.NoteType.SLAUGHTER,
        "fangen": models.NoteType.CATCHING,
    }

    return label_map.get(normalized_label)


def _build_note_entries_from_explicit_type(
    note_type: models.NoteType,
    payload: str,
) -> list[models.NoteEntry]:
    if note_type == models.NoteType.VACCINATION:
        return _build_vaccination_entries(payload)

    if note_type == models.NoteType.TREATMENT:
        return [_build_treatment_entry(payload)]

    return [_build_note_entry(note_type, payload)]


def _build_vaccination_entries(fragment: str) -> list[models.NoteEntry]:
    pieces = [
        piece.strip() for piece in re.split(r"\s*\+\s*", fragment) if piece.strip()
    ]
    if not pieces:
        pieces = [fragment.strip()]

    notes: list[models.NoteEntry] = []
    for piece in pieces:
        code, note_text = _extract_vaccination_code_and_text(piece)
        notes.append(
            _build_note_entry(
                models.NoteType.VACCINATION,
                note_text,
                vaccination_code=code,
            )
        )

    return notes


def _extract_vaccination_code_and_text(
    fragment: str,
) -> tuple[models.VaccinationCode | None, str | None]:
    code_patterns: list[tuple[models.VaccinationCode, str]] = [
        (models.VaccinationCode.ND, r"\bnd\b"),
        (models.VaccinationCode.GUMBORO, r"\bgumboro\b"),
        (models.VaccinationCode.IB, r"\b(?:ib|iib)\b|<ib\b"),
        (models.VaccinationCode.KOKZIDIEN, r"\bkokzidien\b"),
    ]

    working_fragment = fragment.strip()
    code: models.VaccinationCode | None = None

    for vaccination_code, pattern in code_patterns:
        if re.search(pattern, working_fragment, flags=re.IGNORECASE) is None:
            continue

        code = vaccination_code
        working_fragment = re.sub(
            pattern, " ", working_fragment, flags=re.IGNORECASE
        ).strip()
        break

    note_text = working_fragment.strip(" -+/") or None
    if note_text is not None:
        normalized_note_text = note_text.strip().lower()
        if normalized_note_text == "impfung":
            note_text = None

    return code, note_text


def _looks_like_relocation(fragment: str) -> bool:
    return re.search(r"\bumstallung\b", fragment, flags=re.IGNORECASE) is not None


def _looks_like_feeding(fragment: str) -> bool:
    if re.search(r"\bfutter(?:umstellung|ung)?\b", fragment, flags=re.IGNORECASE):
        return True

    if re.search(r"\bmast\b", fragment, flags=re.IGNORECASE):
        return True

    return re.search(r"\d+\s*%|\d+\s*/\s*\d+", fragment) is not None


def _contains_vaccination_marker(fragment: str) -> bool:
    return (
        re.search(
            r"\b(?:nd|nachimpfung|impfung|gumboro|ib|iib|kokzidien)\b|<ib\b",
            fragment,
            flags=re.IGNORECASE,
        )
        is not None
    )


def _split_feeding_and_vaccination_fragment(fragment: str) -> tuple[str, str] | None:
    feeding_match = re.search(
        r"\bfutter(?:umstellung|ung)?\b|\bmast\b|\d+\s*%|\d+\s*/\s*\d+",
        fragment,
        flags=re.IGNORECASE,
    )
    vaccination_match = re.search(
        r"\b(?:nd|nachimpfung|impfung|gumboro|ib|iib|kokzidien)\b|<ib\b",
        fragment,
        flags=re.IGNORECASE,
    )

    if feeding_match is None or vaccination_match is None:
        return None

    if feeding_match.start() > vaccination_match.start():
        return None

    feeding_part = fragment[: vaccination_match.start()].strip(" -+/")
    vaccination_part = fragment[vaccination_match.start() :].strip()

    if not feeding_part:
        return None

    return feeding_part, vaccination_part


def _contains_treatment_marker(fragment: str) -> bool:
    if re.search(
        r"\b(?:"
        r"amproline|amproliene|pyanosid|lincospectin|"
        r"phenoxypen(?:[_\s-]+)?wsp|"
        r"baytril|lanflox|amoxicillin|aviapen|baycox|biocillin|dozuril|"
        r"enro(?:[-_\s]+)?sleecol|enroxal|neomycinsulfat|octacillin|parofor|pharmasin|"
        r"rhemox(?:[-_\s]+)?forte|solomocta|t(?:[.\s_-]*s[.\s_-]*sol)|toltra(?:[-_\s]+)?k"
        r")\b",
        fragment,
        flags=re.IGNORECASE,
    ):
        return True

    return (
        re.search(
            r"\d+(?:[.,]\d+)?\s*(?:l\s*/\s*1000|g\s*/\s*1000|ml|mg|l|kg)\b",
            fragment,
            flags=re.IGNORECASE,
        )
        is not None
    )


def _split_after_marker(
    fragment: str,
    marker_patterns: tuple[str, ...],
) -> tuple[str, str | None]:
    first_match_start: int | None = None
    first_match_end: int | None = None
    for pattern in marker_patterns:
        match = re.search(pattern, fragment, flags=re.IGNORECASE)
        if match is None:
            continue
        if first_match_start is None or match.start() < first_match_start:
            first_match_start = match.start()
            first_match_end = match.end()

    if first_match_start is None or first_match_end is None:
        return fragment, None

    left = fragment[:first_match_end].strip()
    right = fragment[first_match_end:].strip()
    return left, right


def _normalize_treatment_fragment(fragment: str) -> str:
    fragment = re.sub(r"\s*/\s*1000\b", "/1000", fragment.strip(), flags=re.IGNORECASE)

    code_union = (
        r"amproline|amproliene|pyanosid|lincospectin|"
        r"phenoxypen(?:[_\s-]+)?wsp|"
        r"baytril|lanflox|amoxicillin|aviapen|baycox|biocillin|dozuril|"
        r"enro(?:[-_\s]+)?sleecol|enroxal|neomycinsulfat|octacillin|parofor|pharmasin|"
        r"rhemox(?:[-_\s]+)?forte|solomocta|t(?:[.\s_-]*s[.\s_-]*sol)|toltra(?:[-_\s]+)?k"
    )

    fragment = re.sub(
        rf"(?i)\b(?P<value>\d+(?:[.,]\d+)?)\s*(?P<unit>l|g)\s+(?P<name>(?:{code_union}))\b(?P<suffix>/1000)?",
        lambda m: (
            f"{m.group('value')} {m.group('unit')}/1000 {m.group('name')}"
            if m.group("suffix") is not None
            or m.group("unit").lower() in {"l", "g"}
            else m.group(0)
        ),
        fragment,
    )

    fragment = re.sub(
        rf"(?i)\b(?P<name>(?:{code_union}))\s*/1000\b",
        r"\g<name>",
        fragment,
    )

    return re.sub(r"\s+", " ", fragment).strip()


def _build_treatment_entry(fragment: str) -> models.NoteEntry:
    fragment = _normalize_treatment_fragment(fragment)

    code, remaining_text = _extract_treatment_code_and_text(fragment)
    amount_value, amount_unit, note_text = extract_treatment_amount_and_text(
        remaining_text
    )

    return _build_note_entry(
        models.NoteType.TREATMENT,
        note_text,
        treatment_code=code,
        treatment_amount_value=amount_value,
        treatment_amount_unit=amount_unit,
    )


def _extract_treatment_code_and_text(
    fragment: str,
) -> tuple[models.TreatmentCode | None, str]:
    code_patterns: list[tuple[models.TreatmentCode, str]] = [
        (models.TreatmentCode.AMPROLINE, r"\bamproline\b|\bamproliene\b"),
        (models.TreatmentCode.PYANOSID, r"\bpyanosid\b"),
        (models.TreatmentCode.LINCOSPECTIN, r"\blincospectin\b"),
        (models.TreatmentCode.PHENOXYPEN_WSP, r"\bphenoxypen(?:[_\s-]+)?wsp\b"),
        (models.TreatmentCode.BAYTRIL, r"\bbaytril\b"),
        (models.TreatmentCode.LANFLOX, r"\blanflox\b"),
        (models.TreatmentCode.AMOXICILLIN, r"\bamoxicillin\b"),
        (models.TreatmentCode.AVIAPEN, r"\baviapen\b"),
        (models.TreatmentCode.BAYCOX, r"\bbaycox\b"),
        (models.TreatmentCode.BIOCILLIN, r"\bbiocillin\b"),
        (models.TreatmentCode.DOZURIL, r"\bdozuril\b"),
        (models.TreatmentCode.ENRO_SLEECOL, r"\benro(?:[-_\s]+)?sleecol\b"),
        (models.TreatmentCode.ENROXAL, r"\benroxal\b"),
        (models.TreatmentCode.NEOMYCINSULFAT, r"\bneomycinsulfat\b"),
        (models.TreatmentCode.OCTACILLIN, r"\boctacillin\b"),
        (models.TreatmentCode.PAROFOR, r"\bparofor\b"),
        (models.TreatmentCode.PHARMASIN, r"\bpharmasin\b"),
        (models.TreatmentCode.RHEMOX_FORTE, r"\brhemox(?:[-_\s]+)?forte\b"),
        (models.TreatmentCode.SOLOMOCTA, r"\bsolomocta\b"),
        (models.TreatmentCode.T_S_SOL, r"\bt(?:[.\s_-]*s[.\s_-]*sol)\b"),
        (models.TreatmentCode.TOLTRA_K, r"\btoltra(?:[-_\s]+)?k\b"),
    ]

    working_fragment = fragment.strip()
    code: models.TreatmentCode | None = None

    for treatment_code, pattern in code_patterns:
        if re.search(pattern, working_fragment, flags=re.IGNORECASE) is None:
            continue

        code = treatment_code
        working_fragment = re.sub(
            pattern, " ", working_fragment, flags=re.IGNORECASE
        ).strip()
        break

    return code, working_fragment


def extract_treatment_amount_and_text(
    fragment: str,
) -> tuple[float | None, models.TreatmentAmountUnit | None, str | None]:
    pattern = r"(?P<value>\d+(?:[.,]\d+)?)\s*(?P<unit>l\s*/\s*1000|g\s*/\s*1000|ml|mg|kg|l)\b"

    match = re.search(pattern, fragment, flags=re.IGNORECASE)

    if match is None:
        note_text = fragment.strip(" -+/") or None
        return None, None, note_text

    value = float(match.group("value").replace(",", "."))

    raw_unit = match.group("unit").lower()
    normalized_unit = re.sub(r"\s*/\s*", "/", raw_unit)
    unit = models.TreatmentAmountUnit(normalized_unit)

    note_text = (
        re.sub(pattern, " ", fragment, count=1, flags=re.IGNORECASE).strip(" -+/")
        or None
    )

    return value, unit, note_text


def _build_note_entry(
    note_type: models.NoteType,
    note_text: str | None,
    *,
    vaccination_code: models.VaccinationCode | None = None,
    treatment_code: models.TreatmentCode | None = None,
    treatment_amount_value: float | None = None,
    treatment_amount_unit: models.TreatmentAmountUnit | None = None,
) -> models.NoteEntry:
    return models.NoteEntry(
        id=str(uuid.uuid4()),
        note_type=note_type,
        note_text=note_text,
        vaccination_code=vaccination_code,
        treatment_code=treatment_code,
        treatment_amount_value=treatment_amount_value,
        treatment_amount_unit=treatment_amount_unit,
    )