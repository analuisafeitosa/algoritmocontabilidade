import dash
from dash import dcc, html
import pandas as pd
import sqlite3
import plotly.express as px

# Função para calcular as métricas, incluindo Lucro Bruto e Lucro Líquido
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

    # 4. Calcular Lucro Bruto e Lucro Líquido
    lucro_bruto = receita_bruta_mensal['Receita_Bruta'].sum() - despesa_mensal['Despesa'].sum()
    lucro_liquido = lucro_bruto  # Aqui você pode subtrair outras despesas se tiver os dados

    # Fechar a conexão com o banco de dados
    conn.close()

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
    hole=0.2  # Fazer o gráfico de pizza com um "buraco" no centro (estilo donut)
)

def update_graphs(ordenar_por, ordem):
    # Ordenar os dados conforme a escolha do usuário
    if ordenar_por == 'Receita_Bruta':
        df_receita = receita_bruta
        df_receita = df_receita.sort_values(by='Receita_Bruta', ascending=(ordem == 'asc'))
        fig_receita = px.bar(df_receita, x='Mes', y='Receita_Bruta', title="Receita Bruta Mensal")
    
    elif ordenar_por == 'Despesa':
        df_despesa = despesa_mensal
        df_despesa = df_despesa.sort_values(by='Despesa', ascending=(ordem == 'asc'))
        fig_despesa = px.bar(df_despesa, x='Mes', y='Despesa', title="Despesa Mensal")
    
    else:
        df_custo = custo_por_contrato
        df_custo = df_custo.sort_values(by='Custo_Por_Contrato', ascending=(ordem == 'asc'))
        fig_custo = px.bar(df_custo, x='Nome Natureza', y='Custo_Por_Contrato', title="Custo por Contrato de Clientes")

    return fig_receita, fig_despesa, fig_custo
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
