from flask import *
from datetime import datetime
from extensions import db
from modelosDB.modelos import SolicitacaoViagem, CoordenadaRota
# Certifique-se de importar o DAO corretamente dependendo da estrutura das suas pastas
from DAOs.servidor_DAO import ServidorDAO

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


@servidor_bp.route('/rotas_servidor')
def rotas():
    if 'servidor' not in session:
        return render_template('principal.html')
    return render_template('definir_rota_serv.html')

@servidor_bp.route('/criar-via-mapa', methods=['POST'])
def criar_via_mapa():
    """
    Cria uma nova Solicitação de Viagem diretamente pelo desenho do mapa
    e salva seus respectivos pontos geométricos.
    """
    if 'servidor' not in session:
        return jsonify({"erro": "Não autorizado"}), 401

    dados = request.get_json()
    if not dados or 'pontos' not in dados:
        return jsonify({"erro": "Dados ou pontos do mapa não fornecidos"}), 400

    try:
        # 1. Cria o registro principal na tabela SolicitacaoViagem
        # Usamos o formato de data 'YYYY-MM-DDTHH:MM' para combinar com o padrão do seu print
        nova_viagem = SolicitacaoViagem(
            motorista_nome="A Definir",
            rota=dados.get('rota', 'Rota Gerada via Mapa'),
            data_horario=datetime.now().strftime('%Y-%m-%dT%H:%M'),
            veiculo="A Definir",
            status="Pendente"
        )

        # Garante a marcação do tipo se a coluna existir no banco
        if hasattr(nova_viagem, 'tipo_cadastro'):
            nova_viagem.tipo_cadastro = 'mapa'

        db.session.add(nova_viagem)
        db.session.flush()  # Faz o banco gerar o ID da viagem antes de dar o commit final

        # 2. Salva os pontos geométricos atrelados ao ID gerado acima
        for indice, ponto in enumerate(dados['pontos']):
            nova_coordenada = CoordenadaRota(
                viagem_id=nova_viagem.id,
                latitude=ponto['lat'],
                longitude=ponto['lon'],
                ordem=indice
            )
            db.session.add(nova_coordenada)

        db.session.commit()
        return jsonify(
            {"sucesso": True, "id_viagem": nova_viagem.id, "mensagem": "Viagem do mapa criada com sucesso!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500



@servidor_bp.route('/list_viagem_servidores', methods=['GET'])
def cad_viagem():
    if 'servidor' not in session:
        return render_template('principal.html')

    # 1. Recupera os dados do servidor que estão salvos na sessão
    # (Se você salvou um dicionário na sessão, pode passá-lo diretamente)
    servidor_logado = session.get('servidor')

    viagens_banco = SolicitacaoViagem.query.all()
    viagens_processadas = []

    for viagem in viagens_banco:
        if hasattr(viagem, 'tipo_cadastro') and viagem.tipo_cadastro:
            tipo = viagem.tipo_cadastro
        else:
            possui_mapa = CoordenadaRota.query.filter_by(viagem_id=viagem.id).first()
            tipo = 'mapa' if possui_mapa else 'manual'

        viagens_processadas.append({
            "id": viagem.id,
            "tipo_cadastro": tipo,
            "motorista_nome": viagem.motorista_nome,
            "rota": viagem.rota,
            "data_horario": viagem.data_horario,
            "veiculo": viagem.veiculo,
            "status": viagem.status
        })



    # 2. 🔥 Envia a variável 'servidor' para o HTML
    return render_template('homepage.html', viagens=viagens_processadas, servidor=servidor_logado)

@servidor_bp.route('/transito_serv')
def transito_mapa():
    if 'servidor' not in session:
        return render_template('homepage.html')
    return render_template('transito_serv.html')