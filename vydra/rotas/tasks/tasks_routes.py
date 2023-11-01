from flask import Blueprint, request, jsonify
from datetime import datetime
from vydra.models import KeyResults, Objectives, Tasks, Postsql
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

#LISTA A TASK POR KEY_RESULT_ID
@task_routes_bp.route('/tasks/task_kr', methods=['GET'])
def listar_tasks_kr_id():
    
    banco = Postsql('dpg-cjju8uuphtvs73eff01g-a', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")

    key_result_id = request.args.get('key_result_id')

    query = f'''
    SELECT json_agg(t) AS tasks
    FROM (
        SELECT * 
        FROM tasks
        WHERE key_result_id = {key_result_id}
    ) t;
    '''

    dados = banco.query(query)

    return jsonify(dados)

#LISTA TODOS OS OBJETIVOS, KEY_RESULTS E TASKS POR TEAM_ID
@task_routes_bp.route('/tasks/all_tasks', methods=['GET'])
def listar_obj_kr_task():
    
    banco = Postsql('dpg-cjju8uuphtvs73eff01g-a', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")
    # banco = Postsql('dpg-cjju8uuphtvs73eff01g-a.oregon-postgres.render.com', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")

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
    'percentage', objectives.percentage,
    'team_id', objectives.team_id,
    'key_results', (
        SELECT json_agg(json_build_object(
            'key_result_id', key_results.id,
            'key_result_name', key_results.name,
            'key_result_description', key_results.description,
            'created_at', key_results.created_at,
            'prevision_date', key_results.prevision_date,
            'finished_at', key_results.finished_at,
            'weight', key_results.weight,
            'percentage', key_results.percentage,
            'objective_id', key_results.objective_id,
            'responsable', key_results.responsable,
            'responsable_name', employees.first_name,
            'tasks', (
                SELECT json_agg(json_build_object(
                    'task_id', tasks.id,
                    'task_name', tasks.name,
                    'task_description', tasks.description,
                    'task_created_at', tasks.created_at,
                    'task_prevision_date', tasks.prevision_date,
                    'task_finished_at', tasks.finished_at,
                    'task_status', tasks.status
                ))
                FROM tasks
                WHERE tasks.key_result_id = key_results.id
            )
        ))
        FROM key_results
        LEFT JOIN employees employees ON employees.id = key_results.responsable
        WHERE key_results.objective_id = objectives.id
    )
    )
    FROM objectives
    WHERE objectives.team_id = {team_id}
    ORDER BY objectives.name;
    '''

    dados = banco.query(query)

    return jsonify(dados)