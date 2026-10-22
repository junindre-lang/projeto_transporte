from flask import Blueprint, render_template, jsonify, request,session
from datetime import date, datetime, timedelta
from extensions import db
from modelosDB.modelos import SolicitacaoViagem, CoordenadaRota, Motorista, Veiculo, RotaFixa, Servidor
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
        return render_template('auth/principal.html')
    else:
        lista_viagens = SolicitacaoViagem.query.filter_by(status='Pendente').all()
        servidores_pendentes = Servidor.query.filter_by(status='Pendente').order_by(Servidor.nome).all()
        return render_template('admin/admin.html', viagens=lista_viagens,
                               servidores_pendentes=servidores_pendentes)

@admin_bp.route('/lista_servidores')
def lista_servidores():
    # Busca a lista completa de servidores no banco de dados usando o DAO
    if 'admin' not in session:
        return render_template('auth/principal.html')

    servidores = ServidorDAO.listar()
    return render_template('admin/lista_servidores.html', servidores=servidores)

@admin_bp.route('/transito')
def transito():
    if 'admin' not in session:
        return render_template('auth/principal.html')
    return render_template('admin/transito.html')

@admin_bp.route('/rotas')
def rotas():
    if 'admin' not in session:
        return render_template('auth/principal.html')
    return render_template('admin/definir_rota.html', motoristas=Motorista.query.order_by(Motorista.nome).all())


@admin_bp.route('/consultar_rotas')
def consultar_rotas():
    if 'admin' not in session:
        return render_template('auth/principal.html')

    inicio_texto = request.args.get('data_inicial', '').strip()
    fim_texto = request.args.get('data_final', '').strip()
    viagens = []
    erro = None
    data_inicial = data_final = None

    if inicio_texto or fim_texto:
        try:
            data_inicial = datetime.strptime(inicio_texto, '%Y-%m-%d').date()
            data_final = datetime.strptime(fim_texto, '%Y-%m-%d').date()
            if data_final < data_inicial:
                raise ValueError
        except ValueError:
            erro = 'Informe um intervalo válido: a data inicial deve ser anterior ou igual à data final.'
        else:
            _materializar_viagens_fixas(data_inicial, data_final)
            registros = SolicitacaoViagem.query.filter(
                SolicitacaoViagem.data_agendada.isnot(None),
                SolicitacaoViagem.data_agendada >= data_inicial,
                SolicitacaoViagem.data_agendada <= data_final
            ).order_by(SolicitacaoViagem.data_agendada, SolicitacaoViagem.data_horario).all()
            viagens = [{
                'id': viagem.id,
                'data': viagem.data_agendada.strftime('%d/%m/%Y'),
                'horario': viagem.data_horario.rsplit(' ', 1)[-1],
                'motorista': viagem.motorista_nome,
                'rota': viagem.rota,
                'veiculo': viagem.veiculo,
                'status': viagem.status
            } for viagem in registros]

    return render_template(
        'admin/consultar_rotas.html',
        viagens=viagens,
        erro=erro,
        data_inicial=inicio_texto,
        data_final=fim_texto
    )


def _materializar_viagens_fixas(data_inicial, data_final):
    """Cria uma ocorrência por dia para cada rota fixa ativa no intervalo."""
    dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    rotas = RotaFixa.query.filter(
        RotaFixa.ativa.is_(True),
        RotaFixa.data_inicio <= data_final,
        RotaFixa.data_fim >= data_inicial
    ).all()
    alterado = False

    for rota in rotas:
        primeiro_dia = max(data_inicial, rota.data_inicio)
        ultimo_dia = min(data_final, rota.data_fim)
        dias_configurados = set(rota.dias_semana.split(','))
        atual = primeiro_dia
        while atual <= ultimo_dia:
            if dias[atual.weekday()] in dias_configurados:
                existente = SolicitacaoViagem.query.filter_by(
                    rota_fixa_id=rota.id, data_agendada=atual
                ).first()
                if not existente:
                    db.session.add(SolicitacaoViagem(
                        motorista_nome=rota.motorista.nome,
                        motorista_id=rota.motorista_id,
                        rota_fixa_id=rota.id,
                        data_agendada=atual,
                        rota=rota.rota,
                        data_horario=f'{atual.isoformat()} {rota.horario_partida}',
                        veiculo=rota.veiculo,
                        status='Deferida'
                    ))
                    alterado = True
            atual += timedelta(days=1)

    if alterado:
        db.session.commit()


# ==============================================================================
# ROTAS DE AÇÕES AJAX (SERVIDORES)
# ==============================================================================

@admin_bp.route('/lista_servidores/aprovar/<int:id_servidor>', methods=['POST'])
def aprovar_servidor(id_servidor):
    if 'admin' not in session:
        return render_template('auth/principal.html')
    if ServidorDAO.aprovar(id_servidor):
        return jsonify({'sucesso': True, 'mensagem': 'Servidor aprovado com sucesso!'})
    return jsonify({'sucesso': False, 'erro': 'Servidor não encontrado no sistema.'}), 404

@admin_bp.route('/lista_servidores/excluir/<int:id_servidor>', methods=['POST'])
def excluir_servidor(id_servidor):
    if 'admin' not in session:
        return render_template('auth/principal.html')
    if ServidorDAO.excluir(id_servidor):
        return jsonify({'sucesso': True, 'mensagem': 'Servidor excluído com sucesso!'})
    return jsonify({'sucesso': False, 'erro': 'Servidor não encontrado no sistema.'}), 404

@admin_bp.route('/lista_servidores/inativar/<int:id_servidor>', methods=['POST'])
def inativar_servidor(id_servidor):
    if 'admin' not in session:
        return render_template('auth/principal.html')
    if ServidorDAO.inativar(id_servidor):
        return jsonify({'sucesso': True, 'mensagem': 'Servidor inativado com sucesso!'})
    return jsonify({'sucesso': False, 'erro': 'Servidor não encontrado no sistema.'}), 404


# ==============================================================================
# ROTAS DE AÇÕES AJAX (VIAGENS)
# ==============================================================================

@admin_bp.route('/pag_admin/deferir_viagem', methods=['POST'])
def deferir_viagem():
    if 'admin' not in session:
        return render_template('auth/principal.html')
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
        return render_template('auth/principal.html')
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
    consulta = SolicitacaoViagem.query.filter_by(status='Em Andamento')
    if 'admin' not in session:
        matricula_servidor = session.get('servidor')
        servidor = Servidor.query.filter_by(matricula=matricula_servidor).first() if matricula_servidor else None
        if not servidor:
            return jsonify({'erro': 'Não autorizado'}), 401
        consulta = consulta.filter_by(servidor_id=servidor.id)
    viagens_ativas = consulta.all()

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
        return render_template('auth/principal.html')
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
        return render_template('auth/principal.html')
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
        return render_template('auth/principal.html')
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
        return render_template('auth/principal.html')
    return render_template('admin/cadastrar_horario.html',
                           motoristas=Motorista.query.order_by(Motorista.nome).all(),
                           veiculos=Veiculo.query.order_by(Veiculo.prefixo).all())


@admin_bp.route('/api/horarios/cadastrar', methods=['POST'])
def cadastrar_horario():
    """Cadastra o horário enviado pela tela de viagens fixas."""
    if 'admin' not in session:
        return jsonify({'sucesso': False, 'erro': 'Não autorizado'}), 401

    dados = request.get_json(silent=True) or {}
    motorista_id = dados.get('motorista_id')
    try:
        motorista_id = int(motorista_id) if motorista_id else None
    except (TypeError, ValueError):
        motorista_id = None
    motorista = db.session.get(Motorista, motorista_id) if motorista_id else None
    if not motorista:
        nome_motorista = (dados.get('motorista') or '').strip()
        motorista = Motorista.query.filter_by(nome=nome_motorista).first() if nome_motorista else None
    rota = (dados.get('rota_nome') or '').strip()
    horario = (dados.get('horario_partida') or '').strip()
    horario_retorno = (dados.get('horario_retorno') or '').strip() or None
    dias = dados.get('dias_semana') or []
    veiculo_registro = (dados.get('veiculo') or '').strip()
    inicio = (dados.get('data_inicio') or '').strip()
    fim = (dados.get('data_fim') or '').strip()

    try:
        data_inicio = datetime.strptime(inicio, '%Y-%m-%d').date()
        data_fim = datetime.strptime(fim, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'sucesso': False, 'erro': 'Informe um período válido.'}), 400
    if data_fim < data_inicio:
        return jsonify({'sucesso': False, 'erro': 'A data final não pode ser anterior à inicial.'}), 400
    if not motorista or not rota or not veiculo_registro or not horario or not dias:
        return jsonify({'sucesso': False, 'erro': 'Informe motorista, rota, veículo, horário, período e pelo menos um dia.'}), 400

    rota_fixa = RotaFixa(
        motorista_id=motorista.id,
        rota=rota,
        veiculo=veiculo_registro,
        horario_partida=horario,
        horario_retorno=horario_retorno,
        dias_semana=','.join(dias),
        data_inicio=data_inicio,
        data_fim=data_fim,
        itinerario=(dados.get('itinerario') or '').strip()
    )
    db.session.add(rota_fixa)
    db.session.commit()
    return jsonify({'sucesso': True, 'id_rota_fixa': rota_fixa.id}), 201


@admin_bp.route('/list_viagem', methods=['GET'])
def cad_viagem():
    if 'admin' not in session:
        return render_template('auth/principal.html')

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

    return render_template('admin/listar_viagens.html', viagens=viagens_processadas)


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
        motorista_id = dados.get('motorista_id')
        motorista = db.session.get(Motorista, motorista_id) if motorista_id else None
        if not motorista:
            return jsonify({"erro": "Selecione um motorista para a viagem"}), 400

        nova_viagem = SolicitacaoViagem(
            motorista_nome=motorista.nome,
            motorista_id=motorista.id,
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
    cpf = dados.get('cpf', '').strip()
    senha = dados.get('senha', '')
    if not cpf or not senha:
        return jsonify({"sucesso": False, "erro": "CPF e senha são obrigatórios"}), 400
    if Motorista.query.filter_by(cpf=cpf).first():
        return jsonify({"sucesso": False, "erro": "Já existe motorista cadastrado com este CPF"}), 409

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
        senha=senha,
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
                "senha_provisoria": senha
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": f"Erro interno ao salvar no banco: {str(e)}"}), 500
