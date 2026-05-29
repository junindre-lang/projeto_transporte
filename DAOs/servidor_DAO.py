from modelosDB.servidoresDB import *
from modelos.usuario import *


class ServidorDAO:

    @staticmethod
    def __init__(self, matricula, nome, email, senha, senha1):
        login = Usuario(matricula=matricula, nome=nome, email=email, senha=senha, senha1=senha1 )
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