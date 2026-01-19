from flask import Blueprint, render_template, request, send_file
from blueprints.auth.routes import login_required
from services.floor_docx_service import build_floor_docx
from services.floor_pdf_service import build_floor_pdf
from utils.floor import normalize_floor
from services.nutrition_stats_service import (
    get_nutrition_stats_grouped_by_floor
)

bp = Blueprint("stats", __name__, url_prefix="/stats")



@bp.route("/nutrition", methods=["GET"])
def nutrition_stats():
    stats = get_nutrition_stats_grouped_by_floor()
    return render_template("stats/nutrition.html", stats=stats)


@bp.route("/pietro/<floor>/docx", methods=["POST"])
@login_required
def floor_docx(floor):

    floor_key = normalize_floor(floor)
    if floor_key is None:
        return "Nieprawidłowe piętro", 400

    path = build_floor_docx(floor_key)

    return send_file(
        path,
        as_attachment=True,
        download_name=f"PIETRO_{floor}.docx"
    )

@bp.route("/pietro/<floor>/pdf", methods=["POST"])
@login_required
def generate_floor_pdf(floor):

    floor_key = normalize_floor(floor)
    if floor_key is None:
        return "Nieprawidłowe piętro", 400

    path = build_floor_pdf(floor_key)

    return send_file(
        path,
        as_attachment=True,
        download_name=f"PIETRO_{floor}.pdf"
    )

