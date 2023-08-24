'''

PRIMEIRA VERSÃO DO BANCO DE DADOS - V1

from app import db,app


class Cargo(db.Model):
    __tablename__ = 'cargo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    desc = db.Column(db.String(100), nullable=False)
    func = db.relationship('funcionario', backref='cargo')

class Funcionario(db.Model):
    __tablename__ = 'funcionario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    nasc_at = db.Column(db.DateTime, nullable=False)
    salary = db.Column(db.Float(asdecimal=True))
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargo.id'))

    
with app.app_context():
    db.create_all()

'''