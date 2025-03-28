import sqlite3
import pandas as pd

# Função para calcular a Receita Bruta Mensal, Despesa Mensal e Custo por Contrato
def calcular_metrics(db_path):
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect(db_path)
    
    # 1. Receita Bruta Mensal: Somar as entradas por mês
    query_receita_bruta = '''
        SELECT strftime('%Y-%m', Data) AS Mes, SUM(Entrada) AS Receita_Bruta
        FROM movimentacao_bancaria
        GROUP BY strftime('%Y-%m', Data)
    '''
    receita_bruta_mensal = pd.read_sql_query(query_receita_bruta, conn)

    # 2. Despesa Mensal: Somar as saídas por mês
    query_despesa_mensal = '''
        SELECT strftime('%Y-%m', Data) AS Mes, SUM(Saida) AS Despesa
        FROM movimentacao_bancaria
        GROUP BY strftime('%Y-%m', Data)
    '''
    despesa_mensal = pd.read_sql_query(query_despesa_mensal, conn)

    # 3. Custo por Contrato de Clientes: Média das entradas por contrato (Nome Natureza)
    query_custo_por_contrato = '''
        SELECT "Nome Natureza", AVG(Entrada) AS Custo_Por_Contrato
        FROM movimentacao_bancaria
        GROUP BY "Nome Natureza"
    '''
    custo_por_contrato = pd.read_sql_query(query_custo_por_contrato, conn)

    # Fechar a conexão com o banco de dados
    conn.close()

    # Exibindo os resultados
    return receita_bruta_mensal, despesa_mensal, custo_por_contrato

# Caminho para o banco de dados SQLite
db_path = r'C:\Users\analu\OneDrive\Área de Trabalho\algoritmo de contabilidade\algoritmocontabilidade\movimentacao_bancaria.db'

# Calcular as métricas
receita_bruta, despesa_mensal, custo_por_contrato = calcular_metrics(db_path)

# Exibindo os resultados para revisão
print("Receita Bruta Mensal:")
print(receita_bruta)

print("\nDespesa Mensal:")
print(despesa_mensal)

print("\nCusto por Contrato de Clientes:")
print(custo_por_contrato)
