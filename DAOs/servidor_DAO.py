from modelosDB.servidoresDB import *
from servidor import *


class ServidorDAO:

    @staticmethod
    def salvar(matricula, senha):
        login = Servidor(matricula=matricula, senha=senha)
        db.session.add(login)
        db.session.commit()

        return login

    @staticmethod
    def listar():
        return Servidor.query.all()

    @staticmethod
    def excluir(id):
        return Servidor.query.delete(id=id)

    @staticmethod
    def buscar_por_matricula(matricula):
        return Servidor.query.filter_by(matricula=matricula).first()

    @staticmethod
    def autenticar(matricula, senha):
        return Servidor.query.filter_by(matricula=matricula, senha=senha).first()

