from flask import Blueprint, render_template, jsonify, request,session
from datetime import datetime
from extensions import db


bp_motorista = Blueprint('bp_motorista', __name__)

from flask import Blueprint, jsonify, request, render_template


# Rota para renderizar a página do motorista (HTML)
@bp_motorista.route('/motorista')
def pagina_motorista():
    return render_template('princ_motorista.html')


# 1. API: Ficar Livre / Disponível
@bp_motorista.route('/api/motorista/status-livre', methods=['POST'])
def status_livre():
    # TODO: Aqui você atualiza o status do motorista no Banco de Dados para 'Livre'
    # Exemplo: atualiza_status_motorista(id_motorista, 'Livre')

    print("Backend: Motorista agora está marcado como LIVRE para o ADM.")
    return jsonify({
        "status": "sucesso",
        "mensagem": "Você está visível e livre para o sistema."
    }), 200


# 2. API: Verificar Viagens Agendadas
@bp_motorista.route('/api/motorista/viagens-agendadas', methods=['GET'])
def viagens_agendadas():
    # TODO: Buscar no banco as viagens delegadas a este motorista
    # Simulação de dados vindos do banco de dados:
    viagens_mock = [
        {
            "id": 105,
            "rota": "Sousa x Cajazeiras",
            "horario": "16:30",
            "veiculo": "Vans-04"
        }
    ]

    # Se não houver viagens, você pode retornar uma lista vazia []
    return jsonify(viagens_mock), 200


# 3. API: Iniciar Viagem
@bp_motorista.route('/api/motorista/iniciar-viagem', methods=['POST'])
def iniciar_viagem():
    # TODO: Mudar status do motorista/viagem no banco para 'Em Viagem'
    # Isso fará o veículo começar a ser monitorado no mapa principal

    print("Backend: Viagem INICIADA. Rastreamento em tempo real liberado.")
    return jsonify({
        "status": "sucesso",
        "mensagem": "Viagem iniciada com sucesso."
    }), 200


# 4. API: Concluir Viagem
@bp_motorista.route('/api/motorista/concluir-viagem', methods=['POST'])
def concluir_viagem():
    # TODO: Salvar horário de término no banco e mudar status para 'Indisponível' ou 'Livre'

    print("Backend: Viagem CONCLUÍDA. Removendo veículo do mapa ativo.")
    return jsonify({
        "status": "sucesso",
        "mensagem": "Viagem finalizada com sucesso."
    }), 200





