import os
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from datetime import datetime
from blueprints.import_csv import import_csv_bp
from services.csv_importer import import_csv

UPLOAD_DIR = 'uploads'


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def get_csv_files():
    '''
    Zwraca listę plików CSV z folderu uploads z informacjami.
    '''
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    files = []
    
    for filename in os.listdir(UPLOAD_DIR):
        if filename.lower().endswith('.csv'):
            filepath = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
    
    # Sortuj po dacie (najnowsze pierwsze)
    files.sort(key=lambda x: x['date'], reverse=True)
    return files


@import_csv_bp.route('/', methods=['GET', 'POST'])
@login_required
def upload_csv():
    if request.method == 'POST':
        file = request.files.get('file')

        if not file or not file.filename.lower().endswith('.csv'):
            flash('Nieprawidłowy plik CSV', 'danger')
            return redirect(url_for('import_csv.upload_csv'))

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Dodaj datę i czas do nazwy pliku
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        name_parts = file.filename.rsplit('.', 1)
        new_filename = f"IMPORT_{timestamp}.{name_parts[1]}"
        path = os.path.join(UPLOAD_DIR, new_filename)
        file.save(path)

        import_csv(path)

        result = import_csv(path)
        
        # Przygotowanie flash message z informacjami o imporcie
        file_count = result['file_count'] if result['file_count'] else '?'
        active_count = result['active_count']
        inactive_count = result['inactive_count']

        message = f'Deklaracja osób w pliku: {file_count}, Aktywnych osób: {active_count}, Nieaktywnych osób: {inactive_count}'
        flash(message, 'success')

        # Wyrzuć warning jeśli liczba rekordów się nie zgadza
        if result.get('warning'):
            flash(result['warning'], 'danger')

        flash('Import CSV zakończony pomyślnie', 'success')
        return redirect(url_for('residents.list_residents'))

    # Pobierz listę plików CSV
    csv_files = get_csv_files()
    return render_template('import/upload.html', csv_files=csv_files)


@import_csv_bp.route('/import/<filename>', methods=['POST'])
@login_required
def import_existing_file(filename):
    '''
    Importuje istniejący plik CSV z folderu uploads.
    '''
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Walidacja bezpieczeństwa
    if not os.path.abspath(filepath).startswith(os.path.abspath(UPLOAD_DIR)):
        flash('Nieprawidłowa ścieżka pliku', 'danger')
        return redirect(url_for('import_csv.upload_csv'))
    
    if not os.path.exists(filepath) or not filepath.lower().endswith('.csv'):
        flash('Plik nie istnieje', 'danger')
        return redirect(url_for('import_csv.upload_csv'))
    
    # Import pliku
    result = import_csv(filepath)
    
    # Przygotowanie flash message z informacjami o imporcie
    file_count = result['file_count'] if result['file_count'] else '?'
    active_count = result['active_count']
    inactive_count = result['inactive_count']

    message = f'Deklaracja osób w pliku: {file_count}, Aktywnych osób: {active_count}, Nieaktywnych osób: {inactive_count}'
    flash(message, 'success')

    # Wyrzuć warning jeśli liczba rekordów się nie zgadza
    if result.get('warning'):
        flash(result['warning'], 'danger')

    flash('Import CSV zakończony pomyślnie', 'success')
    return redirect(url_for('residents.list_residents'))


@import_csv_bp.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    '''
    Usuwa plik CSV z folderu uploads.
    '''
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Walidacja bezpieczeństwa
    if not os.path.abspath(filepath).startswith(os.path.abspath(UPLOAD_DIR)):
        flash('Nieprawidłowa ścieżka pliku', 'danger')
        return redirect(url_for('import_csv.upload_csv'))
    
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            flash(f'Plik {filename} został usunięty', 'success')
        else:
            flash('Plik nie istnieje', 'warning')
    except Exception as e:
        flash(f'Błąd przy usuwaniu pliku: {str(e)}', 'danger')
    
    return redirect(url_for('import_csv.upload_csv'))
