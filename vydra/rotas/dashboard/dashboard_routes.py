import os
from flask import Blueprint, jsonify, request
from vydra.models import Postsql
from vydra.rotas.authentication.authentication import token_required


dashboard_routes_bp = Blueprint('dashboard_routes',__name__)

@dashboard_routes_bp.route('/dashboard', methods=['GET'])
@token_required
def visao_geral_time():
    banco = Postsql('localhost', 'vydra', 'postgres', os.getenv("DATABASE_PASSWORD"))

    team_id = request.args.get('team_id')

    query = f'''
    SELECT json_build_object(
    'objectives_completed', (
        SELECT COUNT(id) 
        FROM objectives 
        WHERE status = true AND team_id = {team_id}
    ),
    'total_objectives', (
        SELECT COUNT(id) 
        FROM objectives 
        WHERE team_id = {team_id}
    ),
    'key_results_completed', (
        SELECT COUNT(kr.id) 
        FROM key_results kr
        JOIN objectives o ON o.id = kr.objective_id
        WHERE kr.percentage = 100 AND o.team_id = {team_id}
    ),
    'total_key_results', (
        SELECT COUNT(kr.id) 
        FROM key_results kr
        JOIN objectives o ON o.id = kr.objective_id
        WHERE o.team_id = {team_id}
    ),
    'tasks_completed', (
        SELECT COUNT(ta.id) 
        FROM tasks ta
        JOIN key_results kr ON kr.id = ta.key_result_id
        JOIN objectives o ON o.id = kr.objective_id
        WHERE ta.status = true AND o.team_id = {team_id}
    ),
    'total_tasks', (
        SELECT COUNT(ta.id) 
        FROM tasks ta
        JOIN key_results kr ON kr.id = ta.key_result_id
        JOIN objectives o ON o.id = kr.objective_id
        WHERE o.team_id = {team_id}
    )
    ) AS visao_geral;   
    '''

    
    dados = banco.query(query)
    return jsonify(dados)

@dashboard_routes_bp.route('/dashboard_comp', methods=['GET'])
@token_required
def visao_geral_empresa():
    banco = Postsql('localhost', 'vydra', 'postgres', os.getenv("DATABASE_PASSWORD"))

    query = f'''
        SELECT json_agg(json_build_object(
        'percentage_okr', COALESCE(percentage_okr, 0),
        'qtd_objectives', COALESCE(qtd_objectives, 0),
        'qtd_key_results', COALESCE(qtd_key_results, 0)
    )) AS result
FROM (
    SELECT
        ROUND(SUM(COALESCE(kr.percentage, 0)) / COUNT(kr.id), 1) AS percentage_okr,
        COUNT(DISTINCT o.id) AS qtd_objectives,
        COUNT(kr.id) AS qtd_key_results
    FROM objectives o
    LEFT JOIN key_results kr ON o.id = kr.objective_id
) AS metric_data;
        '''

    dados = banco.query(query)
    return jsonify(dados)


@dashboard_routes_bp.route('/dashboard_teams', methods=['GET'])
@token_required
def visao_times():
    banco = Postsql('localhost', 'vydra', 'postgres', os.getenv("DATABASE_PASSWORD"))

    query = f'''
       SELECT json_agg(json_build_object('name', name, 'percentage', ROUND(average_percentage, 2))) AS json_output
FROM (
    SELECT t.name, ROUND(AVG(kr_avg.percentage_avg), 2) AS average_percentage
    FROM teams t
    LEFT JOIN objectives o ON t.id = o.team_id
    LEFT JOIN (
            SELECT o.id, AVG(kr.percentage) AS percentage_avg
            FROM objectives o
            JOIN key_results kr ON kr.objective_id = o.id
            GROUP BY o.id
        ) kr_avg ON kr_avg.id = o.id
        GROUP BY t.name
    ) subquery;
        '''

    dados = banco.query(query)
    return jsonify(dados)
