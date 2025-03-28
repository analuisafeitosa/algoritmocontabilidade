import sqlite3

# Verificar as colunas da tabela para corrigir qualquer erro
conn = sqlite3.connect('movimentacao_bancaria.db')
cursor = conn.cursor()

# Consultar os nomes das colunas na tabela
cursor.execute('PRAGMA table_info(movimentacao_bancaria)')
columns = cursor.fetchall()

# Exibir os nomes das colunas
for column in columns:
    print(column)  # Isso vai imprimir as colunas na sua saída

# Fechar a conexão
conn.close()

# Agora você pode colocar o restante do código que vai fazer o cálculo
# Coloque aqui seu código normal após essa verificação
