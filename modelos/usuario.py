class Usuario:
    def __init__(self, nome, matricula, senha):
        self.__nome = nome
        self.__matricula = matricula
        self.__senha = senha


    def get_nome(self):
        return self.__nome

    def get_matricula(self):
        return self.__matricula

    def get_senha(self):
        return self.__senha