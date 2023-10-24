import atexit
import datetime
import time

from apscheduler.schedulers.background import BackgroundScheduler
from vydra.models import Postsql, Questions
from app import db

banco = Postsql('dpg-cjju8uuphtvs73eff01g-a.oregon-postgres.render.com', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")

def atualiza_perguntas():
    print("atualizei")
    query = '''   
    SELECT DISTINCT ON (dimension_id) dimension_id, id
    FROM questions
    ORDER BY dimension_id, send_date'''

    dados = banco.query(query)

    for dado in dados:
        question = Questions.query.get(dado[1])
        question.send_date = datetime.now()
        db.session.commit()

    print("atualizei2")

#Instancia a classe de tarefas agendadas
scheduler = BackgroundScheduler()
scheduler.add_job(atualiza_perguntas, 'interval', seconds=5)
scheduler.add_job(atualiza_perguntas, 'cron', day_of_week='wed', hour=2, minute=30)
scheduler.start()