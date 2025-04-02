import dash
from dash import dcc, html
import pandas as pd
import sqlite3
import plotly.express as px

# Função para calcular as métricas com a nova lógica de entrada/saída

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

# Caminho para o banco de dados
db_path = r'C:\Users\analu\OneDrive\Área de Trabalho\algoritmo de contabilidade\algoritmocontabilidade\movimentacao_bancaria.db'

receita_bruta, despesa_mensal, custo_por_contrato, lucro_bruto, lucro_liquido = calcular_metrics(db_path)

receita_bruta = receita_bruta[receita_bruta['Receita_Bruta'] > 0]
despesa_mensal = despesa_mensal[despesa_mensal['Despesa'] > 0]
custo_por_contrato = custo_por_contrato[custo_por_contrato['Custo_Por_Contrato'] > 0]

# Preparar dados de custo para os gráficos (apenas registros com Entrada = 0 ou NULL e Saida > 0)
thresh = 5
custo_por_contrato['Categoria'] = custo_por_contrato['Custo_Por_Contrato'].apply(
    lambda x: 'Outros' if x < thresh else 'Significativo'
)

significant_categories = custo_por_contrato[custo_por_contrato['Categoria'] == 'Significativo']
other_categories = custo_por_contrato[custo_por_contrato['Categoria'] == 'Outros']
other_sum = other_categories['Custo_Por_Contrato'].sum()

outros_df = pd.DataFrame({
    'Nome Natureza': ['Outros'],
    'Custo_Por_Contrato': [other_sum],
    'Categoria': ['Outros']
})

significant_categories = pd.concat([significant_categories, outros_df], ignore_index=True)

pie_fig = px.pie(
    significant_categories,
    names='Nome Natureza',
    values='Custo_Por_Contrato',
    title="Distribuição do Custo por Contrato",
    hole=0.2
)

pie_fig.update_traces(textinfo="percent+label", pull=[0.1]*len(significant_categories))

def update_graphs(ordenar_por, ordem):
    if ordenar_por == 'Receita_Bruta':
        df_receita = receita_bruta.sort_values(by='Receita_Bruta', ascending=(ordem == 'asc'))
        fig_receita = px.bar(df_receita, x='Mes', y='Receita_Bruta', title="Receita Bruta Mensal")
    elif ordenar_por == 'Despesa':
        df_despesa = despesa_mensal.sort_values(by='Despesa', ascending=(ordem == 'asc'))
        fig_despesa = px.bar(df_despesa, x='Mes', y='Despesa', title="Despesa Mensal")
    else:
        df_custo = custo_por_contrato.sort_values(by='Custo_Por_Contrato', ascending=(ordem == 'asc'))
        fig_custo = px.bar(df_custo, x='Nome Natureza', y='Custo_Por_Contrato', title="Custo por Contrato de Clientes")
    return fig_receita, fig_despesa, fig_custo

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de Movimentação Bancária", style={
        'text-align': 'center',
        'font-family': 'Arial, sans-serif',
        'color': '#333'
    }),

    dcc.Graph(
        id='grafico-receita-bruta',
        figure=px.bar(receita_bruta, x='Mes', y='Receita_Bruta', title="Receita Bruta Mensal")
    ),

    dcc.Graph(
        id='grafico-despesa',
        figure=px.bar(despesa_mensal, x='Mes', y='Despesa', title="Despesa Mensal")
    ),

    dcc.Graph(
        id='grafico-custo-por-contrato',
        figure=px.bar(significant_categories, x='Nome Natureza', y='Custo_Por_Contrato', title="Custo por Contrato de Clientes")
    ),

    dcc.Graph(
        id='grafico-pizza-custo',
        figure=pie_fig
    )
])

if __name__ == '__main__':
    app.run(debug=True)
