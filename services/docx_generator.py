import os
import shutil
from docx import Document
from collections import defaultdict
from models.resident import Resident
from models.resident_diet import ResidentDiet
from models.diet import Diet
from models.user import db
from datetime import date


TEMPLATES = {
    0: 'parter.docx',
    1: 'pietro1.docx',
    2: 'pietro2.docx',
    3: 'pietro3.docx'
}


def generate_all(output_dir='generated'):
    os.makedirs(output_dir, exist_ok=True)
    paths = []

    for floor in TEMPLATES:
        path = generate_for_floor(floor, output_dir)
        paths.append(path)

    return paths


def generate_for_floor(floor: int, output_dir: str):
    template = os.path.join('templates_docx', TEMPLATES[floor])
    output = os.path.join(
        output_dir,
        f'DPS_diety_pietro_{floor}_{date.today()}.docx'
    )

    shutil.copy(template, output)
    doc = Document(output)

    residents = (
        db.session.query(Resident, ResidentDiet, Diet)
        .join(ResidentDiet, Resident.id == ResidentDiet.resident_id)
        .join(Diet, Diet.id == ResidentDiet.diet_id)
        .filter(
            Resident.floor == floor,
            Resident.is_active == True,
            Resident.is_hospital == False,
            Resident.is_pass == False
        )
        .order_by(Resident.room_number, Resident.last_name)
        .all()
    )

    fill_resident_table(doc, residents)
    fill_summary_tables(doc, residents)

    doc.save(output)
    return output
