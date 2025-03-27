import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Função para calcular a receita bruta mensal
def calcular_receita_bruta(mensalidades):
    return sum(mensalidades)

# Função para calcular as despesas mensais
def calcular_despesas_mensais(despesas):
    return sum(despesas)

# Função para calcular o custo por contrato com clientes
def calcular_custo_por_contrato(despesas, contratos):
    if contratos == 0:
        return 0
    return despesas / contratos

# Função para gerar o gráfico
def gerar_grafico(receita_bruta, despesas_mensais, custo_contrato):
    # Criando os dados para o gráfico
    categorias = ['Receita Bruta', 'Despesas Mensais', 'Custo por Contrato']
    valores = [receita_bruta, despesas_mensais, custo_contrato]
    
    # Criando o gráfico de barras
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(categorias, valores, color=['green', 'red', 'blue'])
    ax.set_title('Análise Financeira')
    ax.set_ylabel('Valor (R$)')
    
    # Inserindo o gráfico na interface Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

# Função que será chamada ao clicar no botão "Calcular"
def calcular():
    try:
        # Obter os dados da interface
        mensalidades = list(map(float, entry_mensalidades.get().split()))
        despesas = list(map(float, entry_despesas.get().split()))
        contratos = int(entry_contratos.get())
        
        # Realizar os cálculos
        receita_bruta = calcular_receita_bruta(mensalidades)
        despesas_mensais = calcular_despesas_mensais(despesas)
        custo_contrato = calcular_custo_por_contrato(despesas_mensais, contratos)
        
        # Exibir os resultados na interface
        resultado_receita.config(text=f"Receita Bruta Mensal: R${receita_bruta:.2f}")
        resultado_despesas.config(text=f"Despesas Mensais: R${despesas_mensais:.2f}")
        resultado_custo.config(text=f"Custo por Contrato com Clientes: R${custo_contrato:.2f}")
        
        # Gerar o gráfico
        gerar_grafico(receita_bruta, despesas_mensais, custo_contrato)
    
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira dados válidos.")

# Criando a janela principal
root = tk.Tk()
root.title("Cálculos Financeiros - Agência de Publicidade")

# Definindo o tamanho da janela e o fundo
root.geometry("500x600")
root.config(bg="#f4f4f9")

# Estilo de fonte
font_padrao = ("Arial", 12)
font_resultados = ("Arial", 10, "bold")

# Adicionando widgets para entrada de dados
label_mensalidades = tk.Label(root, text="Mensalidades dos contratos (separadas por espaço):", font=font_padrao, bg="#f4f4f9")
label_mensalidades.pack(pady=10)

entry_mensalidades = tk.Entry(root, width=40, font=font_padrao, bd=2, relief="solid")
entry_mensalidades.pack(pady=5)

label_despesas = tk.Label(root, text="Despesas mensais (separadas por espaço):", font=font_padrao, bg="#f4f4f9")
label_despesas.pack(pady=10)

entry_despesas = tk.Entry(root, width=40, font=font_padrao, bd=2, relief="solid")
entry_despesas.pack(pady=5)

label_contratos = tk.Label(root, text="Número de contratos:", font=font_padrao, bg="#f4f4f9")
label_contratos.pack(pady=10)

entry_contratos = tk.Entry(root, width=40, font=font_padrao, bd=2, relief="solid")
entry_contratos.pack(pady=5)

# Botão para calcular
btn_calcular = tk.Button(root, text="Calcular", command=calcular, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", relief="raised", bd=2)
btn_calcular.pack(pady=20)

# Labels para exibir os resultados
resultado_receita = tk.Label(root, text="Receita Bruta Mensal: R$0.00", font=font_resultados, bg="#f4f4f9")
resultado_receita.pack(pady=5)

resultado_despesas = tk.Label(root, text="Despesas Mensais: R$0.00", font=font_resultados, bg="#f4f4f9")
resultado_despesas.pack(pady=5)

resultado_custo = tk.Label(root, text="Custo por Contrato com Clientes: R$0.00", font=font_resultados, bg="#f4f4f9")
resultado_custo.pack(pady=5)

# Iniciando o loop da interface
root.mainloop()
