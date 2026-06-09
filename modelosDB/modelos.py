# modelosDB/modelos.py
from extensions import db

class Servidor(db.Model):
    __tablename__ = 'servidor'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    matricula = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)  # Removido unique=True
    cargo = db.Column(db.String(100), default='Servidor')
    status = db.Column(db.String(50), default='Pendente')  # Usado para substituir o '.aprovado'

    def __repr__(self):
        return f'<Servidor {self.nome}>'

    def __init__(self, nome, email, matricula, senha, cargo, status):
        self.nome = nome
        self.email = email
        self.matricula = matricula
        self.senha = senha
        self.cargo = cargo
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
    nome = db.Column(db.String(100), nullable=False)
    cnh = db.Column(db.String(20), unique=True, nullable=False)
    categoria = db.Column(db.String(5), nullable=False)
    validade_cnh = db.Column(db.String(20), nullable=False)

    def __init__(self, matricula, nome, cnh, categoria, validade_cnh):
        self.matricula = matricula
        self.nome = nome
        self.cnh = cnh
        self.categoria = categoria
        self.validade_cnh = validade_cnh


class SolicitacaoViagem(db.Model):
    __tablename__ = 'solicitacoes_viagem'

    id = db.Column(db.Integer, primary_key=True)
    servidor_id = db.Column(db.Integer, db.ForeignKey('servidor.id')) # Relacionamento
    motorista_nome = db.Column(db.String(100), nullable=False)
    rota = db.Column(db.String(200), nullable=False)
    data_horario = db.Column(db.String(50), nullable=False)
    veiculo = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Pendente')

    def __init__(self, motorista_nome, rota, data_horario, veiculo, status):
        self.motorista_nome = motorista_nome
        self.rota = rota
        self.data_horario = data_horario
        self.veiculo = veiculo
        self.status = status