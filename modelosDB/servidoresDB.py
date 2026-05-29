import dbm.sqlite3

from servidor import *

class Servidor(db.Model):
    __tablename__ = 'servidor'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    matricula = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<Servidor {self.nome}>'
