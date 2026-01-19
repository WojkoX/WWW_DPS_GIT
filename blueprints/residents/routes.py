from flask import render_template, request, redirect, url_for, flash, session, current_app
from models.resident import Resident
from models.user import db
from models.diet import Diet
from models.resident_diet import ResidentDiet
from blueprints.residents import residents_bp
from functools import wraps
from datetime import datetime
import locale
from math import ceil





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
# LISTA MIESZKAŃCÓW
# =====================
@residents_bp.route('/')
@login_required
def list_residents():
    page = request.args.get('page', 1, type=int)
    floor = request.args.get('floor')
    active = request.args.get('active')

    # NORMALIZACJA
    if active not in ('0', '1'):
        active = ''
    if floor == '':
        floor = None

    query = Resident.query

    if floor is not None:
        query = query.filter_by(floor=int(floor))

    if active == '1':
        query = query.filter_by(is_active=True)
    elif active == '0':
        query = query.filter_by(is_active=False)

    # ====== GLOBALNE SORTOWANIE PL (SQLITE) ======
    try:
        locale.setlocale(locale.LC_COLLATE, 'pl_PL.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_COLLATE, 'Polish_Poland.1250')

    all_items = query.all()

    all_items.sort(
        key=lambda r: locale.strxfrm(r.last_name)
    )

    # ====== RĘCZNA PAGINACJA ======
    per_page = current_app.config['ITEMS_PER_PAGE']
    total = len(all_items)
    pages = max(1, ceil(total / per_page))

    if page < 1:
        page = 1
    if page > pages:
        page = pages

    start = (page - 1) * per_page
    end = start + per_page
    items = all_items[start:end]

    # FAKE Pagination object (tylko to, co potrzebujesz)
    class Pagination:
        def __init__(self, items, page, pages):
            self.items = items
            self.page = page
            self.pages = pages
            self.has_prev = page > 1
            self.has_next = page < pages
            self.prev_num = page - 1
            self.next_num = page + 1

    residents = Pagination(items, page, pages)

    # Liczba aktywnych i nieaktywnych rezydentów
    active_count = Resident.query.filter_by(is_active=True).count()
    inactive_count = Resident.query.filter_by(is_active=False).count()

    return render_template(
        'residents/list.html',
        residents=residents,
        floor=floor,
        active=active,
        active_count=active_count,
        inactive_count=inactive_count
    )


# =====================
# DODAJ MIESZKAŃCA
# =====================
@residents_bp.route('/nowy', methods=['GET', 'POST'])
@login_required
def add_resident():
    if request.method == 'POST':
        room = request.form['room_number'].strip()

        # automatyczne wyliczenie piętra
        try:
            floor = get_floor_from_room(room)
        except ValueError:
            flash('Nieprawidłowy numer pokoju', 'danger')
            return redirect(url_for('residents.add_resident'))

        resident = Resident(
            last_name=request.form['last_name'].upper(),
            first_name=request.form['first_name'],
            room_number=room,
            floor=floor,
            notes=request.form.get('notes'),
            is_hospital=bool(request.form.get('is_hospital')),
            is_pass=bool(request.form.get('is_pass')),
            is_active=bool(request.form.get('is_active'))
        )

        db.session.add(resident)
        db.session.commit()

        flash('Dodano mieszkańca', 'success')
        return redirect(url_for('residents.list_residents'))

    return render_template('residents/form.html', resident=None)


# =====================
# EDYCJA MIESZKAŃCA
# =====================
@residents_bp.route('/<int:resident_id>/edytuj', methods=['GET', 'POST'])
@login_required
def edit_resident(resident_id):
    resident = Resident.query.get_or_404(resident_id)

    if request.method == 'POST':
        room = request.form['room_number'].strip()

        try:
              floor = get_floor_from_room(room)
       
       
        except ValueError:
            flash('Nieprawidłowy numer pokoju', 'danger')
            return redirect(url_for('residents.edit_resident', resident_id=resident.id))

        resident.last_name = request.form['last_name'].upper()
        resident.first_name = request.form['first_name'].upper()
        resident.room_number = room
        resident.floor = floor
        resident.notes = request.form.get('notes')
        resident.is_hospital = bool(request.form.get('is_hospital'))
        resident.is_pass = bool(request.form.get('is_pass'))
        resident.is_active = bool(request.form.get('is_active'))

        db.session.commit()
        flash('Zapisano zmiany', 'success')
        return redirect(url_for('residents.list_residents'))

    return render_template('residents/form.html', resident=resident)

# =====================
# PRZYPISANIE DIETY – WIDOK
# =====================
@residents_bp.route('/<int:resident_id>/dieta', methods=['GET'])
@login_required
def assign_diet(resident_id):
    resident = Resident.query.get_or_404(resident_id)

    diets = Diet.query.filter_by(active=True).order_by(Diet.name).all()

    current_diet = ResidentDiet.query.filter_by(
        resident_id=resident.id
    ).first()

    return render_template(
        'residents/_diet_form.html',
        resident=resident,
        diets=diets,
        diet=current_diet
    )




# =====================
# PRZYPISANIE DIETY – ZAPIS
# =====================
@residents_bp.route('/<int:resident_id>/dieta', methods=['POST'])
@login_required
def save_diet(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    
    diet_id = request.form.get('diet_id')
    diet_name = (diet := Diet.query.get(request.form.get('diet_id', type=int))) and diet.name

    if not diet_id:
        flash('Nie wybrano diety', 'danger')
        return redirect(
            url_for('residents.assign_diet', resident_id=resident.id)
        )

    breakfast = bool(request.form.get('breakfast'))
    lunch = bool(request.form.get('lunch'))
    dinner = bool(request.form.get('dinner'))
    notes = request.form.get('notes', '').strip()

    # usuwamy poprzednią dietę (1:1)
    ResidentDiet.query.filter_by(
        resident_id=resident.id
    ).delete()

    rd = ResidentDiet(
        resident_id=resident.id,
        diet_id=int(diet_id),
        breakfast=breakfast,
        lunch=lunch,
        dinner=dinner
    )
    db.session.add(rd)

    # aktualizacja statusów rezydenta
    resident.has_diet = True
    resident.needs_attention = False
    resident.notes = notes
    resident.updated_at = datetime.utcnow()

    db.session.commit()

    flash('Dieta ' + diet_name +' została przypisana dla ' + resident.last_name + ' ' + resident.first_name + '  (pok.' + resident.room_number +')', 'success')
    return redirect(
     url_for('dashboard.dashboard') + f'?resident_id={resident.id}'    
    # or url_for('dashboard.dashboard', resident_id=resident.id)
    )

@residents_bp.route('/<int:resident_id>/dieta/partial')
@login_required
def diet_partial(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    diets = Diet.query.filter_by(active=True).all()
    current = ResidentDiet.query.filter_by(resident_id=resident.id).first()

    return render_template(
        'residents/_diet_form.html',
        resident=resident,
        diets=diets,
        diet=current
    )





@residents_bp.route('/<int:resident_id>/delete', methods=['POST'])
@login_required
def delete_resident(resident_id):
    resident = Resident.query.get_or_404(resident_id)

    # zabezpieczenie logiczne
    if resident.is_active:
        flash('Nie można usunąć aktywnego mieszkańca.', 'danger')
        return redirect(url_for('residents.edit_resident', resident_id=resident.id))


    full_name = f"{resident.last_name} {resident.first_name}"
    # usunięcie powiązanych diet
    ResidentDiet.query.filter_by(resident_id=resident.id).delete()
    db.session.delete(resident)
    db.session.commit()

    flash('Mieszkaniec ' + full_name + ' i jego diety został trwale usunięty.', 'warning')
    return redirect(url_for('residents.list_residents'))

# ===== Wykonywanie wyszukiwania mieszkańców (AJAX) =====
@residents_bp.route('/search')
@login_required
def search_residents():
    q = request.args.get('q', '').strip()

    query = Resident.query

    if q:
        query = query.filter(
            Resident.last_name.ilike(f"%{q}%")
        )

    residents = query.order_by(Resident.last_name).limit(50).all()

    return render_template(
        'residents/_table_rows.html',
        residents=residents
    )

@residents_bp.route('/<int:resident_id>/diet/detach', methods=['POST'])
@login_required
def detach_diet(resident_id):
    resident = Resident.query.get_or_404(resident_id)

    # usuń dietę
    ResidentDiet.query.filter_by(resident_id=resident.id).delete()

    # przywróć stany domyślne
    resident.has_diet = False
    resident.needs_attention = True

    db.session.commit()

    flash(
        f'Odpięto dietę mieszkańcowi {resident.last_name} {resident.first_name} (Piętro {resident.floor} Pokój {resident.room_number}) ,\n Ustawiono status wymagający uwagi.',
        'warning'
    )

    return redirect(
        url_for('dashboard.dashboard') + f'?resident_id={resident.id}' 
    )

def get_floor_from_room(room: str | int) -> int | None:
    try:
        room_num = int(room)
    except (TypeError, ValueError):
        return None

    if room_num < 0:
        return None

    return room_num // 100
