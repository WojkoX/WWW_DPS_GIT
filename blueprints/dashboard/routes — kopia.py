from flask import render_template, session, redirect, url_for, request
from functools import wraps

from models.resident import Resident
from models.resident_diet import ResidentDiet
from blueprints.dashboard import dashboard_bp
from services.dashboard_tree import build_dashboard_tree


# =====================
# OCHRONA – TYLKO ADMIN
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

    tree = build_dashboard_tree()
    resident = None
    diet = None

    if resident_id:
        resident = Resident.query.get_or_404(resident_id)
        diet = ResidentDiet.query.filter_by(resident_id=resident.id).first()

    return render_template(
        'dashboard/dashboard.html',
        tree=tree,
        resident=resident,
        diet=diet
    )

@dashboard_bp.route('/diet/save/<int:resident_id>', methods=['POST'])
@login_required
def save_diet(resident_id):
    resident = Resident.query.get_or_404(resident_id)

    diet_id = request.form.get('diet_id')
    breakfast = bool(request.form.get('breakfast'))
    lunch = bool(request.form.get('lunch'))
    dinner = bool(request.form.get('dinner'))
    notes = request.form.get('notes')

    # usuń starą dietę (1 aktywna na osobę)
    ResidentDiet.query.filter_by(resident_id=resident.id).delete()

    rd = ResidentDiet(
        resident_id=resident.id,
        diet_id=diet_id,
        breakfast=breakfast,
        lunch=lunch,
        dinner=dinner
    )
    db.session.add(rd)

    # statusy rezydenta
    resident.has_diet = True
    resident.needs_attention = False
    resident.updated_at = datetime.utcnow()

    db.session.commit()

    # 🔑 KLUCZOWE: wracamy DO DASHBOARDU z tym samym resident_id
    return redirect(url_for(
        'dashboard.dashboard',
        resident_id=resident.id
    ))