import os
from flask import Blueprint, request, jsonify
from vydra.models import Roles, Postsql
from app import db
from vydra.rotas.authentication.authentication import token_required


profile_routes_bp = Blueprint('profile_routes',__name__)

@profile_routes_bp.route('/profile', methods=['GET'])
def listar_dados():
    
    banco = Postsql('dpg-cjju8uuphtvs73eff01g-a', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")
    # banco = Postsql('dpg-cjju8uuphtvs73eff01g-a.oregon-postgres.render.com', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")

    employee = request.args.get('id')

    query = f'''
    SELECT json_agg(
        json_build_object(
            'first_name', e.first_name,
            'last_name', e.last_name,
            'email', e.email,
            'birth_date', e.birth_date,
            'role_name', r.name,
            'team_name', t.name,
            'qtd_kr_responsable', k.qtd_kr_responsable
            )
        )
    FROM (
        SELECT e.id, count(k.responsable) AS qtd_kr_responsable
        FROM employees e
        JOIN key_results k ON e.id = k.responsable
        WHERE e.id = {employee}
        GROUP BY e.id
    ) AS k
    JOIN employees e ON e.id = k.id
    JOIN roles r ON e.role_id = r.id
    JOIN teams t ON e.team_id = t.id;
    '''

    dados = banco.query(query)

    return jsonify(dados)

