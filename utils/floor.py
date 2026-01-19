def normalize_floor(floor: str):
    if not floor:
        return None

    if floor.upper() == "PARTER":
        return "PARTER"

    try:
        return int(floor)
    except ValueError:
        return None