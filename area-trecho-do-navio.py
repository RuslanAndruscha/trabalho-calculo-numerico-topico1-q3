import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class NavioInterativoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Seção Mestra - Navio")
        self.root.state('zoomed')

        # --- VALORES INICIAIS DA QUESTÃO ---
        self.default_h = "0.4"
        self.default_y = "3.00, 2.92, 2.75, 2.52, 2.30, 1.84, 0.92, 0.00"
        self.setup_ui()
        self.calcular_e_plotar()

    def setup_ui(self):
        # --- Painel Esquerdo (Controles) ---
        panel_left = ttk.Frame(self.root, padding=20)
        panel_left.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(panel_left, text="Parâmetros de Entrada", font=("Arial", 16, "bold")).pack(pady=(0, 20))

        # Entrada do Passo (h)
        ttk.Label(panel_left, text="Passo Vertical (h) em metros:", font=("Arial", 12)).pack(anchor="w")
        self.ent_h = ttk.Entry(panel_left, font=("Arial", 12))
        self.ent_h.insert(0, self.default_h)  # Preenche valor inicial
        self.ent_h.pack(fill=tk.X, pady=(5, 15))

        # Entrada das Larguras (y)
        ttk.Label(panel_left, text="Larguras (y) separadas por vírgula:", font=("Arial", 12)).pack(anchor="w")
        ttk.Label(panel_left, text="(Do topo até a quilha)", font=("Arial", 9, "italic"), foreground="gray").pack(
            anchor="w")

        self.ent_y = tk.Text(panel_left, height=4, font=("Arial", 12), width=30)
        self.ent_y.insert(tk.END, self.default_y)  # Preenche valores iniciais
        self.ent_y.pack(fill=tk.X, pady=(5, 20))

        # Botão Calcular
        btn_calc = ttk.Button(panel_left, text="RECALCULAR", command=self.calcular_e_plotar)
        btn_calc.pack(fill=tk.X, ipady=10)

        # --- Painel de Resultados ---
        res_frame = ttk.LabelFrame(panel_left, text="Resultados", padding=15)
        res_frame.pack(fill=tk.X, pady=30)

        self.lbl_trap = ttk.Label(res_frame, text="Trapézios: ---", font=("Courier New", 14, "bold"),
                                  foreground="#003366")
        self.lbl_trap.pack(anchor="w", pady=5)

        self.lbl_simp = ttk.Label(res_frame, text="Simpson: ---", font=("Courier New", 14, "bold"),
                                  foreground="#003366")
        self.lbl_simp.pack(anchor="w", pady=5)

        self.lbl_info_simp = ttk.Label(res_frame, text="", font=("Arial", 9, "italic"), foreground="red",
                                       wraplength=250)
        self.lbl_info_simp.pack(anchor="w", pady=(10, 0))

        # --- Painel Direito (Gráfico) ---
        panel_right = ttk.Frame(self.root)
        panel_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=panel_right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def get_dados(self):
        try:
            h = float(self.ent_h.get().replace(',', '.'))

            # Pega o texto, remove quebras de linha, substitui vírgula decimal se houver confusão
            raw_y = self.ent_y.get("1.0", tk.END).strip()
            # Divide por vírgula e converte para float array
            y_list = [float(val.strip()) for val in raw_y.split(',')]

            return h, np.array(y_list)
        except ValueError:
            messagebox.showerror("Erro de Formato",
                                 "Certifique-se de usar números válidos.\nUse ponto (.) para decimais e vírgula (,) para separar as larguras.")
            return None, None

    def calcular_e_plotar(self):
        h, y = self.get_dados()
        if h is None or y is None: return

        n_intervalos = len(y) - 1

        if n_intervalos < 1:
            messagebox.showerror("Erro", "É necessário pelo menos 2 pontos (1 intervalo).")
            return

        # --- CÁLCULO 1: Regra dos Trapézios Repetida ---
        # Formula: h/2 * (y_inicial + 2*soma_meio + y_final)
        area_trap = (h / 2) * (y[0] + 2 * np.sum(y[1:-1]) + y[-1])

        # --- CÁLCULO 2: Regra de Simpson (Adaptativa) ---
        area_simp = 0
        info_msg = ""

        # Verifica paridade dos intervalos
        if n_intervalos % 2 == 0:
            # Caso ideal: Número par de intervalos -> Simpson Puro
            # Formula: h/3 * (y0 + 4*Impares + 2*Pares + yn)
            soma_impares = np.sum(y[1:-1:2])  # Índices 1, 3, 5...
            soma_pares = np.sum(y[2:-1:2])  # Índices 2, 4, 6...
            area_simp = (h / 3) * (y[0] + 4 * soma_impares + 2 * soma_pares + y[-1])
            info_msg = "Método: Simpson 1/3 Puro (N par)"

        else:
            # Caso da questão: Número ímpar de intervalos -> Simpson Misto
            # Estratégia: Simpson até o penúltimo ponto + Trapézio no último

            # Parte A: Simpson (0 até n-1)
            y_simp = y[:-1]  # Remove o último ponto
            soma_impares = np.sum(y_simp[1:-1:2])
            soma_pares = np.sum(y_simp[2:-1:2])
            area_parte_simp = (h / 3) * (y_simp[0] + 4 * soma_impares + 2 * soma_pares + y_simp[-1])

            # Parte B: Trapézio (último intervalo)
            area_parte_trap = (h / 2) * (y[-2] + y[-1])

            area_simp = area_parte_simp + area_parte_trap
            info_msg = f"Atenção: N={n_intervalos} (ímpar).\nMétodo Misto aplicado:\nSimpson (0-{n_intervalos - 1}) + Trapézio ({n_intervalos - 1}-{n_intervalos})"

        # Atualiza Labels
        self.lbl_trap.config(text=f"Trapézios: {area_trap:.4f} m²")
        self.lbl_simp.config(text=f"Simpson:   {area_simp:.4f} m²")
        self.lbl_info_simp.config(text=info_msg)

        # Plota Gráfico
        self.plotar_casco(h, y)

    def plotar_casco(self, h, y):
        self.ax.clear()

        # Coordenadas de profundidade (0, -0.4, -0.8...)
        profundidades = -np.arange(len(y)) * h

        # Desenha o perfil direito
        self.ax.plot(y, profundidades, 'o-', color='navy', linewidth=2, label='Casco')
        # Linha de centro
        self.ax.axvline(0, color='black', linestyle='-', linewidth=0.5)

        # Preenchimento
        self.ax.fill_betweenx(profundidades, 0, y, color='skyblue', alpha=0.6, label='Área Integrada')

        # Estética
        self.ax.set_title("Perfil da Seção Transversal", fontsize=14)
        self.ax.set_xlabel("Largura (m)")
        self.ax.set_ylabel("Profundidade (m)")
        self.ax.grid(True, linestyle='--', alpha=0.5)
        self.ax.legend()
        self.ax.set_aspect('equal')  # Mantém a proporção visual correta

        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = NavioInterativoApp(root)
    root.mainloop()