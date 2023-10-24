from flask import Blueprint, request, jsonify
from datetime import datetime
from vydra.models import Answers, Postsql, Relation_User_Wave
from app import db
from vydra.rotas.authentication.authentication import token_required
import random


climate_routes_bp = Blueprint('climate_routes',__name__)
banco = Postsql('dpg-cjju8uuphtvs73eff01g-a', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")
# banco = Postsql('dpg-cjju8uuphtvs73eff01g-a.oregon-postgres.render.com', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")

def recupera_onda():
    semana_atual: int
    if datetime.now().day <= 7:
        semana_atual = 1
    elif datetime.now().day > 7 and datetime.now().day <= 14:
        semana_atual = 2
    elif datetime.now().day > 14 and datetime.now().day <= 21:
        semana_atual = 3
    elif datetime.now().day > 21:
        semana_atual = 4

    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    return str(semana_atual) + str(mes_atual) + str(ano_atual)

@climate_routes_bp.route('/answer', methods=['POST'])
@token_required
def enviar_resposta():
    payload = request.json

    onda = recupera_onda()

    respostas = payload["answers"]

    relation_user_wave = Relation_User_Wave(
        employee_id=payload["employee_id"],
        wave=onda
    )
    db.session.add(relation_user_wave)

    for resposta_usuario in respostas:
        resposta = Answers(
            value=resposta_usuario['value'],
            date=datetime.now(),
            wave=onda,
            question_id=resposta_usuario['question_id'],
            team_id=resposta_usuario['team_id']
        )
        db.session.add(resposta)

    db.session.commit()

    return jsonify({'message': 'Resposta contabilizada com sucesso!'})

@climate_routes_bp.route('/questions/<int:id>', methods=['GET'])
@token_required
def perguntas(id):
    onda = recupera_onda()

    query_verifica_onda = "SELECT * FROM relation_user_wave WHERE employee_id = " + str(id) + \
        " and wave = " + str(onda) 
    onda_usuario = banco.query(query_verifica_onda)

    if onda_usuario:
        return jsonify({'questions': [], 'permission': False})

    query = '''   
    SELECT DISTINCT ON (dimension_id) dimension_id, description, id
    FROM questions
    ORDER BY dimension_id, send_date, RANDOM()'''

    dados = banco.query(query)
    random.shuffle(dados)
    questions = []

    for dado in dados:
        questions.append(
            {
                "question_id": dado[2],
                "dimension_id": dado[0],
                "description": dado[1]
            }
        )

    return jsonify({'questions': questions, 'permission': True})