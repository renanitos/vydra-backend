import os
from flask import Blueprint, request, jsonify
from datetime import datetime
from vydra.models import KeyResults, Postsql
from app import db
from vydra.rotas.authentication.authentication import token_required


key_results_routes_bp = Blueprint('key_results_routes',__name__)

@key_results_routes_bp.route('/key_results', methods=['POST'])
@token_required
def criar_resultado_chave():
    payload = request.json

    date_payload = payload.get('prevision_date_formated')
    if date_payload:
        date_payload = datetime.strptime(date_payload, '%Y-%m-%d').date()

    resultado_chave = KeyResults(
        name=payload['name'],
        description=payload['description'],
        created_at=datetime.now(),
        prevision_date=date_payload,
        weight=payload['weight'],
        objective_id=payload['objective_id'],
        responsable=payload['responsable']
    )

    db.session.add(resultado_chave)
    db.session.commit()

    return jsonify({'message': 'Resultado chave criado com sucesso!'})

@key_results_routes_bp.route('/key_results', methods=['GET'])
@token_required
def listar_resultado_chaves():
    resultados_chave = KeyResults.query.all()

    resultados_chave_lista = []

    for resultado_chave in resultados_chave:
        resultado_chave_json = {
            'id': resultado_chave.id,
            'name': resultado_chave.name,
            'description': resultado_chave.description,
            'created_at': resultado_chave.created_at,
            'prevision_date': resultado_chave.prevision_date,
            'finished_at': resultado_chave.finished_at,
            'weight': resultado_chave.weight,
            'objective_id': resultado_chave.objective_id,
            'responsable': resultado_chave.responsable,
            'percentage': resultado_chave.percentage
        }

        resultados_chave_lista.append(resultado_chave_json)

    return jsonify(resultados_chave_lista)

@key_results_routes_bp.route('/key_results/<int:id>', methods=['GET'])
@token_required
def buscar_resultado_chave(id):
    resultado_chave = KeyResults.query.get(id)

    if resultado_chave is None:
        return jsonify({'message': 'Resultado chave não encontrado'}), 404

    resultado_chave_json = {
        'id': resultado_chave.id,
        'name': resultado_chave.name,
        'description': resultado_chave.description,
        'created_at': resultado_chave.created_at,
        'prevision_date': resultado_chave.prevision_date,
        'finished_at': resultado_chave.finished_at,
        'weight': resultado_chave.weight,
        'objective_id': resultado_chave.objective_id,
        'responsable': resultado_chave.responsable,
        'percentage': resultado_chave.percentage
    }

    return jsonify(resultado_chave_json)

@key_results_routes_bp.route('/key_results/<int:id>', methods=['PUT'])
@token_required
def atualizar_resultado_chave(id):
    payload = request.json

    resultado_chave = KeyResults.query.get(id)

    if resultado_chave is None:
        return jsonify({'message': 'Resultado-chave não encontrado'}), 404

    date_payload = payload.get('prevision_date_formated')
    if date_payload:
        date_payload = datetime.strptime(date_payload, '%Y-%m-%d').date()
    
    resultado_chave.name = payload['name']
    resultado_chave.description = payload['description']
    resultado_chave.prevision_date = date_payload
    resultado_chave.finished_at = payload.get('finished_at')
    resultado_chave.weight = payload['weight']
    resultado_chave.responsable = payload['responsable']
    resultado_chave.percentage = payload.get('percentage')

    db.session.commit()

    return jsonify({'message': 'Resultado-chave atualizado com sucesso!'})

@key_results_routes_bp.route('/key_results/<int:id>', methods=['DELETE'])
@token_required
def deletar_resultado_chave(id):
    resultado_chave = KeyResults.query.get(id)

    if resultado_chave is None:
        return jsonify({'message': 'Resultado-chave não encontrado'}), 404

    db.session.delete(resultado_chave)
    db.session.commit()

    return jsonify({'message': 'Resultado-chave deletado com sucesso!'})

@key_results_routes_bp.route('/page_key_results', methods=['GET'])
@token_required
def buscar_resultado_chave_page():
    banco = Postsql('dpg-cjju8uuphtvs73eff01g-a', 'vydra_96oh', 'vydra_96oh_user', "LNZSNaXgaB2tnD51TY8eHxNgeJ5PK8zg")

    query = '''   
        SELECT json_build_object(
        'id', kr.id,
        'name', kr.name,
        'description', kr.description,
        'prevision_date', kr.prevision_date,
        'weight', kr.weight,
        'objective_id', kr.objective_id,
        'responsable_id', e.id,
        'responsable', e.first_name,
        'percentage', kr.percentage
        ) AS json_data
        FROM key_results kr
        JOIN employees e ON e.id = kr.responsable;
    '''

    dados = banco.query(query)

    dados_formatados = []

    for dado in dados:
        resultado_chave = {}
        resultado_chave["id"] = dado[0]["id"]
        resultado_chave["name"] = dado[0]["name"]
        resultado_chave["description"] = dado[0]["description"]
        resultado_chave["prevision_date"] = dado[0]["prevision_date"]
        resultado_chave["weight"] = dado[0]["weight"]
        resultado_chave["objective_id"] = dado[0]["objective_id"]
        resultado_chave["responsable"] = dado[0]["responsable"]
        resultado_chave["percentage"] = dado[0]["percentage"]
        dados_formatados.append(resultado_chave)

    return jsonify(dados_formatados)