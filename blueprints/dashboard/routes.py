from flask import render_template, session, redirect, url_for, request
from functools import wraps
from extensions import db
from datetime import datetime

from blueprints.dashboard import dashboard_bp
from services.dashboard_tree import build_dashboard_tree

from models.resident import Resident
from models.resident_diet import ResidentDiet


# =====================
# OCHRONA – LOGIN
# =====================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


# =====================
# DASHBOARD
# =====================
@dashboard_bp.route('/')
@login_required
def dashboard():
    resident_id = request.args.get('resident_id', type=int)

    # bazowe drzewo (floor -> room -> residents as dict)
    tree = build_dashboard_tree()

    # ==================================================
    # PATCH: UWAGA (!) + SORTOWANIE NUMERYCZNE POKOI
    # ==================================================
    for floor, rooms in tree.items():

        floor_needs_attention = False

        # sortowanie pokoi: 1,2,3,10,11...
        sorted_rooms = dict(
            sorted(
                rooms.items(),
                key=lambda item: int(item[0]) if str(item[0]).isdigit() else item[0]
            )
        )

        for room_number, room in sorted_rooms.items():
            room_needs_attention = False

            for r in room.get("residents", []):
                # r JEST DICTEM
                if not r.get("has_diet", False):
                    room_needs_attention = True
                    floor_needs_attention = True
                    break

            room["needs_attention"] = room_needs_attention

        # flaga na poziomie piętra
        sorted_rooms["_needs_attention"] = floor_needs_attention

        # podmień pokoje na posortowane + wzbogacone
        tree[floor] = sorted_rooms

    # =====================================
    # (opcjonalnie) rehydratacja formularza
    # =====================================
    resident = None
    diet = None

    if resident_id:
        resident = Resident.query.get_or_404(resident_id)
        diet = ResidentDiet.query.filter_by(resident_id=resident.id).first()

    return render_template(
        "dashboard/dashboard.html",
        tree=tree,
        resident=resident,
        diet=diet
    )
