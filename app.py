from flask import Flask
from flask_cors import CORS 
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://vydra_96oh_user:LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg@dpg-cjju8uuphtvs73eff01g-a/vydra_96oh"
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://vydra_96oh_user:LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg@dpg-cjju8uuphtvs73eff01g-a.oregon-postgres.render.com/vydra_96oh"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

if __name__ == "__main__":
    app.run(debug=True)

from vydra.rotas.common_routes.common_routes import rotas_bp
from vydra.rotas.funcionarios.funcionario_routes import employees_routes_bp
from vydra.rotas.tasks.tasks_routes import task_routes_bp
from vydra.rotas.roles.roles_routes import role_routes_bp
from vydra.rotas.teams.teams_routes import team_routes_bp
from vydra.rotas.users.users_routes import user_routes_bp
from vydra.rotas.objectives.objectives_routes import objectives_routes_bp
from vydra.rotas.key_results.key_results_routes import key_results_routes_bp
from vydra.rotas.authentication.authentication import authentication_routes_bp
from vydra.rotas.dashboard.dashboard_routes import dashboard_routes_bp
from vydra.rotas.profile.profile_routes import profile_routes_bp
from vydra.rotas.climate.climate_routes import climate_routes_bp, atualiza_perguntas

#Instancia a classe de tarefas agendadas
scheduler = BackgroundScheduler()
# scheduler.add_job(atualiza_perguntas, 'cron', day_of_week='wed', hour=1, minute=10)
scheduler.add_job(atualiza_perguntas, 'cron', day_of_week='thu', hour=1)
scheduler.start()

app.register_blueprint(rotas_bp)
app.register_blueprint(employees_routes_bp)
app.register_blueprint(task_routes_bp)
app.register_blueprint(role_routes_bp)
app.register_blueprint(team_routes_bp)
app.register_blueprint(user_routes_bp)
app.register_blueprint(objectives_routes_bp)
app.register_blueprint(key_results_routes_bp)
app.register_blueprint(authentication_routes_bp)
app.register_blueprint(dashboard_routes_bp)
app.register_blueprint(profile_routes_bp)
app.register_blueprint(climate_routes_bp)