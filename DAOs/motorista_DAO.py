from extensions import db
from modelosDB.modelos import Motorista
from sqlalchemy.exc import IntegrityError

class Motorista_DAO:

    @staticmethod
    def salvar( matricula, senha, nome, cnh, categoria):
        try:
            # O status padrão ao cadastrar costuma ser 'Pendente'
            novo_motora = Motorista( matricula=matricula,senha=senha, nome=nome, cnh=cnh, categoria=categoria)
            db.session.add(novo_motora)
            db.session.commit()
            return novo_motora
        except IntegrityError:
            # Faz o rollback se tentar salvar uma matrícula que já existe
            db.session.rollback()
            return None

    @staticmethod
    def iniciar_viagem():
        pass
