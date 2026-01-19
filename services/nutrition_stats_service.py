from collections import defaultdict
from flask import current_app
from extensions import db
from models import Resident, ResidentDiet, Diet


MEAL_MAP = {
    "breakfast": "śniadanie",
    "lunch": "obiad",
    "dinner": "kolacja",
}


def _floor_label(floor):
    if floor in (0, None, ""):
        return "PARTER"
    return floor


def _meals_in_room(resident_diet):
    meals = []
    if not resident_diet:
        return meals
    for field, label in MEAL_MAP.items():
        if getattr(resident_diet, field):
            meals.append(label)
    return meals


def _init_summary():
    return {
        "śniadanie": 0,
        "obiad": 0,
        "kolacja": 0,
        "bezmleczna": set(),  # LICZYMY OSOBY
    }


def get_nutrition_stats_grouped_by_floor():

    # =========================================================
    # SŁOWNIK DIET – JEDYNE ŹRÓDŁO KOLEJNOŚCI
    # BRAK = pseudo-dieta (jawnie dodana)
    # =========================================================
    all_diets = ["BRAK"] + [
        d.name
        for d in db.session.query(Diet)
        .order_by(Diet.sort_order, Diet.name)
        .all()
    ]

    rows = (
        db.session.query(Resident, ResidentDiet, Diet)
        .outerjoin(
            ResidentDiet,
            ResidentDiet.resident_id == Resident.id
        )
        .outerjoin(
            Diet,
            Diet.id == ResidentDiet.diet_id
        )
        .filter(Resident.is_active == 1)
        .all()
    )

    floors = defaultdict(lambda: {
        "present_residents": [],
        "summary_eat_in_room": defaultdict(_init_summary),
        "summary_all_present": defaultdict(_init_summary),
        "presence_summary": {
            "total": 0,
            "hospital": 0,
            "pass": 0,
        },
    })

    # =========================================================
    # GŁÓWNA PĘTLA – ZLICZANIE
    # =========================================================
    for resident, resident_diet, diet in rows:

        # ✅ NAJPIERW ustalamy piętro
        floor = _floor_label(resident.floor)

        # -----------------------------------------------------
        # STATYSTYKA OBECNOŚCI (LICZYMY ZAWSZE)
        # -----------------------------------------------------
        floors[floor]["presence_summary"]["total"] += 1

        if resident.is_hospital:
            floors[floor]["presence_summary"]["hospital"] += 1

        if resident.is_pass:
            floors[floor]["presence_summary"]["pass"] += 1

        # -----------------------------------------------------
        # NIEOBECNI: NIE BIORĄ UDZIAŁU W ŻYWIENIU
        # -----------------------------------------------------
        if resident.is_hospital or resident.is_pass:
            continue

        meals = _meals_in_room(resident_diet)
        eat_in_room = bool(meals)

        diet_name = diet.name if diet else "BRAK"
        is_milk_free = bool(diet.is_milk_free) if diet else False

        floors[floor]["present_residents"].append({
            "room": resident.room_number,
            "last_name": resident.last_name,
            "first_name": resident.first_name,
            "name": f"{resident.last_name} {resident.first_name}",
            "diet": diet_name,
            "meals": meals,
            "eat_in_room": eat_in_room,
            "notes": resident.notes or "",
        })

        # -----------------------------------------------------
        # TABELA 2: WSZYSCY OBECNI (DO WYŻYWIENIA)
        # -----------------------------------------------------
        for meal in ("śniadanie", "obiad", "kolacja"):
            floors[floor]["summary_all_present"][diet_name][meal] += 1

        if is_milk_free:
            floors[floor]["summary_all_present"][diet_name]["bezmleczna"].add(
                resident.id
            )

        # -----------------------------------------------------
        # TABELA 1: JEDZĄCY W POKOJACH
        # -----------------------------------------------------
        if eat_in_room:
            for meal in meals:
                floors[floor]["summary_eat_in_room"][diet_name][meal] += 1

            if is_milk_free:
                floors[floor]["summary_eat_in_room"][diet_name]["bezmleczna"].add(
                    resident.id
                )

    # =========================================================
    # OPCJONALNIE: POKAZUJ WSZYSTKIE DIETY ZE SŁOWNIKA
    # =========================================================
    if current_app.config.get("ALL_DIETS_IN_SUMMARY", False):
        for floor_data in floors.values():
            for diet_name in all_diets:
                floor_data["summary_all_present"].setdefault(
                    diet_name, _init_summary()
                )
                floor_data["summary_eat_in_room"].setdefault(
                    diet_name, _init_summary()
                )

    # =========================================================
    # SORT + LP (LISTA MIESZKAŃCÓW)
    # =========================================================
    for floor_data in floors.values():
        floor_data["present_residents"].sort(
            key=lambda r: (
                int(r["room"]) if str(r["room"]).isdigit() else 9999,
                r["last_name"],
                r["first_name"],
            )
        )
        for idx, r in enumerate(floor_data["present_residents"], start=1):
            r["lp"] = idx

    # =========================================================
    # KONWERSJA SET → INT (BEZMLECZNA)
    # =========================================================
    for floor_data in floors.values():
        for summary in ("summary_all_present", "summary_eat_in_room"):
            for diet_data in floor_data[summary].values():
                diet_data["bezmleczna"] = len(diet_data["bezmleczna"])

    # =========================================================
    # WYMUŚ KOLEJNOŚĆ DIET WG sort_order (+ BRAK)
    # =========================================================
    for floor_data in floors.values():
        for key in ("summary_all_present", "summary_eat_in_room"):
            ordered = {}
            for diet_name in all_diets:
                if diet_name in floor_data[key]:
                    ordered[diet_name] = floor_data[key][diet_name]
            floor_data[key] = ordered

    return dict(floors)
