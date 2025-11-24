import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ShipAreaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cálculo de Área Naval - Integração Numérica")
        self.root.state('zoomed')  # Abre em tela cheia/maximizado

        # --- DADOS DO PROBLEMA (Conforme imagem) ---
        # Alturas (y) em metros, de cima (A) para baixo (A7)
        self.larguras = np.array([3.00, 2.92, 2.75, 2.52, 2.30, 1.84, 0.92, 0.00])
        self.h = 0.4  # Espaçamento vertical (passo)

        # Configuração de Estilos
        self.setup_styles()

        # Layout Principal
        self.create_widgets()

        # Plotar gráfico inicial
        self.plot_profile()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 12))
        style.configure("Header.TLabel", font=("Arial", 18, "bold"))
        style.configure("Result.TLabel", font=("Courier New", 14, "bold"), foreground="#003366")
        style.configure("TButton", font=("Arial", 12, "bold"))

    def create_widgets(self):
        # Frame Esquerdo (Controles e Resultados)
        left_frame = ttk.Frame(self.root, padding="20")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Título
        ttk.Label(left_frame, text="Seção Transversal do Navio", style="Header.TLabel").pack(pady=(0, 20))

        # Exibição dos Dados
        data_frame = ttk.LabelFrame(left_frame, text="Dados de Entrada", padding="10")
        data_frame.pack(fill=tk.X, pady=10)

        ttk.Label(data_frame, text=f"Passo (h): {self.h} m").pack(anchor="w")
        ttk.Label(data_frame, text=f"Larguras (m): {list(self.larguras)}").pack(anchor="w", pady=5)
        ttk.Label(data_frame, text=f"Nº de Intervalos: {len(self.larguras) - 1}").pack(anchor="w")

        # Botão Calcular
        calc_btn = ttk.Button(left_frame, text="CALCULAR ÁREAS", command=self.calcular_areas)
        calc_btn.pack(fill=tk.X, pady=20)

        # Área de Resultados
        self.res_frame = ttk.LabelFrame(left_frame, text="Resultados Calculados", padding="15")
        self.res_frame.pack(fill=tk.X, expand=True, anchor="n")

        self.lbl_res_trap = ttk.Label(self.res_frame, text="Trapézios: ---", style="Result.TLabel")
        self.lbl_res_trap.pack(pady=10, anchor="w")

        self.lbl_res_simp = ttk.Label(self.res_frame, text="Simpson: ---", style="Result.TLabel")
        self.lbl_res_simp.pack(pady=10, anchor="w")

        # Explicação Técnica
        expl_text = (
            "Nota sobre Simpson:\n"
            "Como n=7 (ímpar), o método foi adaptado:\n"
            "1. Simpson nos primeiros 6 intervalos (0 a 6).\n"
            "2. Trapézio no último intervalo (6 a 7)."
        )
        ttk.Label(left_frame, text=expl_text, font=("Arial", 10, "italic"), foreground="gray").pack(side=tk.BOTTOM,
                                                                                                    anchor="w")

        # Frame Direito (Gráfico)
        right_frame = ttk.Frame(self.root, padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def calcular_areas(self):
        y = self.larguras
        h = self.h
        n = len(y) - 1  # Número de intervalos

        # --- 1. Regra dos Trapézios Repetida ---
        # Area = h/2 * [y0 + 2*soma(meio) + yn]
        soma_meio = np.sum(y[1:-1])
        area_trap = (h / 2) * (y[0] + 2 * soma_meio + y[-1])

        # --- 2. Regra de Simpson Mista ---
        # Temos 7 intervalos. Simpson precisa de par.
        # Dividimos em: Simpson (0 a 6) + Trapézio (6 a 7)

        # Parte A: Simpson (índices 0 a 6 -> 7 pontos)
        y_simpson = y[0:7]
        # Fórmula: h/3 * [y0 + 4*(ímpares) + 2*(pares) + yn]
        # Índices relativos ao subconjunto:
        # Extremos: 0 e 6
        # Ímpares (coef 4): 1, 3, 5
        # Pares (coef 2): 2, 4
        soma_impares = y_simpson[1] + y_simpson[3] + y_simpson[5]
        soma_pares = y_simpson[2] + y_simpson[4]

        area_part_simpson = (h / 3) * (y_simpson[0] + 4 * soma_impares + 2 * soma_pares + y_simpson[-1])

        # Parte B: Trapézio Simples (índices 6 a 7)
        area_part_trap = (h / 2) * (y[6] + y[7])

        area_total_simpson = area_part_simpson + area_part_trap

        # Atualizar Interface
        self.lbl_res_trap.config(text=f"Trapézios: {area_trap:.4f} m²")
        self.lbl_res_simp.config(text=f"Simpson (+Trap): {area_total_simpson:.4f} m²")

        self.plot_profile(fill=True)

    def plot_profile(self, fill=False):
        self.ax.clear()

        # Coordenadas para plotagem
        # O eixo X será a largura, o eixo Y será a profundidade (negativa para desenhar para baixo)
        profundidades = -np.arange(0, len(self.larguras) * self.h, self.h)
        larguras = self.larguras

        # Desenhar o perfil (lado direito)
        self.ax.plot(larguras, profundidades, 'o-', color='blue', linewidth=2, label='Casco (Direito)')

        # Desenhar linha de centro
        self.ax.axvline(x=0, color='black', linestyle='--', linewidth=1)

        # Desenhar espelho (lado esquerdo) para parecer um navio
        self.ax.plot(-larguras, profundidades, 'b-', alpha=0.3)

        # Preenchimento da área calculada
        if fill:
            self.ax.fill_betweenx(profundidades, 0, larguras, color='skyblue', alpha=0.5, label='Área Calculada')
            self.ax.text(1.5, -1.5, "Área Aprox.\n~5.9 m²", fontsize=12, color='darkblue', fontweight='bold')

        # Configurações do Gráfico
        self.ax.set_title("Perfil da Seção Transversal")
        self.ax.set_xlabel("Largura (m)")
        self.ax.set_ylabel("Profundidade (m)")
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.legend()

        # Ajustar proporção para não distorcer
        self.ax.set_aspect('equal')

        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = ShipAreaApp(root)
    root.mainloop()