import sqlite3 as sql

def initializeSchema():
    database = sql.connect('database.db', check_same_thread=False)
    cursor = database.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS veiculo (matricula VARCHAR(10) PRIMARY KEY, data_contracto DATETIME);''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS passagem (id INTEGER PRIMARY KEY AUTOINCREMENT, data_passagem DATETIME, veiculo_id VARCHAR(10), FOREIGN KEY(veiculo_id) REFERENCES veiculo(matricula));''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS multa (id INTEGER PRIMARY KEY AUTOINCREMENT, matricula VARCHAR(10), valor FLOAT, passagem_id INTEGER, BOOLEAN pago, FOREIGN KEY(passagem_id) REFERENCES passagem(id));''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pagamento (id INTEGER PRIMARY KEY AUTOINCREMENT, data_pagamento DATETIME, valor FLOAT, multa_id INTEGER, FOREIGN KEY(multa_id) REFERENCES multa(id));''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS carro_nao_lido (image_path TEXT PRIMARY KEY, passagem_id INTEGER, FOREIGN KEY(passagem_id) REFERENCES passagem);''')

 #   cursor.execute('''CREATE TRIGGER IF NOT EXISTS passagem_trigger AFTER INSERT ON passagem
 #   BEGIN
 #   UPDATE passagem SET valido = (SELECT veiculo_id FROM veiculo WHERE veiculo_id = NEW.veiculo_id) IS NOT NULL WHERE id = NEW.id;
 #   END;''')

    database.commit()
    cursor.close()
    database.close()

class Database:

    __database = sql.connect('database.db', check_same_thread=False)
    __cursor = __database.cursor()

    def checkCar(self, matricula):
        self.__cursor.execute('''SELECT * FROM veiculo WHERE matricula = ?''', (matricula,))
        return self.__cursor.fetchone() is not None

    def insertCar(self, matricula, data_contracto):
        self.__cursor.execute('''INSERT INTO veiculo (matricula, data_contracto) VALUES (?, ?)''', (matricula, data_contracto))
        self.__database.commit()

    def insertPassagem(self, veiculo_id, data_passagem):
        self.__cursor.execute('''INSERT INTO passagem (veiculo_id, data_passagem) VALUES (?, ?)''', (veiculo_id, data_passagem))
        self.__database.commit()
        return self.__cursor.lastrowid

    def insertMulta(self, passagem_id, matricula, valor, pago):
        self.__cursor.execute('''INSERT INTO multa (passagem_id, matricula, valor, pago) VALUES (?, ?, ?, ?)''', (passagem_id, matricula, valor, pago))
        self.__database.commit()

    def insertCarroNaoLido(self, image_path, passagem_id):
        self.__cursor.execute('''INSERT INTO carro_nao_lido (image_path, passagem_id) VALUES (?, ?)''', (image_path, passagem_id))
        self.__database.commit()