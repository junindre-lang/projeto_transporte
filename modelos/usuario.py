class Usuario:
    def __init__(self, nome, email, matricula, senha, senha1 ):
        self.__nome = nome
        self.__email= email
        self.__matricula = matricula
        self.__senha = senha
        self.__senha1 = senha1


    def get_nome(self):
        return self.__nome

    def get_email(self):
        return self.__email

    def get_matricula(self):
        return self.__matricula

    def get_senha(self):
        return self.__senha

    def get_senha1(self):
        return self.__senha1