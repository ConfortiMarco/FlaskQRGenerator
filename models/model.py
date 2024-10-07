from flask_login import UserMixin
from models.conn import db
from flask import current_app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# The UserMixin will add Flask-Login attributes to the model so that Flask-Login will be able to work with it.
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # Campo per la password criptata

    api_keys = db.relationship('ApiKey', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Imposta la password criptata."""
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        """Verifica se la password è corretta."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User username:{self.username}, email:{self.email}>'
    
    def set_api_key(self, key_value):
        """Imposta una chiave API personalizzata."""
        new_key = ApiKey(user=self, value=key_value)
        db.session.add(new_key)
        db.session.commit()

    def get_api_keys(self):
        """Restituisce le chiavi API personalizzate dell'utente."""
        return self.api_keys

class QrCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(255), nullable=False)
    background_color = db.Column(db.String(10), nullable=False)
    fill_color = db.Column(db.String(10), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    file = db.Column(db.String(255), nullable=True)
    qr_base64 = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(qr_code):
        return {
            'id': qr_code.id,
            'qr_base64': qr_code.qr_base64,
        }

class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    value = db.Column(db.String(80), unique=True, nullable=False)