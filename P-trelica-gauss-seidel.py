import tkinter as tk
from tkinter import messagebox
import math


class TrussSolverVisual:
    def __init__(self, root):
        self.root = root
        self.root.title("Solver Treliça - Resultados Detalhados")
        self.root.geometry("1350x700")

        # --- Definições Físicas da Treliça ---
        self.var_names = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "H1", "V1", "V3"]
        self.num_vars = len(self.var_names)

        # Senos e Cossenos
        s45 = math.sin(math.radians(45))
        c45 = math.cos(math.radians(45))
        s60 = math.sin(math.radians(60))
        c60 = math.cos(math.radians(60))
        s30 = math.sin(math.radians(30))
        c30 = math.cos(math.radians(30))

        # MATRIZ (Ordenada para garantir convergência)
        self.default_matrix = [
            [-s45, 0, -s45, 0, 0, 0, 0, 0, 0, 0],  # Nó 4 Y
            [0, -1.0, -c45, 0, c60, 1.0, 0, 0, 0, 0],  # Nó 2 X
            [0, 0, s45, 0, s60, 0, 0, 0, 0, 0],  # Nó 2 Y
            [-c45, 0, c45, 1.0, 0, 0, 0, 0, 0, 0],  # Nó 4 X
            [0, 0, 0, 0, -s60, 0, -s30, 0, 0, 0],  # Nó 5 Y
            [0, 0, 0, 0, 0, -1.0, -c30, 0, 0, 0],  # Nó 3 X
            [0, 0, 0, -1.0, -c60, 0, c30, 0, 0, 0],  # Nó 5 X
            [c45, 1.0, 0, 0, 0, 0, 0, 1.0, 0, 0],  # Nó 1 X
            [s45, 0, 0, 0, 0, 0, 0, 0, 1.0, 0],  # Nó 1 Y
            [0, 0, 0, 0, 0, 0, s30, 0, 0, 1.0]  # Nó 3 Y
        ]

        self.default_b = [500, 0, 0, 0, 100, 0, 0, 0, 0, 0]

        # --- Interface ---
        frame_top = tk.Frame(self.root, pady=10)
        frame_top.pack()

        tk.Label(frame_top, text="Erro Máx:").pack(side=tk.LEFT)
        self.entry_error = tk.Entry(frame_top, width=8)
        self.entry_error.pack(side=tk.LEFT, padx=5)
        self.entry_error.insert(0, "0.0001")

        tk.Label(frame_top, text="Iterações:").pack(side=tk.LEFT, padx=10)
        self.entry_iter = tk.Entry(frame_top, width=5)
        self.entry_iter.pack(side=tk.LEFT, padx=5)
        self.entry_iter.insert(0, "500")

        btn_reset = tk.Button(frame_top, text="Reiniciar Dados", command=self.load_default_data, bg="#FFD700")
        btn_reset.pack(side=tk.LEFT, padx=20)

        # Botão Calcular Grande
        btn_calc = tk.Button(frame_top, text="CALCULAR FORÇAS AGORA", command=self.solve, bg="#4CAF50", fg="white",
                             font=("Arial", 10, "bold"))
        btn_calc.pack(side=tk.LEFT, padx=20)

        # Container Principal
        self.frame_matrix = tk.Frame(self.root)
        self.frame_matrix.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.entries_matrix = []
        self.entries_b = []
        self.entries_x = []
        self.labels_results = []  # Lista para guardar os labels onde a resposta aparecerá

        self.create_grid()
        self.load_default_data()

        # Rodapé com status
        self.status_label = tk.Label(self.root, text="Pronto para calcular...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def create_grid(self):
        # Cabeçalhos
        headers = ["Var", "X Inicial", "Matriz A (Coeficientes)", "=", "B (Cargas)", "RESULTADO FINAL (N)"]
        widths = [5, 8, 60, 2, 8, 25]

        # Layout manual dos headers para precisão
        tk.Label(self.frame_matrix, text=headers[0], font=("Arial", 9, "bold")).grid(row=0, column=0)
        tk.Label(self.frame_matrix, text=headers[1], font=("Arial", 9, "bold"), bg="#D1E8E2").grid(row=0, column=1)
        tk.Label(self.frame_matrix, text=headers[2], font=("Arial", 9, "bold")).grid(row=0, column=2,
                                                                                     columnspan=self.num_vars)
        tk.Label(self.frame_matrix, text=headers[3], font=("Arial", 9, "bold")).grid(row=0, column=self.num_vars + 2)
        tk.Label(self.frame_matrix, text=headers[4], font=("Arial", 9, "bold")).grid(row=0, column=self.num_vars + 3)
        tk.Label(self.frame_matrix, text=headers[5], font=("Arial", 10, "bold"), bg="#000000", fg="white").grid(row=0,
                                                                                                                column=self.num_vars + 4,
                                                                                                                padx=10,
                                                                                                                sticky="ew")

        for i in range(self.num_vars):
            # Nome Var
            tk.Label(self.frame_matrix, text=self.var_names[i], font=("Arial", 9, "bold"), fg="blue").grid(row=i + 1,
                                                                                                           column=0,
                                                                                                           pady=2)

            # X Inicial
            ex = tk.Entry(self.frame_matrix, width=8, justify="center", bg="#D1E8E2")
            ex.grid(row=i + 1, column=1, padx=2)
            self.entries_x.append(ex)

            # Matriz A
            row_entries = []
            for j in range(self.num_vars):
                e = tk.Entry(self.frame_matrix, width=6, justify="center")
                e.grid(row=i + 1, column=j + 2)
                if i == j: e.config(bg="#E6F2FF")
                row_entries.append(e)
            self.entries_matrix.append(row_entries)

            tk.Label(self.frame_matrix, text="=").grid(row=i + 1, column=self.num_vars + 2)

            # Vetor B
            eb = tk.Entry(self.frame_matrix, width=8, justify="center", bg="#FFF8DC")
            eb.grid(row=i + 1, column=self.num_vars + 3, padx=2)
            self.entries_b.append(eb)

            # --- CAMPO DE RESULTADO (NOVO) ---
            # Label vazio que será preenchido após o cálculo
            lbl_res = tk.Label(self.frame_matrix, text="---", font=("Arial", 10, "bold"), width=25, bg="#F0F0F0",
                               relief="groove")
            lbl_res.grid(row=i + 1, column=self.num_vars + 4, padx=10, pady=2)
            self.labels_results.append(lbl_res)

    def load_default_data(self):
        for i in range(self.num_vars):
            self.entries_x[i].delete(0, tk.END)
            self.entries_x[i].insert(0, "0.0")
            self.labels_results[i].config(text="---", bg="#F0F0F0", fg="black")

            self.entries_b[i].delete(0, tk.END)
            self.entries_b[i].insert(0, f"{self.default_b[i]}")

            for j in range(self.num_vars):
                val = self.default_matrix[i][j]
                self.entries_matrix[i][j].delete(0, tk.END)
                self.entries_matrix[i][j].insert(0, f"{val:.4f}")

    def solve(self):
        try:
            n = self.num_vars
            tol = float(self.entry_error.get())
            max_iter = int(self.entry_iter.get())

            A = []
            B = []
            x = []

            # Leitura
            for i in range(n):
                x.append(float(self.entries_x[i].get()))
                B.append(float(self.entries_b[i].get()))
                row = []
                for j in range(n):
                    row.append(float(self.entries_matrix[i][j].get()))
                A.append(row)

            # Gauss-Seidel Loop
            converged = False
            iters = 0

            for k in range(max_iter):
                x_old = x[:]
                max_err = 0.0

                for i in range(n):
                    sigma = 0
                    for j in range(n):
                        if j != i: sigma += A[i][j] * x[j]

                    if abs(A[i][i]) < 1e-9:
                        messagebox.showerror("Erro", f"Divisão por zero na linha {i + 1}")
                        return

                    x[i] = (B[i] - sigma) / A[i][i]

                    if abs(x[i]) > 1e-9:
                        err = abs((x[i] - x_old[i]) / x[i])
                    else:
                        err = abs(x[i] - x_old[i])

                    if err > max_err: max_err = err

                if max_err < tol:
                    converged = True
                    iters = k + 1
                    break

            # --- EXIBIR RESULTADOS NA TABELA ---
            if converged:
                self.status_label.config(text=f"Convergência alcançada em {iters} iterações. Erro final: {max_err:.6e}",
                                         fg="green")

                for i in range(n):
                    val = x[i]

                    # Lógica de exibição (Física)
                    tipo = ""
                    cor_fundo = "#FFFFFF"
                    cor_texto = "black"

                    if i < 7:  # Se for Força (F1 a F7)
                        if val > 0:
                            tipo = " (TRAÇÃO)"
                            cor_texto = "blue"
                            cor_fundo = "#E0F7FA"  # Azul claro
                        elif val < 0:
                            tipo = " (COMPRESSÃO)"
                            cor_texto = "red"
                            cor_fundo = "#FFEBEE"  # Vermelho claro
                        else:
                            tipo = " (Neutro)"
                    else:  # Reações
                        tipo = " (Reação)"
                        cor_texto = "#333333"

                    texto_final = f"{val:.2f} N{tipo}"
                    self.labels_results[i].config(text=texto_final, fg=cor_texto, bg=cor_fundo)

            else:
                self.status_label.config(text=f"FALHA: Não convergiu após {max_iter} iterações. Erro atual: {max_err}",
                                         fg="red")
                for lbl in self.labels_results:
                    lbl.config(text="Não convergiu", bg="red", fg="white")

        except ValueError:
            messagebox.showerror("Erro", "Verifique os números inseridos.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TrussSolverVisual(root)
    root.mainloop()