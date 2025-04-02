import dash
from dash import dcc, html
import pandas as pd
import sqlite3
import plotly.express as px

# Função para calcular as métricas, incluindo Lucro Bruto e Lucro Líquido
def calcular_metrics(db_path):
    conn = sqlite3.connect(db_path)

    # Receita Bruta Mensal: entrada > 0 e saida = 0
    query_receita_bruta = '''
        SELECT strftime('%Y-%m', Data) AS Mes, SUM(Entrada) AS Receita_Bruta
        FROM movimentacao_bancaria
        WHERE Entrada > 0 AND (Saida = 0 OR Saida IS NULL)
        GROUP BY strftime('%Y-%m', Data)
    '''
    receita_bruta_mensal = pd.read_sql_query(query_receita_bruta, conn)

    # Despesa Mensal: saida > 0 e entrada = 0
    query_despesa_mensal = '''
        SELECT strftime('%Y-%m', Data) AS Mes, SUM(Saida) AS Despesa
        FROM movimentacao_bancaria
        WHERE Saida > 0 AND (Entrada = 0 OR Entrada IS NULL)
        GROUP BY strftime('%Y-%m', Data)
    '''
    despesa_mensal = pd.read_sql_query(query_despesa_mensal, conn)

    # Custo por Contrato: média das saídas por contrato (quando entrada = 0 ou null)
    query_custo_por_contrato = '''
        SELECT "Nome Natureza", AVG(Saida) AS Custo_Por_Contrato
        FROM movimentacao_bancaria
        WHERE (Entrada = 0 OR Entrada IS NULL) AND Saida > 0
        GROUP BY "Nome Natureza"
    '''
    custo_por_contrato = pd.read_sql_query(query_custo_por_contrato, conn)

    lucro_bruto = receita_bruta_mensal['Receita_Bruta'].sum() - despesa_mensal['Despesa'].sum()
    lucro_liquido = lucro_bruto

    conn.close()
    print("Custo por contrato (filtrado):")
    print(custo_por_contrato)

    return receita_bruta_mensal, despesa_mensal, custo_por_contrato, lucro_bruto, lucro_liquido

# Caminho para o banco de dados SQLite
db_path = r'C:\Users\analu\OneDrive\Área de Trabalho\algoritmo de contabilidade\algoritmocontabilidade\movimentacao_bancaria.db'

# Calcular as métricas
receita_bruta, despesa_mensal, custo_por_contrato, lucro_bruto, lucro_liquido = calcular_metrics(db_path)

# Filtrando os dados para mostrar apenas valores maiores que 0 nos gráficos de barra
receita_bruta = receita_bruta[receita_bruta['Receita_Bruta'] > 0]
despesa_mensal = despesa_mensal[despesa_mensal['Despesa'] > 0]
custo_por_contrato = custo_por_contrato[custo_por_contrato['Custo_Por_Contrato'] > 0]

# Criar a aplicação Dash
app = dash.Dash(__name__)

# Cores mais neutras e profissionais para relatório contábil
cor_receita = '#2E8B57'  # verde escuro
cor_despesa = '#B22222'  # vermelho escuro
cor_custo = '#4682B4'    # azul meio cinza

# Gráficos com cores definidas
fig_receita = px.bar(receita_bruta, x='Mes', y='Receita_Bruta', title="Receita Bruta Mensal")
fig_receita.update_traces(marker_color=cor_receita)

fig_despesa = px.bar(despesa_mensal, x='Mes', y='Despesa', title="Despesa Mensal")
fig_despesa.update_traces(marker_color=cor_despesa)

fig_custo = px.bar(custo_por_contrato, x='Nome Natureza', y='Custo_Por_Contrato', title="Custo por Contrato de Clientes")
fig_custo.update_traces(marker_color=cor_custo)

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
        figure=fig_receita
    ),

    # Gráfico de Despesa Mensal
    dcc.Graph(
        id='grafico-despesa',
        figure=fig_despesa
    ),

    # Gráfico de Custo por Contrato
    dcc.Graph(
        id='grafico-custo-por-contrato',
        figure=fig_custo
    )
])

# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)
