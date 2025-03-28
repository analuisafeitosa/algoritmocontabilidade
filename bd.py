import sqlite3
# Reabrir a conexão
conn = sqlite3.connect('movimentacao_bancaria.db')
cursor = conn.cursor()

# Consultar todos os dados da tabela
cursor.execute('SELECT * FROM movimentacao_bancaria')
rows = cursor.fetchall()

# Exibir o resultado
for row in rows:
    print(row)

# Fechar a conexão
conn.close()
