import dash
from dash import dcc, html
import pandas as pd
import sqlite3
import plotly.express as px
from algoritmo import db_path

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

    return receita_bruta_mensal, despesa_mensal, custo_por_contrato

# Caminho para o banco de dados SQLite
db_path = r'C:\Users\analu\OneDrive\Área de Trabalho\algoritmo de contabilidade\algoritmocontabilidade\movimentacao_bancaria.db'

# Calcular as métricas
receita_bruta, despesa_mensal, custo_por_contrato = calcular_metrics(db_path)

# Criar a aplicação Dash
app = dash.Dash(__name__)

# Agrupar os menores custos por contrato em "Outros"
threshold = 5  # Limite do valor para considerar um contrato como "Outros"
custo_por_contrato['Custo_Por_Contrato'] = custo_por_contrato['Custo_Por_Contrato'].fillna(0)
custo_por_contrato['Categoria'] = custo_por_contrato['Custo_Por_Contrato'].apply(
    lambda x: 'Outros' if x < threshold else 'Significativo'
)

# Agrupar para manter apenas as categorias significativas
significant_categories = custo_por_contrato[custo_por_contrato['Categoria'] == 'Significativo']
other_categories = custo_por_contrato[custo_por_contrato['Categoria'] == 'Outros']

# Somar os valores das categorias "Outros"
other_sum = other_categories['Custo_Por_Contrato'].sum()

# Criando o DataFrame para "Outros"
outros_df = pd.DataFrame({
    'Nome Natureza': ['Outros'],
    'Custo_Por_Contrato': [other_sum],
    'Categoria': ['Outros']
})

# Concatenar as categorias significativas com os "Outros"
significant_categories = pd.concat([significant_categories, outros_df], ignore_index=True)

# Criar o gráfico de pizza
pie_fig = px.pie(
    significant_categories, 
    names='Nome Natureza', 
    values='Custo_Por_Contrato',
    title="Distribuição do Custo por Contrato",
    hole=0.3  # Fazer o gráfico de pizza com um "buraco" no centro (estilo donut)
)

# Ajustar o tamanho da fonte
pie_fig.update_traces(textinfo="percent+label", pull=[0.1]*len(significant_categories))

# Layout da aplicação
app.layout = html.Div([
    html.H1("Dashboard de Movimentação Bancária", style={
        'text-align': 'center', 
        'font-family': 'Arial, sans-serif', 
        'color': '#333'
    }),

    # Gráfico de Receita Bruta Mensal
    dcc.Graph(
        id='grafico-receita-bruta',
        figure=px.bar(receita_bruta, x='Mes', y='Receita_Bruta', title="Receita Bruta Mensal")
    ),
    
    # Gráfico de Despesa Mensal
    dcc.Graph(
        id='grafico-despesa',
        figure=px.bar(despesa_mensal, x='Mes', y='Despesa', title="Despesa Mensal")
    ),
    
    # Gráfico de Custo por Contrato
    dcc.Graph(
        id='grafico-custo-por-contrato',
        figure=px.bar(custo_por_contrato, x='Nome Natureza', y='Custo_Por_Contrato', title="Custo por Contrato de Clientes")
    ),

    # Gráfico de Pizza para Custo por Contrato
    dcc.Graph(
        id='grafico-pizza-custo',
        figure=pie_fig
    )
])

# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)
