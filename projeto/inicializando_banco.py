import mysql.connector  # pip install mysql-connector-python
from mysql.connector import errorcode

print("CONECTANDO...")

try:
    conectar = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='darc147'
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('Existe algo errado no nome de usuário ou senha.')
    else:
        print(err)


cursor = conectar.cursor()


"""
-> A função `mysql.connector.connect()` tenta estabelecer uma conexão com o banco de dados.

-> `errorcode.ER_ACCESS_DENIED_ERROR`: Verifica se o erro é de acesso negado, o que pode 
    ocorrer se o nome de usuário ou senha estiverem errados.

-> `conectar.cursor()`: Após a conexão ser estabelecida, você cria um cursor, que é um objeto 
    usado para interagir com o banco de dados. Com ele, você pode executar comandos SQL, como SELECT, INSERT, UPDATE, DELETE, entre outros.
"""


# Caso a tabela já exista, o comando abaixo irá apaga-lá
cursor.execute("DROP DATABASE IF EXIST `workforce`;")

# Criando a base de dados e usando-a
cursor.execute("CREATE DATABASE `workforce`;")
cursor.execute("USE `workforce`;")
