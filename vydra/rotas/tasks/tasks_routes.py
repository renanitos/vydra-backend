from flask import Blueprint, request, jsonify
from datetime import datetime
from vydra.models import KeyResults, Objectives, Tasks
from app import db
from vydra.rotas.authentication.authentication import token_required


task_routes_bp = Blueprint('tasks_routes',__name__)

@task_routes_bp.route('/tasks', methods=['POST'])
@token_required
def criar_tarefa():
    payload = request.json

    tarefa = Tasks(
        name=payload['name'],
        description=payload['description'],
        created_at=datetime.now(),
        prevision_date=payload['prevision_date'],
        finished_at=payload.get('finished_at'),
        status=payload['status'],
        key_result_id=payload['key_result_id']
    )

    db.session.add(tarefa)
    db.session.commit()

    return jsonify({'message': 'Tarefa criada com sucesso!'})

@task_routes_bp.route('/tasks', methods=['GET'])
@token_required
def listar_tarefas():
    tarefas = Tasks.query.all()

    tarefas_json = []

    for tarefa in tarefas:
        tarefa_json = {
            'id': tarefa.id,
            'name': tarefa.name,
            'description': tarefa.description,
            'created_at': tarefa.created_at,
            'prevision_date': tarefa.prevision_date,
            'finished_at': tarefa.finished_at,
            'status': tarefa.status,
            'key_result_id': tarefa.key_result_id
        }

        tarefas_json.append(tarefa_json)

    return jsonify(tarefas_json)

@task_routes_bp.route('/tasks/<int:id>', methods=['GET'])
@token_required
def buscar_tarefa(id):
    tarefa = Tasks.query.get(id)

    if tarefa is None:
        return jsonify({'message': 'Tarefa não encontrado'}), 404

    tarefa_json = {
        'id': tarefa.id,
        'name': tarefa.name,
        'description': tarefa.description,
        'created_at': tarefa.created_at,
        'prevision_date': tarefa.prevision_date,
        'finished_at': tarefa.finished_at,
        'status': tarefa.status,
        'key_result_id': tarefa.key_result_id
    }

    return jsonify(tarefa_json)

@task_routes_bp.route('/tasks/<int:id>', methods=['PUT'])
@token_required
def atualizar_tarefa(id):
    payload = request.json

    tarefa = Tasks.query.get(id)

    if tarefa is None:
        return jsonify({'message': 'Tarefa não encontrada'}), 404

    tarefa.name = payload['name']
    tarefa.description = payload['description']
    tarefa.prevision_date = payload['prevision_date']
    tarefa.finished_at = payload.get('finished_at')
    tarefa.status = payload['status']
    tarefa.key_result_id = payload['key_result_id']

    if payload['status']:
        kr_tarefa = KeyResults.query.get(tarefa.key_result_id)
        krs = KeyResults.query.filter(KeyResults.objective_id == kr_tarefa.objective_id).all()
        tasks = Tasks.query.filter(Tasks.key_result_id == tarefa.key_result_id).all()
        objective_kr = Objectives.query.get(kr_tarefa.objective_id)

        sum_tasks = 0
        if not tasks:
            kr_tarefa.percentage = 100
        else:
            value_task = 100 / len(tasks)
            for task in tasks:
                if task.status:
                    sum_tasks += value_task
            kr_tarefa.percentage = int(round(sum_tasks, 0))

        sum_krs = 0
        if not krs:
            objective_kr.percentage = 100
        else:
            value_krs = 100 / len(krs)
            for okr in krs:
                if okr.percentage == 100:
                    sum_krs += value_krs
            objective_kr.percentage = int(round(sum_krs, 0))

    db.session.commit()

    return jsonify({'message': 'Tarefa atualizada com sucesso!'})

@task_routes_bp.route('/tasks/<int:id>', methods=['DELETE'])
@token_required
def deletar_tarefa(id):
    tarefa = Tasks.query.get(id)

    if tarefa is None:
        return jsonify({'message': 'Tarefa não encontrada'}), 404

    db.session.delete(tarefa)
    db.session.commit()

    return jsonify({'message': 'Tarefa deletada com sucesso!'})