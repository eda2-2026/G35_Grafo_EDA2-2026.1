import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import numpy as np
from node import *
import graph_ops as ops

# Importa as funções que unificamos na main 
import main as logic 

class RefinedGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Projeto Algoritmos - Visualizador de SCC & Conectividade")
        self.root.geometry("1000x800") # Janela maior para acomodar os gráficos
        self.root.configure(bg="#f5f5f5")

        self.caminho_arquivo = ""
        self.grafo_entrada = []
        self.sccs = []
        self.conexoes_sugeridas = [] 

    
        self.header_frame = tk.Frame(root, bg="#f5f5f5")
        self.header_frame.pack(pady=10)
        tk.Label(self.header_frame, text="Otimizador de Conectividade de Grafos", 
                 font=("Segoe UI", 18, "bold"), bg="#f5f5f5", fg="#333").pack()

   
        self.ctrl_frame = tk.Frame(root, width=250, bg="white", relief=tk.RIDGE, borderwidth=1)
        self.ctrl_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=10)
        self.ctrl_frame.pack_propagate(False) # Mantém tamanho fixo

        tk.Label(self.ctrl_frame, text="Controles", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=10)
        
        self.btn_carregar = tk.Button(self.ctrl_frame, text="📂 Carregar in.txt", 
                                      command=self.acao_carregar, font=("Segoe UI", 10))
        self.btn_carregar.pack(pady=5, padx=20, fill=tk.X)

        self.btn_processar = tk.Button(self.ctrl_frame, text="🚀 Processar Grafo", 
                                       command=self.acao_processar, font=("Segoe UI", 10, "bold"),
                                       bg="#4CAF50", fg="white", state=tk.DISABLED)
        self.btn_processar.pack(pady=5, padx=20, fill=tk.X)

        tk.Label(self.ctrl_frame, text="Log de Análise", font=("Segoe UI", 10), bg="white").pack(pady=(20, 5))
        self.log_area = scrolledtext.ScrolledText(self.ctrl_frame, height=25, font=("Consolas", 9))
        self.log_area.pack(padx=10, pady=5, fill=tk.BOTH)
        self.log_area.insert(tk.END, "Aguardando arquivo...\n")

       
        self.plot_frame = tk.Frame(root, bg="#e0e0e0")
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

       
        self.fig, (self.ax_orig, self.ax_final) = plt.subplots(2, 1, figsize=(6, 8))
        self.fig.tight_layout(pad=4.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.configurar_eixos_iniciais()

    #  Funções de Interface 

    def configurar_eixos_iniciais(self):
        # Limpa e coloca títulos padrão
        self.ax_orig.clear()
        self.ax_orig.set_title("1. Grafo de Entrada (Coordenadas XY)")
        self.ax_orig.axis('off')

        self.ax_final.clear()
        self.ax_final.set_title("2. Sugestões de Conexão (Grafo Final Conexo)")
        self.ax_final.axis('off')
        
        self.canvas.draw()

    def update_log(self, text, type="normal"):
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.see(tk.END) # Scroll automático

  

    def acao_carregar(self):
        self.caminho_arquivo = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.caminho_arquivo:
            try:
                self.log_area.delete(1.0, tk.END)
                fname = self.caminho_arquivo.split('/')[-1]
                self.update_log(f"✅ Arquivo carregado: {fname}")
                
                # Reseta estado
                self.configurar_eixos_iniciais()
                self.btn_processar.config(state=tk.NORMAL)
                
                # Pré-carrega o grafo para ver se está lendo ok
                self.grafo_entrada = logic.carregar_grafo(self.caminho_arquivo)
                
                # Alerta sobre coordenadas zeros 
                xs = [n.x for n in self.grafo_entrada]
                ys = [n.y for n in self.grafo_entrada]
                if all(x == 0 for x in xs) and all(y == 0 for y in ys):
                    self.update_log("⚠️ AVISO: Todos os nós estão na coordenada (0,0).")
                    self.update_log("Para melhor visualização gráfica, use coordenadas diferentes no arquivo.")

            except Exception as e:
                messagebox.showerror("Erro de Leitura", f"Erro ao ler arquivo:\n{str(e)}")

    def acao_processar(self):
        try:
            if not self.grafo_entrada: return
            
            self.update_log("\n--- Iniciando Processamento ---")
            
            # Recupera Lógica de SCC (reutilizando a main unificada)
            g_trabalho = logic.ops.copy_graph(self.grafo_entrada)
            self.sccs = []
            while g_trabalho:
                gi = logic.ops.inverted(g_trabalho)
                sni = logic.DFS_visit(gi) 
                sn = g_trabalho[logic.Node.find_node(g_trabalho, sni)]
                
                bfg = logic.BFS(g_trabalho, sn)
                bfgi = logic.BFS(gi, sni)
                scc = logic.ops.intersect(bfg, bfgi)
                
                self.sccs.append(scc)
                g_trabalho = logic.ops.minus(g_trabalho, scc)

            self.update_log(f"📊 {len(self.sccs)} Componentes Fortemente Conexos encontrados.")
            for i, scc in enumerate(self.sccs):
                self.update_log(f"🔹 SCC {i+1}: {[n.name for n in scc]}")

            # Recupera Lógica de Conexão Baseada em Distância
            self.conexoes_sugeridas = []
            sccs_ativos = [s for s in self.sccs]
            while len(sccs_ativos) > 1:
                menor_dist = float('inf')
                par_escolhido = (None, None)
                indices = (0, 0)
                ab_ba = (False, False)

                for i in range(len(sccs_ativos)):
                    for j in range(i + 1, len(sccs_ativos)):
                        for no_a in sccs_ativos[i]:
                            for no_b in sccs_ativos[j]:
                                d = logic.calcular_distancia(no_a, no_b)
                                if d < menor_dist:
                                    menor_dist = d
                                    par_escolhido = (no_a, no_b)
                                    indices = (i, j)
                # Checa se já existe conexão entre os sccs
                for n in sccs_ativos[indices[0]]:
                    for neigh in self.grafo_entrada[Node.find_node(self.grafo_entrada,n)].neighbors:
                        if(Node.find_node(sccs_ativos[indices[1]],neigh) != -1):
                            ab_ba = (True, False)
                            break
                if(not ab_ba[0]):
                    for m in sccs_ativos[indices[1]]:
                        for meigh in self.grafo_entrada[Node.find_node(self.grafo_entrada,m)].neighbors:
                            if(Node.find_node(sccs_ativos[indices[0]], meigh) != -1):
                                ab_ba = (False, True)
                                break

                
                if par_escolhido[0]:
                    n1, n2 = par_escolhido
                    # Criamos arestas de ida e volta conforme requisito
                    self.conexoes_sugeridas.append((n1.name, n2.name, menor_dist, ab_ba))
                    
                    idx1, idx2 = indices
                    sccs_ativos[idx1] = ops.dumb_unite(sccs_ativos[idx1], sccs_ativos[idx2])
                    sccs_ativos.pop(idx2)

            if self.conexoes_sugeridas:
                self.update_log("\n💡 Arestas Sugeridas:")
                for u, v, d, ab in self.conexoes_sugeridas:
                    self.update_log(f"🔗 Unir {u} {"" if ab[0] else "<"}-{"" if ab[1] else ">"} {v} (Dist: {d:.2f})")
            else:
                self.update_log("\nO grafo já é fortemente conexo!")

            self.update_log("\n⚙️ Renderizando visualização gráfica...")
            self.desenhar_grafos()
            self.update_log("✅ Concluído!")

        except Exception as e:
            messagebox.showerror("Erro de Processamento", f"Falha ao processar o grafo:\n{str(e)}")
            self.update_log(f"❌ Erro: {e}")

    # Funções de Plotagem 

    def preparar_nx_graph(self, nodes_list):

        G = nx.DiGraph()
        
        # Mapa de nomes para Nodes para resgatar coordenadas
        node_map = {node.name: node for node in nodes_list}
        
        pos = {}
        for name, node in node_map.items():
            G.add_node(name)
            pos[name] = (node.x, node.y) # X e Y do arquivo
        
        # Adiciona arestas originais
        for name, node in node_map.items():
            for neighbor in node.neighbors:
                G.add_edge(name, neighbor.name)
        
        return G, pos

    def desenhar_grafos(self):
        node_color = '#bbdefb' # Azul claro
        edge_color_orig = '#333' # Cinza escuro
        node_size = 600
        edge_width = 1.5
        arrow_size = 15

        # Desenha Subplot 1: Original
        self.ax_orig.clear()
        self.ax_orig.set_title("1. Grafo de Entrada (Nós nas Coordenadas XY)", fontname="Segoe UI", fontsize=11, fontweight="bold")
        self.ax_orig.axis('off')

        G_orig, pos = self.preparar_nx_graph(self.grafo_entrada)
        
        # Se todos os nós estão no mesmo ponto (0,0), Nx desenha horrível. 
        if pos:
            all_x = [p[0] for p in pos.values()]
            all_y = [p[1] for p in pos.values()]
            if len(set(all_x)) == 1 and len(set(all_y)) == 1:
                # Alarga os eixos manualmente se for tudo (0,0)
                self.ax_orig.set_xlim(-1, 1)
                self.ax_orig.set_ylim(-1, 1)

        # Desenha Nós
        nx.draw_networkx_nodes(G_orig, pos, ax=self.ax_orig, node_size=node_size, 
                               node_color=node_color, edgecolors='#333', linewidths=1)
        # Desenha Rótulos (Nomes)
        nx.draw_networkx_labels(G_orig, pos, ax=self.ax_orig, font_size=10, font_family="Segoe UI")
        # Desenha Arestas Originais (setinhas)
        nx.draw_networkx_edges(G_orig, pos, ax=self.ax_orig, edge_color=edge_color_orig, 
                               width=edge_width, arrows=True, arrowsize=arrow_size,
                               connectionstyle="arc3,rad=0.1") # Curva leve para arestas duplas

        # Desenha Subplot 2: Final (Original + Sugestões)
        self.ax_final.clear()
        self.ax_final.set_title("2. Resultado Final (Arestas Sugeridas em Vermelho)", fontname="Segoe UI", fontsize=11, fontweight="bold")
        self.ax_final.axis('off')

        # Cria uma cópia do grafo para adicionar as sugestões
        G_final = G_orig.copy()
        
        # Adiciona as sugestões (como DiGraph - Ida e Volta)
        for u, v, _, ab in self.conexoes_sugeridas:
            if (not ab[0]): G_final.add_edge(u, v)
            if (not ab[1]): G_final.add_edge(v, u)

        # Desenha a base (nós e labels)
        nx.draw_networkx_nodes(G_final, pos, ax=self.ax_final, node_size=node_size, 
                               node_color=node_color, edgecolors='#333', linewidths=1)
        nx.draw_networkx_labels(G_final, pos, ax=self.ax_final, font_size=10, font_family="Segoe UI")
        
        # Desenha Arestas Originais
        nx.draw_networkx_edges(G_final, pos, ax=self.ax_final, edgelist=G_orig.edges(), 
                               edge_color=edge_color_orig, width=edge_width, arrows=True, arrowsize=arrow_size,
                               connectionstyle="arc3,rad=0.1")


        if self.conexoes_sugeridas:
            edges_sug_nx = []
            for u, v, _, ab in self.conexoes_sugeridas:
                if(not ab[0]): edges_sug_nx.append((u, v)) # ida
                if(not ab[1]): edges_sug_nx.append((v, u)) # volta

            nx.draw_networkx_edges(G_final, pos, ax=self.ax_final, edgelist=edges_sug_nx, 
                                   edge_color='#f44336', width=2.0, style='--', arrows=True, arrowsize=15,
                                   connectionstyle="arc3,rad=0.15") # Curva diferente para destacar

        # Redesenha a tela do Tkinter
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    # Tenta definir um ícone padrão do Windows para bolinha, se falhar, ok
    try: root.iconbitmap(None) 
    except: pass
    app = RefinedGraphApp(root)
    root.mainloop()
