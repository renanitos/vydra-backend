from flask import Blueprint

rotas_bp =  Blueprint('rotas',__name__)

@rotas_bp.route('/')
def index():
    return '<h1> Testando BP </h1>'

@rotas_bp.route('/teste')
def teste():
    return '<h1> teste de rota simples </h1>'