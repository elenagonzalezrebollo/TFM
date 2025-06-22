from pathlib import Path
class Config:
    SECRET_KEY = "iTSd2sdF.w2€"
    SQLALCHEMY_DATABASE_URI  = "sqlite:///app.sqlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_DIR   = Path(__file__).resolve().parent.parent
    DATA_DIR   = BASE_DIR / "uploads"
    AUDIO_DIR  = DATA_DIR / "audio"
    DATA_DIR.mkdir(exist_ok=True)
    AUDIO_DIR.mkdir(exist_ok=True)
