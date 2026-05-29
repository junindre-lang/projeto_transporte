class Veiculo:
    def __init__(self, prefixo, modelo, placa, capacidade, status):
        self.__prefixo = prefixo
        self.__modelo = modelo
        self.__placa = placa
        self.__capacidade = capacidade
        self.__status = status

    def get_prefixo(self):
        return self.__prefixo

    def get_modelo(self):
        return self.__modelo

    def get_placa(self):
        return self.__placa

    def get_capacidade(self):
        return self.__capacidade

    def get_status(self):
        return self.__status

