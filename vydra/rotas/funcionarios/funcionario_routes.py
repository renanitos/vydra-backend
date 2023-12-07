import os
from flask import Blueprint, request, jsonify
from datetime import datetime
from vydra.models import Employees, Postsql, Users
from app import db
from vydra.rotas.authentication.authentication import token_required, gerador_token
from werkzeug.security import generate_password_hash

employees_routes_bp = Blueprint('employees_routes',__name__)

@employees_routes_bp.route('/employees', methods=['POST'])
@token_required
def criar_funcionario():
    payload = request.json

    funcionario = Employees(
        first_name=payload['first_name'],
        last_name=payload['last_name'],
        email=payload['email'],
        created_at=datetime.now(),
        birth_date=payload['birth_date'],
        role_id=payload['role_id'],
        team_id=payload['team_id']
    )

    db.session.add(funcionario)
    db.session.commit()

    new_employee_id = funcionario.id
    pass_hash = generate_password_hash(funcionario.first_name)

    user = Users(
        email=funcionario.email,
        password=pass_hash,
        token=gerador_token(new_employee_id),
        employee_id=new_employee_id
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Funcionário e usuário criados com sucesso!'})

@employees_routes_bp.route('/employees', methods=['GET'])
@token_required
def listar_funcionarios():
    funcionarios = Employees.query.order_by(Employees.first_name).all()

    funcionarios_json = []

    for funcionario in funcionarios:
        if str(funcionario.first_name).upper() == "ADMIN": continue
        
        funcionario_json = {
            'id': funcionario.id,
            'first_name': funcionario.first_name,
            'last_name': funcionario.last_name,
            'email': funcionario.email,
            'created_at': funcionario.created_at,
            'birth_date': funcionario.birth_date,
            'role_id': funcionario.role_id,
            'team_id': funcionario.team_id
        }

        funcionarios_json.append(funcionario_json)

    return jsonify(funcionarios_json)

@employees_routes_bp.route('/employees/<int:id>', methods=['GET'])
@token_required
def buscar_funcionario(id):
    funcionario = Employees.query.get(id)

    if funcionario is None:
        return jsonify({'message': 'Funcionário não encontrado'}), 404

    funcionario_json = {
        'id': funcionario.id,
        'first_name': funcionario.first_name,
        'last_name': funcionario.last_name,
        'email': funcionario.email,
        'created_at': funcionario.created_at,
        'birth_date': funcionario.birth_date,
        'role_id': funcionario.role_id,
        'team_id': funcionario.team_id
    }

    return jsonify(funcionario_json)

@employees_routes_bp.route('/employees/<int:id>', methods=['PUT'])
@token_required
def atualizar_funcionario(id):
    payload = request.json

    funcionario = Employees.query.get(id)

    if funcionario is None:
        return jsonify({'message': 'Funcionário não encontrado'}), 404

    funcionario.first_name = payload['first_name']
    funcionario.last_name = payload['last_name']
    funcionario.role_id = payload['role_id']
    funcionario.team_id = payload['team_id']

    db.session.commit()

    return jsonify({'message': 'Funcionário atualizado com sucesso!'})

@employees_routes_bp.route('/employees/<int:id>', methods=['DELETE'])
@token_required
def deletar_funcionario(id):
    funcionario = Employees.query.get(id)

    if funcionario is None:
        return jsonify({'message': 'Funcionário não encontrado'}), 404

    usuario_associado = Users.query.filter_by(employee_id=id).first()

    if usuario_associado:
        db.session.delete(usuario_associado)

    db.session.delete(funcionario)
    db.session.commit()

    return jsonify({'message': 'Funcionário e usuário deletados com sucesso!'})


@employees_routes_bp.route('/page_employees', methods=['GET'])
@token_required
def buscar_todos():
    banco = Postsql('dpg-cjju8uuphtvs73eff01g-a', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")

    query = '''   
    SELECT json_build_object(
    'employee_id', e.id,
    'name', e.first_name || ' ' || e.last_name,
    'role_name', r.name,
    'team_name', t.name,
    'first_name', e.first_name,
    'last_name', e.last_name,
    'role_id', r.id,
    'team_id', t.id
    ) AS json_data
    FROM employees e
    JOIN roles r ON e.role_id = r.id
    JOIN teams t ON e.team_id = t.id;'''

    dados = banco.query(query)

    return jsonify(dados)


