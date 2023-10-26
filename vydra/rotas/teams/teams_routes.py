import os
from flask import Blueprint, request, jsonify
from vydra.models import Postsql, Teams
from app import db
from vydra.rotas.authentication.authentication import token_required


team_routes_bp = Blueprint('teams_routes',__name__)

@team_routes_bp.route('/teams', methods=['POST'])
@token_required
def criar_times():
    payload = request.json

    time = Teams(
        name=payload['name'],
        description=payload['description'],
        major_team_id=payload.get("major_team_id")
    )

    db.session.add(time)
    db.session.commit()

    return jsonify({'message': 'Time criado com sucesso!'})

@team_routes_bp.route('/teams', methods=['GET'])
@token_required
def listar_times():
    times = Teams.query.order_by(Teams.name).all()

    times_json = []

    for time in times:
        time_json = {
            'id': time.id,
            'name': time.name,
            'description': time.description,
            'major_team_id': time.major_team_id
        }

        times_json.append(time_json)

    return jsonify(times_json)

@team_routes_bp.route('/teams/<int:id>', methods=['GET'])
@token_required
def buscar_time(id):
    time = Teams.query.get(id)

    if time is None:
        return jsonify({'message': 'Time não encontrado'}), 404

    time_json = {
        'id': time.id,
        'name': time.name,
        'description': time.description,
        'major_team_id': time.major_team_id
    }

    return jsonify(time_json)

@team_routes_bp.route('/teams/<int:id>', methods=['PUT'])
@token_required
def atualizar_cargo(id):
    payload = request.json

    time = Teams.query.get(id)

    if time is None:
        return jsonify({'message': 'Time não encontrado'}), 404

    time.name = payload['name']
    time.description = payload['description']
    time.major_team_id = payload['major_team_id']

    db.session.commit()

    return jsonify({'message': 'Time atualizado com sucesso!'})

@team_routes_bp.route('/teams/<int:id>', methods=['DELETE'])
@token_required
def deletar_time(id):
    time = Teams.query.get(id)

    if time is None:
        return jsonify({'message': 'Time não encontrado'}), 404

    db.session.delete(time)
    db.session.commit()

    return jsonify({'message': 'Time deletado com sucesso!'})

@team_routes_bp.route('/page_teams', methods=['GET'])
@token_required
def buscar_todos_times():
    banco = Postsql('dpg-cjju8uuphtvs73eff01g-a', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")
    # banco = Postsql('dpg-cjju8uuphtvs73eff01g-a.oregon-postgres.render.com', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")

    query = '''   
    SELECT json_build_object(
    'id', t.id,
    'name', t.name,
    'description', t.description,
    'major_team_id', t.major_team_id,
    'major_team_name', t_major.name
    ) AS json_data
    FROM teams t
    LEFT JOIN teams t_major ON t.major_team_id = t_major.id;
    '''

    dados = banco.query(query)

    return jsonify(dados)