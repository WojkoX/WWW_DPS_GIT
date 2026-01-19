import csv
import io
from datetime import datetime

from models.resident import Resident
from models.diet import Diet
from models.resident_diet import ResidentDiet
from models.user import db


# =====================================================
# POMOCNICZE
# =====================================================

def normalize_header(h: str) -> str:
    return h.replace('\ufeff', '').strip().lower()


def detect_floor(room: str) -> int:
    room = room.upper().replace(' ', '')
    num = ''
    for c in room:
        if c.isdigit():
            num += c
        else:
            break
    if not num:
        return 0
    n = int(num)
    return 0 if n < 100 else n // 100


def parse_diet_text(text: str):
    t = text.upper()
    return {
        'is_basic': 'PODSTAW' in t,
        'is_light': 'LEKKO' in t,
        'is_diabetes': 'CUKR' in t,
        'is_milk_free': 'BEZMLE' in t or 'BEZ MLE' in t,
        'is_mix': 'MIX' in t,
        'is_peg': 'PEG' in t or 'SONDA' in t,
        'is_restrictive': 'RESTR' in t
    }


def parse_meals(text: str):
    t = text.lower()
    return {
        'breakfast': 'śniad' in t,
        'lunch': 'obiad' in t,
        'dinner': 'kolac' in t
    }


def find_or_create_diet(diet_text: str):
    flags = parse_diet_text(diet_text)

    for d in Diet.query.filter_by(active=True).all():
        if (
            d.is_basic == flags['is_basic'] and
            d.is_light == flags['is_light'] and
            d.is_diabetes == flags['is_diabetes'] and
            d.is_milk_free == flags['is_milk_free'] and
            d.is_mix == flags['is_mix'] and
            d.is_peg == flags['is_peg'] and
            d.is_restrictive == flags['is_restrictive']
        ):
            return d

    diet = Diet(
        name=diet_text.strip(),
        code=f"AUTO_{Diet.query.count() + 1}",
        **flags
    )
    db.session.add(diet)
    db.session.flush()
    return diet


# =====================================================
# IMPORT CSV – LINIOWY (RAPORTOWY)
# =====================================================

def import_csv(filepath: str):
    seen_keys = set()
    file_record_count = 0
    processed_record_count = 0

    # --- 1. CZYTAMY BAJTY ---
    with open(filepath, 'rb') as bf:
        raw = bf.read()

    # --- 2. DEKODOWANIE ---
    for enc in ('utf-8-sig', 'cp1250', 'latin-1'):
        try:
            text = raw.decode(enc)
            print(f"[CSV] Kodowanie: {enc}")
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Nieznane kodowanie CSV")

    lines = text.splitlines()

    # --- 3. PARSOWANIE LINIOWE ---
    for line in lines:
        line = line.strip()

        if not line:
            continue

        # pobieramy liczbę z linii "Suma rekordów :129"
        if 'SUMA' in line.upper() and 'REKORD' in line.upper():
            parts = line.split(':')
            if len(parts) > 1:
                count_str = parts[1].split(';')[0].strip()
                try:
                    file_record_count = int(count_str)
                except ValueError:
                    pass
            continue

        # pomijamy śmieci nagłówkowe / raportowe
        if (
            line.startswith(';') or
            'DOM POMOCY SPOŁECZNEJ' in line.upper() or
            'STRONA' in line.upper() or
            'L.P.' in line.upper() or
            'TWÓRZ ZAKRES' in line.upper()
        ):
            continue

        parts = [p.strip() for p in line.split(';')]

        # pierwsza kolumna MUSI być numerem porządkowym
        if not parts or not parts[0].isdigit():
            continue

        # usuwamy puste kolumny
        parts = [p for p in parts if p]

        # oczekujemy: [LP, NAZWISKO, IMIĘ, POKÓJ]
        if len(parts) < 4:
            continue

        last_name = parts[1].strip().upper()
        first_name = parts[2].strip().upper()
        room = parts[3].strip()
        
        processed_record_count += 1
        key = (last_name, first_name)
        seen_keys.add(key)

        resident = Resident.query.filter_by(
            last_name=last_name,
            first_name=first_name
        ).first()

        # --- NOWY / ISTNIEJĄCY REZYDENT ---
        if not resident:
            resident = Resident(
                last_name=last_name,
                first_name=first_name,
                room_number=room,
                floor=detect_floor(room),
                is_active=True,
                is_hospital=False,
                is_pass=False,
                has_diet=False,
                needs_attention=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(resident)
            db.session.flush()
        else:
            if resident.room_number != room:
                resident.room_number = room
                resident.floor = detect_floor(room)
                resident.needs_attention = True

            resident.is_active = True
            resident.updated_at = datetime.utcnow()

        # ⚠️ TEN CSV NIE ZAWIERA DIET – NIC WIĘCEJ TU NIE ROBIMY

    # --- 4. DEZAKTYWACJA OSÓB NIEOBECNYCH ---
    for r in Resident.query.filter_by(is_active=True).all():
        if (r.last_name, r.first_name) not in seen_keys:
            r.is_active = False

    db.session.commit()

    # --- 5. POLICZENIE AKTYWNYCH / NIEAKTYWNYCH ---
    active_count = Resident.query.filter_by(is_active=True).count()
    inactive_count = Resident.query.filter_by(is_active=False).count()

    # --- 6. WALIDACJA LICZBY REKORDÓW ---
    warning_message = None
    if file_record_count > 0 and processed_record_count != file_record_count:
        warning_message = f"Niezgodna liczba osób w pliku CSV: deklaracja różna od liczby rekordów {file_record_count} : {processed_record_count}"

    # Zwracamy informacje o imporcie
    return {
        'file_count': file_record_count,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'warning': warning_message
    }
