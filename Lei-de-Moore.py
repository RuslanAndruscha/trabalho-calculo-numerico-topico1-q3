import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# --- LÓGICA MATEMÁTICA PASSO A PASSO (Baseada nos Slides) ---

def calcular_mmq_detalhado():
    """
    Realiza o MMQ construindo manualmente o Sistema Normal.
    Baseado no Slide 44 e 45 do material.
    """
    # 1. Dados Originais
    x = np.array([1971, 1972, 1974, 1978, 1982, 1986, 1989, 1993, 1997, 1999, 2000], dtype=float)
    N = np.array([2250, 3300, 6000, 29000, 134000, 275000, 1200000, 3100000, 7500000, 9500000, 42000000], dtype=float)
    n_pontos = len(x)

    # 2. Linearização (Slide 38/44)
    # Modelo: N = alpha * 10^(beta * t)
    # Linear: log10(N) = log10(alpha) + beta * t
    # Y = B + A * X
    y_log = np.log10(N)

    # 3. Cálculo dos Somatórios (Tabela do Slide 45)
    sum_x = np.sum(x)
    sum_x2 = np.sum(x ** 2)
    sum_y = np.sum(y_log)
    sum_xy = np.sum(x * y_log)

    # 4. Montagem do Sistema Normal (Slide 44/494)
    # Sistema na forma:
    # [ n      sum_x  ] [ B ] = [ sum_y  ]
    # [ sum_x  sum_x2 ] [ A ] = [ sum_xy ]
    # Onde B é o coeficiente linear (intercepto) e A é o angular (inclinação)

    matriz_coeficientes = np.array([[n_pontos, sum_x],
                                    [sum_x, sum_x2]])

    vetor_termos_indep = np.array([sum_y, sum_xy])

    # 5. Resolução do Sistema Linear
    # Resolvemos para encontrar [B, A]
    solucao = np.linalg.solve(matriz_coeficientes, vetor_termos_indep)

    B_linear = solucao[0]  # log10(alpha)
    A_angular = solucao[1]  # beta

    # 6. Retorno aos parâmetros originais
    alpha = 10 ** B_linear
    beta = A_angular

    # Retorna dados para plotagem e string de memória de cálculo
    detalhes_calculo = (
        f"PASSO 1: TABELA DE SOMATÓRIOS (n={n_pontos})\n"
        f"--------------------------------------------\n"
        f"Σ x    = {sum_x:,.2f}\n"
        f"Σ x²   = {sum_x2:,.2f}\n"
        f"Σ y    = {sum_y:,.4f}  (onde y = log10(N))\n"
        f"Σ x·y  = {sum_xy:,.4f}\n\n"
        f"PASSO 2: SISTEMA NORMAL (Matriz)\n"
        f"--------------------------------------------\n"
        f"[{n_pontos}       {sum_x:,.0f}   ] [ B ]   [ {sum_y:.4f}   ]\n"
        f"[{sum_x:,.0f}   {sum_x2:,.0f} ] [ A ] = [ {sum_xy:.4f} ]\n\n"
        f"PASSO 3: SOLUÇÃO DO SISTEMA\n"
        f"--------------------------------------------\n"
        f"B (Linear/Intercepto) = {B_linear:.6f}\n"
        f"A (Angular/Inclinação)= {A_angular:.6f}\n\n"
        f"PASSO 4: MODELO FINAL\n"
        f"--------------------------------------------\n"
        f"alpha = 10^B = {alpha:.4e}\n"
        f"Equação: N = {alpha:.4e} * 10^({A_angular:.5f} * Ano)"
    )

    return x, N, y_log, alpha, beta, B_linear, detalhes_calculo


def prever(ano, alpha, beta):
    return alpha * (10 ** (beta * ano))


# --- INTERFACE GRÁFICA ---

class MooreAppStepByStep:
    def __init__(self, root):
        self.root = root
        self.root.title("Lei de Moore - Método MMQ Passo a Passo")
        self.root.state('zoomed')

        # Estilos Grandes para Projetor
        style = ttk.Style()
        style.configure("Big.TLabel", font=("Arial", 16))
        style.configure("Header.TLabel", font=("Arial", 24, "bold"))
        style.configure("Mono.TLabel", font=("Courier New", 14), background="#f0f0f0")

        # Cálculos
        self.x, self.y_real, self.y_log, self.alpha, self.beta, self.B_linear, self.texto_detalhes = calcular_mmq_detalhado()

        self.criar_abas()

    def criar_abas(self):
        # Criação de Abas (Notebook)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Aba 1: Gráficos e Previsão
        tab_graph = ttk.Frame(notebook)
        notebook.add(tab_graph, text="  GRÁFICOS E PREVISÃO  ")
        self.setup_tab_graficos(tab_graph)

        # Aba 2: Memória de Cálculo (O que o professor quer ver)
        tab_calc = ttk.Frame(notebook)
        notebook.add(tab_calc, text="  MEMÓRIA DE CÁLCULO (Passo a Passo)  ")
        self.setup_tab_calculo(tab_calc)

    def setup_tab_graficos(self, parent):
        # Layout da Aba Gráficos
        frame_top = ttk.Frame(parent)
        frame_top.pack(fill="x", pady=10, padx=20)

        # Título
        ttk.Label(frame_top, text="Lei de Moore: Resultado Visual", style="Header.TLabel").pack()

        # Input Interativo
        frame_input = ttk.LabelFrame(frame_top, text="Simulação", padding=10)
        frame_input.pack(pady=10)

        ttk.Label(frame_input, text="Ano para prever:", style="Big.TLabel").pack(side="left")
        self.ent_ano = ttk.Entry(frame_input, font=("Arial", 16), width=10)
        self.ent_ano.pack(side="left", padx=10)

        btn = ttk.Button(frame_input, text="CALCULAR", command=self.calcular_custom)
        btn.pack(side="left")

        self.lbl_res = ttk.Label(frame_top, text="Insira um ano acima", style="Big.TLabel", foreground="blue")
        self.lbl_res.pack(pady=5)

        # Gráficos
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

        # Gráfico Linearizado
        x_line = np.linspace(1970, 2025, 100)
        y_line_log = self.beta * x_line + self.B_linear

        ax1.scatter(self.x, self.y_log, color='red', s=80, label='Dados Originais (Log)')
        ax1.plot(x_line, y_line_log, color='blue', linewidth=3, label='Reta MMQ')
        ax1.set_title("Linearização (Log10)", fontsize=14)
        ax1.grid(True)
        ax1.legend()

        # Gráfico Exponencial
        y_line_exp = prever(x_line, self.alpha, self.beta)
        ax2.scatter(self.x, self.y_real, color='red', s=80, label='Dados Reais')
        ax2.plot(x_line, y_line_exp, color='green', linewidth=3, label='Curva Ajustada')
        ax2.set_title("Curva Exponencial Final", fontsize=14)
        ax2.set_yscale('log')
        ax2.grid(True)
        ax2.legend()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def setup_tab_calculo(self, parent):
        # Título
        ttk.Label(parent, text="Detalhamento do Método dos Mínimos Quadrados", style="Header.TLabel").pack(pady=20)

        # Área de Texto com Scroll
        text_area = tk.Text(parent, font=("Courier New", 18), bg="#f5f5f5", padx=20, pady=20)
        text_area.pack(fill="both", expand=True, padx=40, pady=20)

        # Inserir o texto calculado
        text_area.insert(tk.END, self.texto_detalhes)
        text_area.config(state="disabled")  # Apenas leitura

    def calcular_custom(self):
        try:
            ano = float(self.ent_ano.get())
            res = prever(ano, self.alpha, self.beta)
            self.lbl_res.config(text=f"Em {int(ano)}: {res:.2e} transistores")
        except ValueError:
            messagebox.showerror("Erro", "Ano inválido")


if __name__ == "__main__":
    root = tk.Tk()
    app = MooreAppStepByStep(root)
    root.mainloop()