from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from modelosDB.modelos import SolicitacaoViagem

servidor_bp = Blueprint('servidor_bp', __name__)

@servidor_bp.route('/cad_viagem', methods=['GET', 'POST'])
def solicitar_viagem():
    if request.method == 'POST':
        # Captura os dados enviados pelo formulário
        motorista = request.form.get('motorista')
        rota = request.form.get('rota')
        data = request.form.get('data')
        veiculo = request.form.get('veiculo')

        # Validação básica
        if not motorista or not rota or not data or not veiculo:
            flash("Todos os campos são obrigatórios!", "erro")
            return render_template('solicitar_viagem.html')

        # Cria a nova solicitação
        nova_viagem = SolicitacaoViagem(
            motorista_nome=motorista,
            rota=rota,
            data_horario=data,
            veiculo=veiculo,
            status='Pendente'
        )

        try:
            db.session.add(nova_viagem)
            db.session.commit()
            flash("Solicitação enviada com sucesso! Aguarde a análise do administrador.", "sucesso")
            return redirect(url_for('servidor_bp.solicitar_viagem'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar solicitação: {str(e)}", "erro")
            return render_template('solicitar_viagem.html')

    return render_template('solicitar_viagem.html')