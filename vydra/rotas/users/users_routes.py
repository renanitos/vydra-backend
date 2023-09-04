import os
from flask import Blueprint, request, jsonify
from vydra.models import Postsql, Users
from app import db
from werkzeug.security import generate_password_hash
from vydra.rotas.authentication.authentication import gerador_token, token_required

user_routes_bp = Blueprint('user_routes',__name__)

@user_routes_bp.route('/users', methods=['POST'])
def criar_usuario():
    payload = request.json
    password = payload['password']

    pass_hash = generate_password_hash(password)

    token = gerador_token(payload['employee_id'])

    usuario = Users(
        email=payload['email'],
        password=pass_hash,
        employee_id=payload['employee_id'],
        token=token
    )

    db.session.add(usuario)
    db.session.commit()

    return jsonify({'message': 'Usuario criado com sucesso!'})

@user_routes_bp.route('/users', methods=['GET'])
@token_required
def listar_usuario():
    usuarios = Users.query.all()

    usuarios_json = []

    for usuario in usuarios:
        usuario_json = {
            'id': usuario.id,
            'email': usuario.email
        }
        usuarios_json.append(usuario_json)

    return jsonify(usuarios_json)

@user_routes_bp.route('/users/<int:id>', methods=['GET'])
@token_required
def buscar_usuario(id):
    usuario = Users.query.get(id)

    if usuario is None:
        return jsonify({'message': 'Usuario não encontrado'}), 404

    usuario_json = {
        'id': usuario.id,
        'email': usuario.email,
        'employee_id': usuario.employee_id,
    }

    return jsonify(usuario_json)

@user_routes_bp.route('/users/<int:id>', methods=['PUT'])
@token_required
def atualizar_usuario(id):
    payload = request.json

    password = payload['password']
    pass_hash = generate_password_hash(password)

    usuario = Users.query.get(id)

    if usuario is None:
        return jsonify({'message': 'Usuario não encontrado'}), 404

    usuario.password = pass_hash

    db.session.commit()

    return jsonify({'message': 'usuario atualizado com sucesso!'})

@user_routes_bp.route('/users/<int:id>', methods=['DELETE'])
@token_required
def deletar_tarefa(id):
    usuario = Users.query.get(id)

    if usuario is None:
        return jsonify({'message': 'Usuario não encontrado'}), 404

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({'message': 'Usuario deletado com sucesso!'})

@user_routes_bp.route('/profile', methods=['POST'])
@token_required
def recuperar_perfil():
    payload = request.json
    email = payload["email"]
    employee_id = payload["employee_id"]
    banco = Postsql('dpg-cjju8uuphtvs73eff01g-a', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")
    # banco = Postsql('dpg-cjju8uuphtvs73eff01g-a.oregon-postgres.render.com', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")

    query = f'''   
    SELECT json_build_object(
    'employee_id', e.id,
    'name', e.first_name || ' ' || e.last_name,
    'role_name', r.name,
    'team_name', t.name,
    'first_name', e.first_name,
    'last_name', e.last_name,
    'role_id', r.id,
    'team_id', t.id,
    'email', u.email
    ) AS json_data
    FROM employees e
    LEFT JOIN roles r ON e.role_id = r.id
    LEFT JOIN teams t ON e.team_id = t.id
    LEFT JOIN users u ON u.employee_id = e.id
    WHERE e.id = {employee_id} AND u.email = '{email}';'''

    dados = banco.query(query)

    return jsonify(dados[0])
