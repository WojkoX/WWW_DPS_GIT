from flask import render_template, request, redirect, url_for, flash, session
from blueprints.auth.routes import login_required
from models.diet import Diet
from models.user import db
from blueprints.diets import diets_bp
from functools import wraps
from flask import current_app




# =====================
# LISTA DIET
# =====================
@diets_bp.route('/')
@login_required
def list_diets():
    page = request.args.get('page', 1, type=int)

    diets = Diet.query.order_by(
          Diet.sort_order,
          Diet.name
    ).paginate(
          page=page,
          per_page=current_app.config['ITEMS_PER_PAGE'],
          error_out=False
    )


    return render_template(
        'diets/list.html',
        diets=diets
    )


# =====================
# DODAJ DIETĘ
# =====================
@diets_bp.route('/nowa', methods=['GET', 'POST'])
@login_required
def add_diet():
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code'].upper()
        notes = request.form['notes']
        sort_order = int(request.form.get('sort_order', 0))


        if Diet.query.filter_by(code=code).first():
            flash('Dieta o takim kodzie już istnieje', 'danger')
            return redirect(url_for('diets.add_diet'))

        diet = Diet(
            name=name,
            code=code,
            is_basic=bool(request.form.get('is_basic')),
            is_light=bool(request.form.get('is_light')),
            is_diabetes=bool(request.form.get('is_diabetes')),
            is_milk_free=bool(request.form.get('is_milk_free')),
            is_mix=bool(request.form.get('is_mix')),
            is_peg=bool(request.form.get('is_peg')),
            is_restrictive=bool(request.form.get('is_restrictive')),
            active=bool(request.form.get('active')),
            notes=notes,
            sort_order=sort_order
        )

        db.session.add(diet)
        db.session.commit()

        flash('Dodano dietę', 'success')
        return redirect(url_for('diets.list_diets'))

    return render_template('diets/form.html', diet=None)


# =====================
# EDYCJA DIETY
# =====================
@diets_bp.route('/<int:diet_id>/edytuj', methods=['GET', 'POST'])
@login_required
def edit_diet(diet_id):
    diet = Diet.query.get_or_404(diet_id)

    if request.method == 'POST':
        diet.name = request.form['name']
        diet.code = request.form['code'].upper()
        diet.notes = request.form['notes']
        diet.sort_order = int(request.form.get('sort_order', 0))

        diet.is_basic = bool(request.form.get('is_basic'))
        diet.is_light = bool(request.form.get('is_light'))
        diet.is_diabetes = bool(request.form.get('is_diabetes'))
        diet.is_milk_free = bool(request.form.get('is_milk_free'))
        diet.is_mix = bool(request.form.get('is_mix'))
        diet.is_peg = bool(request.form.get('is_peg'))
        diet.is_restrictive = bool(request.form.get('is_restrictive'))
        diet.active = bool(request.form.get('active'))

        db.session.commit()
        flash('Zapisano zmiany', 'success')
        return redirect(url_for('diets.list_diets'))

    return render_template('diets/form.html', diet=diet)
