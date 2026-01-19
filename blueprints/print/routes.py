from flask import Blueprint, render_template
from datetime import date
from services.nutrition_stats_service import get_nutrition_stats_grouped_by_floor
from blueprints.auth.routes import login_required
from utils.floor import normalize_floor
bp = Blueprint("print", __name__, url_prefix="/print")



@bp.route("/floor/<floor>")
@login_required
def floor_print(floor):

    stats = get_nutrition_stats_grouped_by_floor()

    # ✅ NORMALIZACJA
    floor_key = normalize_floor(floor)
    if floor_key is None:
        return "Nieprawidłowe piętro", 400

    if floor_key not in stats:
        return "Brak danych", 404

    data = stats[floor_key]
    residents = data["present_residents"]

    # === PODZIAŁ NA DWIE KOLUMNY ===
    rows = build_print_rows(residents)

    return render_template(
        "print/floor_print.html",
        floor=floor,
        today=date.today(),
        presence=data["presence_summary"],
        rows=rows,
        summary_eat=data["summary_eat_in_room"],
        summary_all=data["summary_all_present"],
        )

def build_print_rows(residents):
    rows = []
    half = (len(residents) + 1) // 2

    left = residents[:half]
    right = residents[half:]

    for i in range(half):
        row = []

        # LEWA
        if i < len(left):
            r = left[i]
            row.extend([
                r["lp"],
                r["name"],
                r["room"],
                format_diet(r),
            ])
        else:
            row.extend(["", "", "", ""])

        # PRAWA
        if i < len(right):
            r = right[i]
            row.extend([
                r["lp"],
                r["name"],
                r["room"],
                format_diet(r),
            ])
        else:
            row.extend(["", "", "", ""])

        rows.append(row)

    return rows

def format_diet(r):
    if not r:
        return ""

    text = r["diet"]

    if r.get("meals"):
        text += f"<br>({', '.join(r['meals'])})"

    if r.get("notes"):
        text += f"<br><b>{r['notes']}</b>"

    return text