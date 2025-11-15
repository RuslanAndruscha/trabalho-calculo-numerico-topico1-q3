import tkinter as tk
from tkinter import messagebox
import numpy as np


class AppSistemaLinear(tk.Tk):
    """
    Interface gráfica para resolver sistemas lineares 3x3 (Problema 1 - Minas).
    """

    def __init__(self):
        super().__init__()

        self.title("Calculadora de Sistema Linear 3x3")
        self.geometry("400x350")

        # Dados iniciais do Problema 1
        self.dados_A_iniciais = [
            [0.55, 0.25, 0.25],
            [0.30, 0.45, 0.20],
            [0.15, 0.30, 0.55]
        ]
        self.dados_B_iniciais = [4800, 5800, 5700]

        # Listas para guardar os widgets de entrada
        self.entries_A = []
        self.entries_B = []

        # Chamar o método que constrói a interface
        self.criar_widgets()

    def criar_widgets(self):
        """
        Cria e organiza todos os widgets na janela.
        """

        # --- Frame para Matriz A ---
        frame_A = tk.LabelFrame(self, text="Matriz A (Coeficientes)")
        frame_A.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Cria a grade 3x3 de entradas para a Matriz A
        for i in range(3):
            linha_entries = []
            for j in range(3):
                entry = tk.Entry(frame_A, width=8, font=("Arial", 12))
                # Pré-preenche com os dados do problema
                entry.insert(0, str(self.dados_A_iniciais[i][j]))
                entry.grid(row=i, column=j, padx=5, pady=5)
                linha_entries.append(entry)
            self.entries_A.append(linha_entries)

        # --- Frame para Vetor B ---
        frame_B = tk.LabelFrame(self, text="Vetor B (Totais)")
        frame_B.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        # Labels para indicar as equações
        labels_B = ["Areia:", "C. Fino:", "C. Grosso:"]

        # Cria a coluna de entradas para o Vetor B
        for i in range(3):
            # Label
            label = tk.Label(frame_B, text=labels_B[i])
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

            # Entrada
            entry = tk.Entry(frame_B, width=10, font=("Arial", 12))
            # Pré-preenche com os dados do problema
            entry.insert(0, str(self.dados_B_iniciais[i]))
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries_B.append(entry)

        # --- Botão de Cálculo ---
        btn_calcular = tk.Button(self, text="Calcular Solução",
                                 font=("Arial", 12, "bold"),
                                 command=self.calcular_solucao)
        btn_calcular.grid(row=1, column=0, columnspan=2, pady=10)

        # --- Label de Resultado ---
        self.label_resultado = tk.Label(self, text="Aguardando cálculo...",
                                        font=("Arial", 12),
                                        justify=tk.LEFT,
                                        relief="sunken",
                                        padx=10, pady=10)
        self.label_resultado.grid(row=2, column=0, columnspan=2,
                                  padx=10, pady=10, sticky="ew")

    def calcular_solucao(self):
        """
        Lê os dados dos campos de entrada, resolve o sistema e exibe o resultado.
        """
        try:
            # 1. Obter dados da Matriz A
            A = np.zeros((3, 3))
            for i in range(3):
                for j in range(3):
                    A[i, j] = float(self.entries_A[i][j].get())

            # 2. Obter dados do Vetor B
            B = np.zeros(3)
            for i in range(3):
                B[i] = float(self.entries_B[i].get())

        except ValueError:
            messagebox.showerror("Erro de Entrada",
                                 "Entrada inválida. Por favor, insira apenas números.")
            return

        # 3. Resolver o sistema
        try:
            # Usando o método direto do NumPy
            solucao = np.linalg.solve(A, B)

            # 4. Exibir o resultado (Clareza na apresentação)
            str_solucao = f"Solução (Quantidades de cada Mina):\n\n"
            str_solucao += f"  Mina 1 (x1): {solucao[0]:.2f} m³\n"
            str_solucao += f"  Mina 2 (x2): {solucao[1]:.2f} m³\n"
            str_solucao += f"  Mina 3 (x3): {solucao[2]:.2f} m³"

            self.label_resultado.config(text=str_solucao)

        except np.linalg.LinAlgError:
            messagebox.showerror("Erro de Cálculo",
                                 "Matriz singular. O sistema não possui solução única.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")


# --- Ponto de entrada principal para rodar o app ---
if __name__ == "__main__":
    app = AppSistemaLinear()
    app.mainloop()