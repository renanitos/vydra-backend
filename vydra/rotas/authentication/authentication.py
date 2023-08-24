import random
import string
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from functools import wraps
from vydra.models import Employees, Users
from werkzeug.security import check_password_hash

authentication_routes_bp = Blueprint('authentication_routes',__name__)

def gerador_token(employee_id):
    string_random = string.ascii_letters + string.digits + string.ascii_uppercase
    key = ''.join(random.choice(string_random) for i in range(12))
    employee = Employees.query.filter(employee_id == Employees.id).one()
    employee_information = {
        "id": employee.id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.email,
        "role_id": employee.role_id,
        "team_id": employee.team_id
    }
    token = jwt.encode({'username': employee_information, 'exp': datetime.now() + timedelta(hours=12) },
                        key)
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            return jsonify({'message': 'token is missing', 'data': []}), 401
        try:
            usuario = Users.query.filter(Users.token == token).one()
        except:
            return jsonify({'message': 'token is invalid or expired', 'data': []}), 401
        return f(*args, **kwargs)
    return decorated

@authentication_routes_bp.route('/login', methods=['POST', 'GET'])
def login():
    payload = request.json

    login=payload['login'],
    senha=payload['password']
    usuario = Users.query.filter(Users.email == login).one()
    employee = Employees.query.filter(Employees.email == login).one()

    try:
        verificacao = check_password_hash(pwhash=usuario.password, password=senha)
    except:
        return jsonify({'message': 'Não foi possível executar o login! Contate o suporte.'}), 400
    if not verificacao:
            return jsonify({'message': 'Login inválido!'}), 400
    
    return jsonify({'message': 'Login válido!', 'token': usuario.token, 'employee_id' : employee.id,
    'first_name': employee.first_name, 'last_name': employee.last_name, 'email': employee.email,
    'created_at': employee.created_at, 'birth_date': employee.birth_date, 'role_id': employee.role_id,
    'team_id': employee.team_id, })

@authentication_routes_bp.route('/validate-token', methods=['POST'])
def validate_token():
    payload = request.json

    token=payload['token']

    try:
        logged_user = Users.query.filter(Users.token == token).one()
    except:
        return jsonify({'message': 'Token inválido.'}), 400
    
    return jsonify({'message': 'Token válido!'})