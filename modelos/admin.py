class Admin:
    def __init__(self, senha, matricula):
        self.__senha = senha
        self.__matricula = matricula


    def get_senha(self):
        return self.__senha

    def get_matricula(self):
        return self.__matricula
