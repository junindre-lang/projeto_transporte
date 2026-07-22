from flask import Blueprint, render_template, jsonify, request,session
from datetime import datetime
from extensions import db
from modelosDB.modelos import SolicitacaoViagem, CoordenadaRota, Motorista
# Certifique-se de importar o DAO corretamente dependendo da estrutura das suas pastas
from DAOs.servidor_DAO import ServidorDAO
import string
import random


# Declarado uma única vez usando o padrão bp_admin
admin_bp = Blueprint('bp_admin', __name__)

# ==============================================================================
# ROTAS DE PÁGINAS (RENDERIZAÇÃO)
# ==============================================================================

@admin_bp.route('/pag_admin')
def index():
    if 'admin' not in session:
        return render_template('principal.html')
    else:
        lista_viagens = SolicitacaoViagem.query.filter_by(status='Pendente').all()
        return render_template('admin.html', viagens=lista_viagens)

@admin_bp.route('/lista_servidores')
def lista_servidores():
    # Busca a lista completa de servidores no banco de dados usando o DAO
    if 'admin' not in session:
        return render_template('principal.html')

    servidores = ServidorDAO.listar()
    return render_template('lista_servidores.html', servidores=servidores)

@admin_bp.route('/transito')
def transito():
    if 'admin' not in session:
        return render_template('principal.html')
    return render_template('transito.html')

@admin_bp.route('/rotas')
def rotas():
    if 'admin' not in session:
        return render_template('principal.html')
    return render_template('definir_rota.html')


# ==============================================================================
# ROTAS DE AÇÕES AJAX (SERVIDORES)
# ==============================================================================

@admin_bp.route('/lista_servidores/aprovar/<int:id_servidor>', methods=['POST'])
def aprovar_servidor(id_servidor):
    if 'admin' not in session:
        return render_template('principal.html')
    if ServidorDAO.aprovar(id_servidor):
        return jsonify({'sucesso': True, 'mensagem': 'Servidor aprovado com sucesso!'})
    return jsonify({'sucesso': False, 'erro': 'Servidor não encontrado no sistema.'}), 404

@admin_bp.route('/lista_servidores/excluir/<int:id_servidor>', methods=['POST'])
def excluir_servidor(id_servidor):
    if 'admin' not in session:
        return render_template('principal.html')
    if ServidorDAO.excluir(id_servidor):
        return jsonify({'sucesso': True, 'mensagem': 'Servidor excluído com sucesso!'})
    return jsonify({'sucesso': False, 'erro': 'Servidor não encontrado no sistema.'}), 404


# ==============================================================================
# ROTAS DE AÇÕES AJAX (VIAGENS)
# ==============================================================================

@admin_bp.route('/pag_admin/deferir_viagem', methods=['POST'])
def deferir_viagem():
    if 'admin' not in session:
        return render_template('principal.html')
    dados = request.get_json()
    if not dados:
        return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400

    id_viagem = dados.get('id_viagem')
    viagem = db.session.get(SolicitacaoViagem, id_viagem)

    if viagem:
        viagem.status = 'Deferida'
        db.session.commit()
        return jsonify({'sucesso': True, 'status': 'Deferida', 'motorista': viagem.motorista_nome})

    return jsonify({'sucesso': False, 'erro': 'Viagem não encontrada'}), 404


@admin_bp.route('/pag_admin/indeferir_viagem', methods=['POST'])
def indeferir_viagem():
    if 'admin' not in session:
        return render_template('principal.html')
    dados = request.get_json()
    if not dados:
        return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400

    id_viagem = dados.get('id_viagem')
    viagem = db.session.get(SolicitacaoViagem, id_viagem)

    if viagem:
        viagem.status = 'Indeferida'
        db.session.commit()
        return jsonify({'sucesso': True, 'status': 'Indeferida', 'motorista': viagem.motorista_nome})

    return jsonify({'sucesso': False, 'erro': 'Viagem não encontrada'}), 404


# ==============================================================================
# MONITORAMENTO EM TEMPO REAL & MONITORAMENTO IOT
# ==============================================================================

@admin_bp.route('/api/transito/tempo-real')
def transito_tempo_real():
    """
    API que o JavaScript vai consultar via Fetch para pegar
    as coordenadas e dados mais recentes de todas as viagens em andamento.
    """
    if 'admin' not in session:
        return render_template('principal.html')
    viagens_ativas = SolicitacaoViagem.query.filter_by(status='Em Andamento').all()

    lista_viagens = []
    for viagem in viagens_ativas:
        lista_viagens.append({
            "id": viagem.id,
            "motorista": viagem.motorista_nome,
            "rota": viagem.rota,
            "veiculo": viagem.veiculo,
            "lat": getattr(viagem, 'latitude_atual', -6.7578),
            "lon": getattr(viagem, 'longitude_atual', -38.2325),
            "velocidade": getattr(viagem, 'velocidade_atual', 0),
            "status": viagem.status
        })

    return jsonify(lista_viagens)


# ==========================================
# 1. ENDPOINT PARA DEFINIR/SALVAR UMA ROTA
# ==========================================
@admin_bp.route('/api/viagem/<int:viagem_id>/definir-rota', methods=['POST'])
def definir_rota(viagem_id):
    """
    Recebe um array de pontos do front-end e salva como o trajeto planejado da viagem.
    Format esperado do JSON: { "pontos": [{"lat": -6.75, "lon": -38.23}, ...] }
    """
    if 'admin' not in session:
        return render_template('principal.html')
    dados = request.get_json()
    # Correção do erro de digitação/sintaxe aqui:
    if not dados or 'pontos' not in dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    viagem = db.session.get(SolicitacaoViagem, viagem_id)
    if not viagem:
        return jsonify({"erro": "Viagem não encontrada"}), 404

    try:
        # Remove rotas antigas se houver redefinição para evitar lixo acumulado
        CoordenadaRota.query.filter_by(viagem_id=viagem.id).delete()

        # Salva os novos pontos sequencialmente
        for indice, ponto in enumerate(dados['pontos']):
            nova_coordenada = CoordenadaRota(
                viagem_id=viagem.id,
                latitude=ponto['lat'],
                longitude=ponto['lon'],
                ordem=indice
            )
            db.session.add(nova_coordenada)

        db.session.commit()
        return jsonify({"status": "sucesso", "mensagem": "Rota definida com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500


# ==========================================
# 2. ENDPOINT PARA ATUALIZAÇÃO DO HARDWARE IOT
# ==========================================
@admin_bp.route('/api/viagem/<int:viagem_id>/atualizar-posicao', methods=['POST'])
def atualizar_posicao(viagem_id):
    """
    Endpoint que o dispositivo IoT vai disparar via POST enquanto se movimenta.
    """
    if 'admin' not in session:
        return render_template('principal.html')
    dados = request.get_json()
    viagem = db.session.get(SolicitacaoViagem, viagem_id)

    if not viagem:
        return jsonify({"erro": "Viagem não encontrada"}), 404

    if viagem.status != 'Em Andamento':
        return jsonify({"erro": "Esta viagem não está ativa para monitoramento"}), 400

    try:
        viagem.latitude_atual = dados['lat']
        viagem.longitude_atual = dados['lon']
        viagem.velocidade_atual = dados['velocidade']
        viagem.ultima_atualizacao = datetime.now()

        db.session.commit()
        return jsonify({"status": "sucesso", "mensagem": "Coordenadas atualizadas"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500


# ==========================================
# 3. ENDPOINT CONSUMIDO PELO MAPA INDIVIDUAL
# ==========================================
@admin_bp.route('/api/viagem/<int:viagem_id>/posicao-atual', methods=['GET'])
def posicao_atual(viagem_id):
    if 'admin' not in session:
        return render_template('principal.html')
    viagem = db.session.get(SolicitacaoViagem, viagem_id)
    if not viagem:
        return jsonify({"erro": "Viagem não encontrada"}), 404

    # Busca os pontos da rota planejada ordenados para desenhar o trajeto estático no mapa
    pontos_planejados = CoordenadaRota.query.filter_by(viagem_id=viagem.id).order_by(CoordenadaRota.ordem).all()
    linha_planejada = [{"lat": p.latitude, "lon": p.longitude} for p in pontos_planejados]

    return jsonify({
        "motorista": viagem.motorista_nome,
        "veiculo": viagem.veiculo,
        "rota_nome": viagem.rota,
        "status": viagem.status,
        "lat_atual": getattr(viagem, 'latitude_atual', None),
        "lon_atual": getattr(viagem, 'longitude_atual', None),
        "velocidade": getattr(viagem, 'velocidade_atual', 0),
        "rota_planejada": linha_planejada
    })

@admin_bp.route('/cad_hora', methods=['GET'])
def cad_hora():
    if 'admin' not in session:
        return render_template('principal.html')
    return render_template('cadastrar_horario.html')


@admin_bp.route('/list_viagem', methods=['GET'])
def cad_viagem():
    if 'admin' not in session:
        return render_template('principal.html')

    viagens_banco = SolicitacaoViagem.query.all()
    viagens_processadas = []

    for viagem in viagens_banco:
        # Verifica se a viagem veio do mapa (checando a coluna ou se há coordenadas salvas)
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

    return render_template('listar_viagens.html', viagens=viagens_processadas)


@admin_bp.route('/api/viagem/excluir/<int:id_viagem>', methods=['POST'])
def excluir_viagem(id_viagem):
    if 'admin' not in session:
        return jsonify({'sucesso': False, 'erro': 'Não autorizado'}), 401

    viagem = db.session.get(SolicitacaoViagem, id_viagem)
    if not viagem:
        return jsonify({'sucesso': False, 'erro': 'Viagem não encontrada'}), 404

    try:
        # Limpa as coordenadas geográficas da rota para evitar chaves estrangeiras órfãs
        CoordenadaRota.query.filter_by(viagem_id=id_viagem).delete()

        db.session.delete(viagem)
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Viagem removida com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@admin_bp.route('/api/viagem/criar-via-mapa', methods=['POST'])
def criar_via_mapa():
    """
    Cria uma nova Solicitação de Viagem diretamente pelo desenho do mapa
    e salva seus respectivos pontos geométricos.
    """
    if 'admin' not in session:
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


@admin_bp.route('/api/motorista/cadastrar', methods=['POST'])
def cadastrar_motorista():
    # 1. Validação de segurança da sessão do Admin
    if 'admin' not in session:
        return jsonify({"sucesso": False, "erro": "Não autorizado"}), 401

    # 2. Captura e validação dos dados vindos do Front-end
    dados = request.get_json()
    if not dados or 'nome' not in dados:
        return jsonify({"sucesso": False, "erro": "O nome do motorista é obrigatório"}), 400

    nome = dados.get('nome')
    cpf = dados.get('cpf', '')

    try:
        # 3. Geração Automática e Única da Matrícula (Ex: 20268439)
        ano_atual = datetime.now().strftime('%Y')
        while True:
            sufixo_aleatorio = "".join(random.choices(string.digits, k=4))
            matricula_gerada = f"{ano_atual}{sufixo_aleatorio}"

            # Garante no banco de dados que essa matrícula gerada não é duplicada
            # (Substitua 'Motorista' pelo nome exato da sua classe de modelo se for diferente)
            existe = Motorista.query.filter_by(matricula=matricula_gerada).first()
            if not existe:
                break

        # 4. Geração da Senha Provisória Alfanumérica (8 caracteres)
        caracteres = string.ascii_letters + string.digits
        senha_gerada = "".join(random.choices(caracteres, k=8))

        # 5. Criação do objeto e salvamento no Banco de Dados
        novo_motorista = Motorista(
            nome=nome,
            cpf=cpf,
            matricula=matricula_gerada,
            senha=senha_gerada,  # Nota: Se usar criptografia, aplique o hash aqui (ex: generate_password_hash)
            status="Indisponível"  # Inicia como indisponível até ele clicar em "Ficar Livre" no painel dele
        )

        db.session.add(novo_motorista)
        db.session.commit()

        # 6. Retorno de Sucesso devolvendo as credenciais geradas para o Admin visualizar na tela
        return jsonify({
            "sucesso": True,
            "mensagem": "Motorista cadastrado com sucesso!",
            "credenciais": {
                "nome": nome,
                "matricula": matricula_gerada,
                "senha_provisoria": senha_gerada
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": f"Erro interno ao salvar no banco: {str(e)}"}), 500