from extensions import db
from modelosDB.modelos import Veiculo
from sqlalchemy.exc import IntegrityError

class Veiculo_DAO:

    @staticmethod
    def salvar(prefixo, modelo, placa, capacidade, status):
        try:
            # O status padrão ao cadastrar costuma ser 'Pendente'
            novo_Veiculo = Veiculo(prefixo=prefixo, modelo=modelo, placa=placa, capacidade=capacidade, status=status)
            db.session.add(novo_Veiculo)
            db.session.commit()
            return novo_Veiculo
        except IntegrityError:
            # Faz o rollback se tentar salvar uma matrícula que já existe
            db.session.rollback()
            return None

    @staticmethod
    def listar_todos():
        return Veiculo.query.all()

    @staticmethod
    def buscar_por_marca(modelo):
        return Veiculo.query.filter_by(modelo=modelo).first()

    @staticmethod
    def buscar_por_status(status):
        return Veiculo.query.filter_by(status=status).first()

    @staticmethod
    def editar(prefixo, modelo, placa, capacidade, status=None):
        try:
            # 1. Busca o veículo existente pelo prefixo (ou id, caso use id)
            veiculo = Veiculo.query.filter_by(prefixo=prefixo).first()
            if not veiculo:
                return None
            veiculo.modelo = modelo
            veiculo.placa = placa
            veiculo.capacidade = capacidade

            if status is not None:
                veiculo.status = status

            db.session.commit()
            return veiculo

        except IntegrityError:
            # Caso a edição cause algum conflito (ex: mudar a placa para uma que já existe)
            db.session.rollback()
            return None
