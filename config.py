class Config:
    HOST = "0.0.0.0"
    PORT = 5000
    DEBUG = True
    SECRET_KEY = 'CHANGE_ME_SECRET_KEY'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ITEMS_PER_PAGE = 13
    ITEMS_PER_PAGE_SMALL = 10
    ALL_DIETS_IN_SUMMARY = True # False = tylko występujące, True = wszystkie ze słownika
    
    SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"
    
