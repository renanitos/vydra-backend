import os
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from vydra.models import Objectives, Postsql
from app import db
from vydra.rotas.authentication.authentication import token_required

objectives_routes_bp = Blueprint('objectives_routes',__name__)

@objectives_routes_bp.route('/objectives', methods=['POST'])
@token_required
def criar_objetivo():
    payload = request.json

    date_payload = payload.get('prevision_date')
    if date_payload:
        date_payload = datetime.strptime(date_payload, '%Y-%m-%d').date() + timedelta(1)

    objetivo = Objectives(
        name=payload['name'],
        description=payload['description'],
        created_at=datetime.now(),
        prevision_date=date_payload,
        team_id=payload['team_id'],
        status=payload["status"]
    )

    db.session.add(objetivo)
    db.session.commit()

    return jsonify({'message': 'Objetivo criado com sucesso!'})

@objectives_routes_bp.route('/objectives', methods=['GET'])
@token_required
def listar_objetivos():
    
    team_id = request.args.get('team_id')
    
    if team_id is not None:
        return jsonify(team_id)
    
    else:
        objetivos = Objectives.query.all()

        objetivos_json = []

        for objetivo in objetivos:

            objetivo_json = {
                'id': objetivo.id,
                'name': objetivo.name,
                'description': objetivo.description,
                'created_at': objetivo.created_at,
                'prevision_date': objetivo.prevision_date,
                'finished_at': objetivo.finished_at,
                'team_id': objetivo.team_id,
                'status': objetivo.status,
                'percentage': objetivo.percentage
            }

            objetivos_json.append(objetivo_json)

        return jsonify(objetivos_json)

@objectives_routes_bp.route('/objectives/<int:id>', methods=['GET'])
@token_required
def buscar_objetivo(id):
    objetivo = Objectives.query.get(id)

    if objetivo is None:
        return jsonify({'message': 'Objetivo não encontrado'}), 404

    objetivo_json = {
        'id': objetivo.id,
        'name': objetivo.name,
        'description': objetivo.description,
        'created_at': objetivo.created_at,
        'prevision_date': objetivo.prevision_date,
        'finished_at': objetivo.finished_at,
        'team_id': objetivo.team_id,
        'status': objetivo.status,
        'percentage': objetivo.percentage
    }

    return jsonify(objetivo_json)

@objectives_routes_bp.route('/objectives/<int:id>', methods=['PUT'])
@token_required
def atualizar_objetivo(id):
    payload = request.json

    objetivo = Objectives.query.get(id)

    if objetivo is None:
        return jsonify({'message': 'Objetivo não encontrado'}), 404
    
    date_payload = payload.get('prevision_date')
    if date_payload:
        date_payload = datetime.strptime(date_payload, '%Y-%m-%d').date() + timedelta(1)

    objetivo.name = payload['name']
    objetivo.description = payload['description']
    objetivo.prevision_date = date_payload
    objetivo.created_at = payload['created_at']
    objetivo.finished_at = payload.get('finished_at')
    objetivo.team_id = payload['team_id']
    objetivo.status = payload['status']

    db.session.commit()

    return jsonify({'message': 'Objetivo atualizado com sucesso!'})

@objectives_routes_bp.route('/objectives/<int:id>', methods=['DELETE'])
@token_required
def deletar_objetivo(id):
    objetivo = Objectives.query.get(id)

    if objetivo is None:
        return jsonify({'message': 'Objetivo não encontrado'}), 404

    db.session.delete(objetivo)
    db.session.commit()

    return jsonify({'message': 'Objetivo deletado com sucesso!'})

@objectives_routes_bp.route('/objectives/sql/popup', methods=['GET'])
def listar_okr_popup():
    
    banco = Postsql('dpg-cjju8uuphtvs73eff01g-a', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")

    query = '''SELECT json_build_object(
    'objective_name', o.name,
    'key_result_name', kr.name,
    'prevision_date', o.prevision_date,
    'weight_kr', kr.weight,
    'key_result_description', kr.description,
    'responsable_name', e.first_name || ' ' || e.last_name,
    'tasks', json_agg(json_build_object(
        'task_id', ts.id,
        'task_name', ts.name,
        'task_description', ts.description,
        'prevision_date_task', ts.prevision_date
            ))
        ) AS json_data
        FROM teams t 
        JOIN objectives o ON t.id = o.team_id
        JOIN key_results kr ON o.id = kr.objective_id
        JOIN employees e ON e.id = kr.responsable
        JOIN tasks ts ON kr.id = ts.key_result_id 
        WHERE t.id = o.team_id AND o.id = kr.objective_id AND kr.responsable = e.id AND ts.key_result_id = kr.id 
        GROUP BY o.name, kr.name, o.prevision_date, kr.weight, kr.description, e.first_name, e.last_name;'''

    dados = banco.query(query)

    return jsonify(dados)

    
@objectives_routes_bp.route('/objectives/kr_data', methods=['GET'])
def listar_okr_geral():
    
    banco = Postsql('dpg-cjju8uuphtvs73eff01g-a', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")

    team_id = request.args.get('team_id')


    query = f'''
    SELECT json_build_object(
    'objective_id', objectives.id,
    'objective_name', objectives.name,
    'objective_description', objectives.description,
    'created_at', objectives.created_at,
    'prevision_date', objectives.prevision_date,
    'finished_at', objectives.finished_at,
    'status', objectives.status,
    'key_results', (
        SELECT json_agg(json_build_object(
            'key_result_id', key_results.id,
            'key_result_name', key_results.name,
            'key_result_description', key_results.description,
            'created_at', key_results.created_at,
            'prevision_date', key_results.prevision_date,
            'finished_at', key_results.finished_at,
            'weight', key_results.weight,
            'objective_id', key_results.objective_id,
            'responsable', key_results.responsable
        ))
                FROM key_results
                WHERE key_results.objective_id = objectives.id
            )
        )
        FROM objectives
        WHERE objectives.team_id = {team_id};   
        '''

    dados = banco.query(query)

    return jsonify(dados)