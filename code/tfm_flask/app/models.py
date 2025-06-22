import uuid, datetime as dt
from flask_login import UserMixin
from app import db, bcrypt, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    _password     = db.Column("password", db.String(128), nullable=False)
    created_at    = db.Column(db.DateTime, default=dt.datetime.utcnow)
    histories     = db.relationship("History", backref="owner", lazy=True,
                                    cascade="all, delete-orphan")

    @property
    def password(self): raise AttributeError("password is write-only")
    @password.setter
    def password(self, raw):
        self._password = bcrypt.generate_password_hash(raw).decode()

    def verify(self, raw): return bcrypt.check_password_hash(self._password, raw)

class History(db.Model):
    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp     = db.Column(db.DateTime, default=dt.datetime.utcnow, index=True)
    filename      = db.Column(db.String(255))
    display_name  = db.Column(db.String(255)) 
    audio_path    = db.Column(db.String(255))
    audio_mime    = db.Column(db.String(40))
    transcription = db.Column(db.Text)
    summary_short = db.Column(db.Text)
    summary_long  = db.Column(db.Text)
    user_id       = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
