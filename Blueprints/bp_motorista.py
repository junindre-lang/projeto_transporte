from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from extensions import db
from modelosDB.modelos import Motorista, SolicitacaoViagem, Veiculo
from sqlalchemy import or_

bp_motorista = Blueprint('bp_motorista', __name__)


def motorista_logado():
    motorista_id = session.get('motorista_id')
    return db.session.get(Motorista, motorista_id) if motorista_id else None


def resposta_nao_autorizada():
    return jsonify({'sucesso': False, 'erro': 'Autenticação de motorista necessária.'}), 401


def viagem_do_motorista(viagem_id, motorista):
    """Busca apenas viagem atribuída ao motorista autenticado."""
    return SolicitacaoViagem.query.filter(
        SolicitacaoViagem.id == viagem_id,
        or_(SolicitacaoViagem.motorista_id == motorista.id,
            (SolicitacaoViagem.motorista_id.is_(None) &
             (SolicitacaoViagem.motorista_nome == motorista.nome)))
    ).first()


@bp_motorista.route('/motorista', methods=['GET', 'POST'])
def pagina_motorista():
    if request.method == 'POST':
        identificador = (request.form.get('identificador') or '').strip()
        senha = request.form.get('senha') or ''
        motorista = Motorista.query.filter(
            (Motorista.matricula == identificador) | (Motorista.cpf == identificador)
        ).filter_by(senha=senha).first()
        if not motorista:
            return render_template('motorista/login_motorista.html', msg='Matrícula/CPF ou senha incorretos.'), 401

        session.clear()
        session['motorista_id'] = motorista.id
        return redirect(url_for('bp_motorista.pagina_motorista'))

    motorista = motorista_logado()
    if not motorista:
        return redirect(url_for('pagina_motorista'))
    return render_template('motorista/princ_motorista.html', motorista=motorista)


@bp_motorista.route('/motorista/sair', methods=['POST'])
def sair():
    session.pop('motorista_id', None)
    return redirect(url_for('pagina_motorista'))


@bp_motorista.route('/api/motorista/status', methods=['GET'])
def consultar_status():
    motorista = motorista_logado()
    if not motorista:
        return resposta_nao_autorizada()
    return jsonify({'sucesso': True, 'status': motorista.status})


@bp_motorista.route('/api/motorista/status-livre', methods=['POST'])
def status_livre():
    motorista = motorista_logado()
    if not motorista:
        return resposta_nao_autorizada()
    if SolicitacaoViagem.query.filter_by(motorista_id=motorista.id, status='Em Andamento').first():
        return jsonify({'sucesso': False, 'erro': 'Conclua a viagem em andamento antes de alterar sua disponibilidade.'}), 409

    motorista.status = 'Disponível' if motorista.status != 'Disponível' else 'Indisponível'
    db.session.commit()
    return jsonify({'sucesso': True, 'status': motorista.status})


@bp_motorista.route('/api/motorista/viagens-agendadas', methods=['GET'])
def viagens_agendadas():
    motorista = motorista_logado()
    if not motorista:
        return resposta_nao_autorizada()
    viagens = SolicitacaoViagem.query.filter(
        or_(SolicitacaoViagem.motorista_id == motorista.id,
            (SolicitacaoViagem.motorista_id.is_(None) &
             (SolicitacaoViagem.motorista_nome == motorista.nome)))
    ).filter(SolicitacaoViagem.status.in_(['Deferida', 'Em Andamento'])).order_by(
        SolicitacaoViagem.data_horario.asc()).all()
    return jsonify([{'id': v.id, 'rota': v.rota, 'horario': v.data_horario,
                     'veiculo': v.veiculo, 'status': v.status} for v in viagens])


@bp_motorista.route('/api/motorista/iniciar-viagem', methods=['POST'])
def iniciar_viagem():
    motorista = motorista_logado()
    if not motorista:
        return resposta_nao_autorizada()
    viagem_id = (request.get_json(silent=True) or {}).get('id_viagem')
    if not viagem_id:
        return jsonify({'sucesso': False, 'erro': 'Identificador da viagem é obrigatório.'}), 400
    viagem = viagem_do_motorista(viagem_id, motorista)
    if not viagem:
        return jsonify({'sucesso': False, 'erro': 'Viagem não encontrada ou não atribuída a este motorista.'}), 404
    if viagem.status != 'Deferida':
        return jsonify({'sucesso': False, 'erro': 'Somente viagens deferidas podem ser iniciadas.'}), 409
    if SolicitacaoViagem.query.filter_by(motorista_id=motorista.id, status='Em Andamento').first():
        return jsonify({'sucesso': False, 'erro': 'Já existe uma viagem em andamento para este motorista.'}), 409

    viagem.status, motorista.status = 'Em Andamento', 'Em Viagem'
    veiculo = Veiculo.query.filter_by(prefixo=viagem.veiculo).first()
    if veiculo:
        veiculo.status = 'Em uso'
    db.session.commit()
    return jsonify({'sucesso': True, 'status': viagem.status, 'mensagem': 'Viagem iniciada com sucesso.'})


@bp_motorista.route('/api/motorista/concluir-viagem', methods=['POST'])
def concluir_viagem():
    motorista = motorista_logado()
    if not motorista:
        return resposta_nao_autorizada()
    viagem_id = (request.get_json(silent=True) or {}).get('id_viagem')
    viagem = viagem_do_motorista(viagem_id, motorista) if viagem_id else None
    if not viagem:
        return jsonify({'sucesso': False, 'erro': 'Viagem não encontrada ou não atribuída a este motorista.'}), 404
    if viagem.status != 'Em Andamento':
        return jsonify({'sucesso': False, 'erro': 'Somente uma viagem em andamento pode ser concluída.'}), 409

    viagem.status, motorista.status = 'Concluída', 'Disponível'
    veiculo = Veiculo.query.filter_by(prefixo=viagem.veiculo).first()
    if veiculo:
        veiculo.status = 'Disponível'
    db.session.commit()
    return jsonify({'sucesso': True, 'status': viagem.status, 'mensagem': 'Viagem concluída e motorista liberado.'})
