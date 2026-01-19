@echo off
echo Uruchamianie aplikacji DPS Posilki...
cd /d "%~dp0"

:: Sprawdzenie czy venv istnieje
if not exist venv (
    echo Tworzenie srodowiska wirtualnego...
    python -m venv venv
)

:: Aktywacja i instalacja zaleznosci
call venv\Scripts\activate
echo Instalowanie/Aktualizacja bibliotek i zależności...
python -m pip install --upgrade pip
pip install flask flask_sqlalchemy flask_login openpyxl python-docx

:: Uruchomienie aplikacji
echo Start serwera WWW App:DPS Posilki ..
python app.py

:: To zatrzyma okno, jesli aplikacja sie wywali
echo.
echo [UWAGA] Serwer WWW zostal zatrzymany.
pause