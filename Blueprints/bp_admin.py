from flask import Blueprint, render_template, request, jsonify
from extensions import db
from modelosDB.modelos import SolicitacaoViagem
# Certifique-se de importar o DAO corretamente dependendo da estrutura das suas pastas
from DAOs.servidor_DAO import ServidorDAO 

admin_bp = Blueprint('bp_admin', __name__)

# ==============================================================================
# ROTAS DE PÁGINAS (RENDERIZAÇÃO)
# ==============================================================================

@admin_bp.route('/pag_admin')
def index():
    lista_viagens = SolicitacaoViagem.query.filter_by(status='Pendente').all()
    return render_template('admin.html', viagens=lista_viagens)

@admin_bp.route('/lista_servidores')
def lista_servidores():
    # Busca a lista completa de servidores no banco de dados usando o DAO
    servidores = ServidorDAO.listar()
    return render_template('lista_servidores.html', servidores=servidores)


# ==============================================================================
# ROTAS DE AÇÕES AJAX (SERVIDORES)
# ==============================================================================

@admin_bp.route('/lista_servidores/aprovar/<int:id_servidor>', methods=['POST'])
def aprovar_servidor(id_servidor):
    if ServidorDAO.aprovar(id_servidor):
        return jsonify({'sucesso': True, 'mensagem': 'Servidor aprovado com sucesso!'})
    return jsonify({'sucesso': False, 'erro': 'Servidor não encontrado no sistema.'}), 404

@admin_bp.route('/lista_servidores/excluir/<int:id_servidor>', methods=['POST'])
def excluir_servidor(id_servidor):
    if ServidorDAO.excluir(id_servidor):
        return jsonify({'sucesso': True, 'mensagem': 'Servidor excluído com sucesso!'})
    return jsonify({'sucesso': False, 'erro': 'Servidor não encontrado no sistema.'}), 404


# ==============================================================================
# ROTAS DE AÇÕES AJAX (VIAGENS)
# ==============================================================================

@admin_bp.route('/pag_admin/deferir_viagem', methods=['POST'])
def deferir_viagem():
    dados = request.get_json()
    if not dados:
        return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400

    id_viagem = dados.get('id_viagem')
    viagem = SolicitacaoViagem.query.get(id_viagem)

    if viagem:
        viagem.status = 'Deferida'
        db.session.commit()
        return jsonify({'sucesso': True, 'status': 'Deferida', 'motorista': viagem.motorista_nome})

    return jsonify({'sucesso': False, 'erro': 'Viagem não encontrada'}), 404


@admin_bp.route('/pag_admin/indeferir_viagem', methods=['POST'])
def indeferir_viagem():
    dados = request.get_json()
    if not dados:
        return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400

    id_viagem = dados.get('id_viagem')
    viagem = SolicitacaoViagem.query.get(id_viagem)

    if viagem:
        viagem.status = 'Indeferida'
        db.session.commit()
        return jsonify({'sucesso': True, 'status': 'Indeferida', 'motorista': viagem.motorista_nome})

    return jsonify({'sucesso': False, 'erro': 'Viagem não encontrada'}), 404