from extensions import db
from modelosDB.modelos import Servidor
from sqlalchemy.exc import IntegrityError

class ServidorDAO:

    @staticmethod
    def salvar(nome, email, matricula, senha):
        try:
            # O status padrão ao cadastrar costuma ser 'Pendente'
            novo_servidor = Servidor(nome=nome, email=email, matricula=matricula, senha=senha, status='Pendente')
            db.session.add(novo_servidor)
            db.session.commit()
            return novo_servidor
        except IntegrityError:
            # Faz o rollback se tentar salvar uma matrícula que já existe
            db.session.rollback()
            return None

    @staticmethod
    def listar():
        return Servidor.query.all()

    @staticmethod
    def excluir(id_servidor):
        servidor = Servidor.query.get(id_servidor)
        if servidor:
            db.session.delete(servidor)
            db.session.commit()
            return True
        return False

    @staticmethod
    def aprovar(id_servidor):
        servidor = Servidor.query.get(id_servidor)
        if servidor:
            servidor.status = 'Ativo'  # Atualiza o status para Ativo
            db.session.commit()
            return True
        return False

    @staticmethod
    def buscar_por_matricula(matricula):
        return Servidor.query.filter_by(matricula=matricula).first()

    @staticmethod
    def autenticar(matricula, senha):
        return Servidor.query.filter_by(matricula=matricula, senha=senha).first()