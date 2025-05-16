from datetime import datetime
from __init__ import db

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(40), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)