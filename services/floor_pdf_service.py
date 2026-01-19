import subprocess
import tempfile
import os

from flask import current_app
from services.floor_docx_service import build_floor_docx


def build_floor_pdf(floor):

    # =====================================================
    # LibreOffice – ścieżka z config.py
    # =====================================================
    soffice_path = current_app.config.get("SOFFICE_PATH")

    if not soffice_path or not os.path.exists(soffice_path):
        raise RuntimeError(
            "LibreOffice (soffice.exe) nie jest skonfigurowany w config.py "
            "lub ścieżka jest nieprawidłowa"
        )

    # =====================================================
    # DOCX → PDF
    # =====================================================
    docx_path = build_floor_docx(floor)
    out_dir = tempfile.mkdtemp()

    cmd = [
        soffice_path,                 # ✅ TYLKO TO
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--convert-to", "pdf",
        "--outdir", out_dir,
        docx_path
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        raise RuntimeError("Nie można uruchomić LibreOffice")
    except subprocess.CalledProcessError:
        raise RuntimeError("LibreOffice zgłosił błąd przy konwersji PDF")

    pdf_name = os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
    pdf_path = os.path.join(out_dir, pdf_name)

    if not os.path.exists(pdf_path):
        raise RuntimeError("PDF nie został wygenerowany")

    return pdf_path
