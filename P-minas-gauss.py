import tkinter as tk
from tkinter import messagebox
import numpy as np

def resolver_gauss_manual(A_in, B_in):
    A = np.copy(A_in)
    b = np.copy(B_in)
    n = len(b)

    # --- ETAPA 1: Eliminação Progressiva (Escalonamento) ---
    for k in range(n - 1):
        # 1.1 Pivoteamento Parcial:
        # Encontrar a linha com o maior valor absoluto na coluna atual (k)
        indice_max = k
        valor_max = abs(A[k, k])

        for i in range(k + 1, n):
            if abs(A[i, k]) > valor_max:
                valor_max = abs(A[i, k])
                indice_max = i

        if valor_max == 0:
            raise ValueError("O sistema não tem solução única (Matriz Singular).")

        # Trocar as linhas se necessário (tanto na matriz A quanto no vetor b)
        if indice_max != k:
            A[[k, indice_max]] = A[[indice_max, k]]
            b[[k, indice_max]] = b[[indice_max, k]]

        # 1.2 Eliminação (Zerar elementos abaixo do pivô):
        for i in range(k + 1, n):
            # Fator multiplicador (m)
            fator = A[i, k] / A[k, k]

            # Atualiza a linha i da matriz A: L_i = L_i - fator * L_k
            A[i, k:] = A[i, k:] - fator * A[k, k:]

            # Atualiza o vetor b também
            b[i] = b[i] - fator * b[k]

    # Verificação final para o último elemento da diagonal
    if A[n - 1, n - 1] == 0:
        raise ValueError("O sistema não tem solução única (Matriz Singular).")

    # --- ETAPA 2: Substituição Regressiva ---
    x = np.zeros(n)

    # Começa do último índice (n-1) e vai até 0, voltando de 1 em 1
    for i in range(n - 1, -1, -1):
        soma_conhecidos = 0
        # Soma os termos já encontrados (x[j] onde j > i)
        for j in range(i + 1, n):
            soma_conhecidos += A[i, j] * x[j]

        # Isola o x[i]
        x[i] = (b[i] - soma_conhecidos) / A[i, i]

    return x


# --- Interface Gráfica ---

class AppMinas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Problema das Minas")
        self.geometry("550x480")
        self.resizable(False, False)

        self.font_label = ("Arial", 10, "bold")
        self.font_entry = ("Arial", 10)

        self.criar_interface()

    def criar_interface(self):
        lbl_titulo = tk.Label(self, text="Composição das Minas (%)", font=("Arial", 14, "bold"))
        lbl_titulo.pack(pady=15)

        frame_dados = tk.Frame(self)
        frame_dados.pack(pady=5)

        colunas = ["Mina 1 (x1)", "Mina 2 (x2)", "Mina 3 (x3)", "Necessidade (m³)"]
        for idx, col in enumerate(colunas):
            tk.Label(frame_dados, text=col, font=self.font_label).grid(row=0, column=idx + 1, padx=5)

        materiais = ["Areia", "Cascalho Fino", "Cascalho Grosso"]

        defaults_A = [[55, 25, 25], [30, 45, 20], [15, 30, 55]]
        defaults_B = [4800, 5800, 5700]

        self.entradas_A = []
        self.entradas_B = []

        for i in range(3):
            tk.Label(frame_dados, text=materiais[i], font=self.font_label).grid(row=i + 1, column=0, padx=5, pady=5,
                                                                                sticky="e")
            linha_A = []
            for j in range(3):
                entry = tk.Entry(frame_dados, width=10, justify="center", font=self.font_entry)
                entry.insert(0, str(defaults_A[i][j]))
                entry.grid(row=i + 1, column=j + 1, padx=5, pady=5)
                linha_A.append(entry)
            self.entradas_A.append(linha_A)

            entry_b = tk.Entry(frame_dados, width=12, justify="center", font=self.font_entry, bg="#e8f5e9")
            entry_b.insert(0, str(defaults_B[i]))
            entry_b.grid(row=i + 1, column=4, padx=10, pady=5)
            self.entradas_B.append(entry_b)

        tk.Label(self, text="* Insira os valores de A como inteiros (ex: 55 para 55%)",
                 font=("Arial", 8, "italic"), fg="gray").pack()

        frame_botoes = tk.Frame(self)
        frame_botoes.pack(pady=20)

        btn_calc = tk.Button(frame_botoes, text="CALCULAR",
                             font=("Arial", 11, "bold"), bg="#2196F3", fg="white", width=18,
                             command=self.processar_calculo)
        btn_calc.pack(side="left", padx=10)

        btn_limpar = tk.Button(frame_botoes, text="LIMPAR DADOS",
                               font=("Arial", 11, "bold"), bg="#f44336", fg="white", width=15,
                               command=self.limpar_dados)
        btn_limpar.pack(side="left", padx=10)

        self.lbl_resultado = tk.Label(self, text="", font=("Courier New", 11),
                                      justify="left", bg="white", relief="sunken", bd=2)
        self.lbl_resultado.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def limpar_dados(self):
        for linha in self.entradas_A:
            for entry in linha:
                entry.delete(0, tk.END)
        for entry in self.entradas_B:
            entry.delete(0, tk.END)
        self.lbl_resultado.config(text="")
        self.entradas_A[0][0].focus_set()

    def processar_calculo(self):
        try:
            A = np.zeros((3, 3))
            B = np.zeros(3)

            for i in range(3):
                for j in range(3):
                    val_str = self.entradas_A[i][j].get()
                    if not val_str: val_str = "0"
                    A[i, j] = float(val_str) / 100.0

                val_b_str = self.entradas_B[i].get()
                if not val_b_str: val_b_str = "0"
                B[i] = float(val_b_str)

            x = resolver_gauss_manual(A, B)

            texto = "SOLUÇÃO:\n\n"
            texto += f"  Mina 1: {x[0]:.2f} m³\n"
            texto += f"  Mina 2: {x[1]:.2f} m³\n"
            texto += f"  Mina 3: {x[2]:.2f} m³\n"

            b_calc = np.dot(A, x)
            erro = np.linalg.norm(b_calc - B)
            texto += f"\n  (Erro residual: {erro:.2e})"

            self.lbl_resultado.config(text=texto, fg="black")

        except ValueError as ve:
            messagebox.showerror("Erro Matemático", str(ve))
        except Exception as e:
            messagebox.showerror("Erro", "Verifique os dados inseridos.\n" + str(e))


if __name__ == "__main__":
    app = AppMinas()
    app.mainloop()