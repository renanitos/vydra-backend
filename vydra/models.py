import psycopg2 as pg
import pandas as pd
from app import db, app

class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)

class Objectives(db.Model):
    __tablename__ = 'objectives'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    prevision_date = db.Column(db.DateTime, nullable=False)
    finished_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Boolean, nullable=False)
    percentage = db.Column(db.Integer, nullable=True, default=0)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))

class KeyResults(db.Model):
    __tablename__ = 'key_results'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    prevision_date = db.Column(db.DateTime, nullable=False)
    finished_at = db.Column(db.DateTime, nullable=True)
    percentage = db.Column(db.Integer, nullable=True, default=0)
    objective_id = db.Column(db.Integer, db.ForeignKey('objectives.id'))
    responsable = db.Column(db.Integer, db.ForeignKey('employees.id'))

class Tasks(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    prevision_date = db.Column(db.DateTime, nullable=False)
    finished_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Boolean, nullable=False)
    key_result_id = db.Column(db.Integer, db.ForeignKey('key_results.id'))

class Teams(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    major_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)

class Employees(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    birth_date = db.Column(db.DateTime, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    email = db.Column(db.String(120), db.ForeignKey('employees.email'), nullable=True, unique=True)
    password = db.Column(db.String(256), nullable=False)
    token = db.Column(db.String(256), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    administrator = db.Column(db.Boolean, nullable=False)

class Dimensions(db.Model):
    __tablename__ = 'dimensions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)

class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    send_date = db.Column(db.DateTime, nullable=True)
    min_value = db.Column(db.String(50), nullable=False)
    max_value = db.Column(db.String(50), nullable=False)
    dimension_id = db.Column(db.Integer, db.ForeignKey('dimensions.id'))

class Answers(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=True)
    wave = db.Column(db.Integer, nullable=False)
    employee_id_encrypted = db.Column(db.String(256), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))

class Relation_User_Wave(db.Model):
    __tablename__ = 'relation_user_wave'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    wave = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

class Postsql:
    def __init__(self, host, database, user, password):
        self.db = pg.connect(host=host, database=database, user=user, password=password)


    def query(self, query):
        cur = self.db.cursor()
        cur.execute(query)
        retorno = cur.fetchall()
        return retorno

    def database(self, query):
        resp = pd.read_sql_query(query, self.db)
        resp = resp.values
        return resp

    def closedb(self):
        self.db.close()