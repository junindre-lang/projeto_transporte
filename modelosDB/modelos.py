from extensions import db

class Servidor(db.Model):
    __tablename__ = 'servidor'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    matricula = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)  # Removido unique=True
    status = db.Column(db.String(50), default='Pendente')  # Usado para substituir o '.aprovado'

    def __repr__(self):
        return f'<Servidor {self.nome}>'

    def __init__(self, nome, email, matricula, senha, status):
        self.nome = nome
        self.email = email
        self.matricula = matricula
        self.senha = senha
        self.status = status


class Veiculo(db.Model):
    __tablename__ = 'veiculos'

    id = db.Column(db.Integer, primary_key=True)
    prefixo = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    placa = db.Column(db.String(20), unique=True, nullable=False)
    capacidade = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Disponível')

    def __init__(self, prefixo, modelo, placa, capacidade, status):
        self.prefixo = prefixo
        self.modelo = modelo
        self.placa = placa
        self.capacidade = capacidade
        self.status = status


class Motorista(db.Model):
    __tablename__ = 'motoristas'

    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(15), nullable=True)  # Opcional no cadastro inicial
    nome = db.Column(db.String(100), nullable=False)
    cnh = db.Column(db.String(20), unique=True, nullable=True)  # Opcional no cadastro rápido
    categoria = db.Column(db.String(5), nullable=True)  # Opcional no cadastro rápido
    validade_cnh = db.Column(db.String(50), nullable=True)

    # NOVAS COLUNAS ADICIONADAS PARA SUPORTAR O CADASTRO DO ADMIN:
    cpf = db.Column(db.String(20), unique=True, nullable=True)
    status = db.Column(db.String(50), default='Indisponível')

    # Construtor atualizado e ultra flexível para aceitar todos os formatos de cadastro
    def __init__(self, matricula, nome, senha=None, cnh=None, categoria=None, validade_cnh=None, cpf=None,
                 status='Indisponível'):
        self.matricula = matricula
        self.nome = nome
        self.senha = senha
        self.cnh = cnh
        self.categoria = categoria
        self.validade_cnh = validade_cnh
        self.cpf = cpf
        self.status = status


class SolicitacaoViagem(db.Model):
    __tablename__ = 'solicitacoes_viagem'

    id = db.Column(db.Integer, primary_key=True)
    servidor_id = db.Column(db.Integer, db.ForeignKey('servidor.id')) # Relacionamento
    # A viagem pertence a um motorista cadastrado. O nome é mantido para
    # compatibilidade com os registros e telas já existentes.
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'), nullable=True)
    motorista_nome = db.Column(db.String(100), nullable=False)
    rota = db.Column(db.String(200), nullable=False)
    data_horario = db.Column(db.String(50), nullable=False)
    veiculo = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Pendente')

    def __init__(self, motorista_nome, rota, data_horario, veiculo, status, motorista_id=None):
        self.motorista_id = motorista_id
        self.motorista_nome = motorista_nome
        self.rota = rota
        self.data_horario = data_horario
        self.veiculo = veiculo
        self.status = status


class CoordenadaRota(db.Model):
    __tablename__ = 'coordenadas_rota'

    id = db.Column(db.Integer, primary_key=True)
    viagem_id = db.Column(db.Integer, db.ForeignKey('solicitacoes_viagem.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    ordem = db.Column(db.Integer, nullable=False)  # Garante a sequência correta do trajeto

    # Relacionamento com a tabela de viagens
    viagem = db.relationship('SolicitacaoViagem', backref=db.backref('pontos_rota', lazy=True))
