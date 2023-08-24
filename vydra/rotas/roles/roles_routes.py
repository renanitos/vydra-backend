from flask import Blueprint, request, jsonify
from vydra.models import Roles
from app import db
from vydra.rotas.authentication.authentication import token_required


role_routes_bp = Blueprint('roles_routes',__name__)

@role_routes_bp.route('/roles', methods=['POST'])
@token_required
def criar_cargos():
    payload = request.json

    cargo = Roles(
        name=payload['name'],
        description=payload['description']
    )

    db.session.add(cargo)
    db.session.commit()

    return jsonify({'message': 'Cargo criado com sucesso!'})

@role_routes_bp.route('/roles', methods=['GET'])
@token_required
def listar_cargos():
    cargos = Roles.query.all()

    cargos_json = []

    for cargo in cargos:
        cargo_json = {
            'id': cargo.id,
            'name': cargo.name,
            'description': cargo.description,
        }

        cargos_json.append(cargo_json)

    return jsonify(cargos_json)

@role_routes_bp.route('/roles/<int:id>', methods=['GET'])
@token_required
def buscar_cargo(id):
    cargo = Roles.query.get(id)

    if cargo is None:
        return jsonify({'message': 'Cargo não encontrado'}), 404

    cargo_json = {
        'id': cargo.id,
        'name': cargo.name,
        'description': cargo.description,
    }

    return jsonify(cargo_json)

@role_routes_bp.route('/roles/<int:id>', methods=['PUT'])
@token_required
def atualizar_cargo(id):
    payload = request.json

    cargo = Roles.query.get(id)

    if cargo is None:
        return jsonify({'message': 'Cargo não encontrado'}), 404

    cargo.name = payload['name']
    cargo.description = payload['description']

    db.session.commit()

    return jsonify({'message': 'Cargo atualizado com sucesso!'})

@role_routes_bp.route('/roles/<int:id>', methods=['DELETE'])
@token_required
def deletar_tarefa(id):
    cargo = Roles.query.get(id)

    if cargo is None:
        return jsonify({'message': 'Cargo não encontrado'}), 404

    db.session.delete(cargo)
    db.session.commit()

    return jsonify({'message': 'Cargo deletado com sucesso!'})