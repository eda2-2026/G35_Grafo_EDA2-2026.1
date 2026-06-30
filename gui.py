import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import numpy as np
from node import *
import graph_ops as ops
import main as logic


BG_PANEL     = "#1a1d27"
BG_CARD      = "#22263a"
BG_DARK      = "#121212"
BG_HOVER     = "#2a2f47"
ACCENT       = "#7c6af7"     
ACCENT2      = "#dc0404"      
TEXT_PRIMARY = "#e8eaf6"
TEXT_MUTED   = "#8890b0"
TEXT_DIM     = "#555b7a"
BORDER       = "#2e3350"
SUCCESS      = "#4ade80"
WARNING      = "#fbbf24"
DANGER       = "#f87171"
PLOT_BG      = "#12151f"


SCC_COLORS = [
    "#7c6af7", "#00d4aa", "#f97316", "#e879f9",
    "#38bdf8", "#a3e635", "#fb923c", "#f472b6",
    "#34d399", "#fbbf24",
]

MAT_BG   = "#12151f"
MAT_TEXT = "#c8ccec"


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grafo EDA2 — Visualizador de SCC & Conectividade")
        self.root.geometry("1280x820")
        self.root.configure(bg=BG_DARK)
        self.root.minsize(960, 680)

        self.caminho_arquivo = ""
        self.grafo_entrada   = []
        self.sccs            = []
        self.conexoes_sugeridas = []

        self._build_layout()
        self._configure_matplotlib()
        self._draw_empty_state()

    # Layout 
    def _build_layout(self):
        topbar = tk.Frame(self.root, bg=BG_PANEL, height=52)
        topbar.pack(side=tk.TOP, fill=tk.X)
        topbar.pack_propagate(False)

        tk.Label(topbar, text="⬡", font=("Segoe UI", 18), bg=BG_PANEL,
                 fg=ACCENT).pack(side=tk.LEFT, padx=(18, 6), pady=10)
        tk.Label(topbar, text="Grafo EDA2", font=("Segoe UI", 13, "bold"),
                 bg=BG_PANEL, fg=TEXT_PRIMARY).pack(side=tk.LEFT, pady=10)
        tk.Label(topbar, text="SCC & Conectividade", font=("Segoe UI", 10),
                 bg=BG_PANEL, fg=TEXT_MUTED).pack(side=tk.LEFT, padx=(8, 0), pady=10)

       
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)

        # Container principal
        main = tk.Frame(self.root, bg=BG_DARK)
        main.pack(fill=tk.BOTH, expand=True)

        # Painel Lateral 
        sidebar = tk.Frame(main, bg=BG_PANEL, width=270)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        tk.Frame(main, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

        self._build_sidebar(sidebar)

        #  Área Central dos Gráficos 
        center = tk.Frame(main, bg=BG_DARK)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._build_plots(center)

    def _build_sidebar(self, parent):
        pad = {"padx": 16, "fill": tk.X}

        # Arquivo
        self._section_label(parent, "ARQUIVO")
        self.btn_carregar = self._btn(
            parent, "📂  Carregar Grafo", self.acao_carregar,
            bg=BG_CARD, fg=TEXT_PRIMARY, active_bg=BG_HOVER
        )
        self.btn_carregar.pack(pady=(4, 2), **pad)

        self.lbl_arquivo = tk.Label(
            parent, text="Nenhum arquivo selecionado",
            font=("Segoe UI", 8), bg=BG_PANEL, fg=TEXT_DIM,
            wraplength=230, justify=tk.LEFT
        )
        self.lbl_arquivo.pack(anchor=tk.W, padx=16, pady=(0, 10))

        # Processamento
        self._section_label(parent, "PROCESSAMENTO")
        self.btn_processar = self._btn(
            parent, "▶  Processar Grafo", self.acao_processar,
            bg=ACCENT, fg="white", active_bg="#6355d4",
            state=tk.DISABLED
        )
        self.btn_processar.pack(pady=(4, 2), **pad)

        self.btn_limpar = self._btn(
            parent, "↺  Limpar", self.acao_limpar,
            bg=BG_CARD, fg=TEXT_MUTED, active_bg=BG_HOVER
        )
        self.btn_limpar.pack(pady=(2, 12), **pad)

        # Resultados
        self._section_label(parent, "RESULTADOS")
        self.results_frame = tk.Frame(parent, bg=BG_PANEL)
        self.results_frame.pack(fill=tk.X, padx=12)
        self._draw_empty_cards()

        # Log
        self._section_label(parent, "LOG")
        log_wrap = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDER,
                            highlightthickness=1)
        log_wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 12))

        self.log_area = tk.Text(
            log_wrap, font=("Consolas", 8), bg=BG_CARD, fg=TEXT_MUTED,
            insertbackground=TEXT_PRIMARY, relief=tk.FLAT,
            padx=8, pady=8, wrap=tk.WORD, state=tk.DISABLED
        )
        vsb = tk.Scrollbar(log_wrap, orient=tk.VERTICAL,
                           command=self.log_area.yview, bg=BG_CARD)
        self.log_area.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_area.pack(fill=tk.BOTH, expand=True)

        self._log("Pronto. Carregue um arquivo .txt para começar.", "dim")

    def _build_plots(self, parent):
        # Tabs no topo
        tabbar = tk.Frame(parent, bg=BG_PANEL, height=40)
        tabbar.pack(fill=tk.X)
        tabbar.pack_propagate(False)
        tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X)

        self.tab_var = tk.IntVar(value=0)
        self._tab_btns = []
        for i, label in enumerate(["Grafo Original", "Grafo Final"]):
            b = tk.Button(
                tabbar, text=label,
                font=("Segoe UI", 9),
                bg=BG_PANEL, fg=ACCENT if i == 0 else TEXT_MUTED,
                activebackground=BG_PANEL, activeforeground=ACCENT,
                relief=tk.FLAT, bd=0, padx=18, pady=10,
                cursor="hand2",
                command=lambda idx=i: self._switch_tab(idx)
            )
            b.pack(side=tk.LEFT)
            self._tab_btns.append(b)

        # Canvas matplotlib
        plot_wrap = tk.Frame(parent, bg=PLOT_BG)
        plot_wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.fig, self.axes = plt.subplots(1, 2, figsize=(12, 7))
        self.fig.patch.set_facecolor(PLOT_BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_wrap)
        self.canvas.get_tk_widget().configure(bg=PLOT_BG, highlightthickness=0)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self._current_tab = 0

    # Helpers visuais 
    def _section_label(self, parent, text):
        f = tk.Frame(parent, bg=BG_PANEL)
        f.pack(fill=tk.X, padx=16, pady=(14, 4))
        tk.Label(f, text=text, font=("Segoe UI", 7, "bold"),
                 bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT)
        tk.Frame(f, bg=BORDER, height=1).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

    def _btn(self, parent, text, cmd, bg, fg, active_bg, state=tk.NORMAL):
        b = tk.Button(
            parent, text=text, command=cmd,
            font=("Segoe UI", 9), bg=bg, fg=fg,
            activebackground=active_bg, activeforeground=fg,
            relief=tk.FLAT, bd=0, padx=12, pady=8,
            cursor="hand2", state=state
        )
        return b

    def _draw_empty_cards(self):
        for w in self.results_frame.winfo_children():
            w.destroy()
        self._stat_card("SCCs", "—", TEXT_DIM)
        self._stat_card("Nós", "—", TEXT_DIM)
        self._stat_card("Arestas sugeridas", "—", TEXT_DIM)

    def _stat_card(self, label, value, color):
        card = tk.Frame(self.results_frame, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill=tk.X, pady=3)
        tk.Label(card, text=label, font=("Segoe UI", 8),
                 bg=BG_CARD, fg=TEXT_DIM).pack(anchor=tk.W, padx=10, pady=(6, 0))
        tk.Label(card, text=str(value), font=("Segoe UI", 16, "bold"),
                 bg=BG_CARD, fg=color).pack(anchor=tk.W, padx=10, pady=(0, 6))

    def _update_cards(self):
        for w in self.results_frame.winfo_children():
            w.destroy()
        self._stat_card("SCCs encontrados", len(self.sccs), ACCENT)
        self._stat_card("Nós no grafo", len(self.grafo_entrada), ACCENT2)
        n_sug = len(self.conexoes_sugeridas)
        color = SUCCESS if n_sug == 0 else WARNING
        val = "Já conexo ✓" if n_sug == 0 else n_sug
        self._stat_card("Arestas sugeridas", val, color)

    def _log(self, text, tipo="normal"):
        tags = {
            "normal": TEXT_MUTED,
            "ok":     SUCCESS,
            "warn":   WARNING,
            "err":    DANGER,
            "accent": ACCENT,
            "dim":    TEXT_DIM,
        }
        color = tags.get(tipo, TEXT_MUTED)
        self.log_area.configure(state=tk.NORMAL)
        self.log_area.insert(tk.END, text + "\n", tipo)
        self.log_area.tag_configure(tipo, foreground=color)
        self.log_area.see(tk.END)
        self.log_area.configure(state=tk.DISABLED)

    def _configure_matplotlib(self):
        plt.rcParams.update({
            "figure.facecolor":  PLOT_BG,
            "axes.facecolor":    PLOT_BG,
            "text.color":        MAT_TEXT,
            "axes.titlecolor":   TEXT_PRIMARY,
            "axes.titlesize":    11,
            "axes.titleweight":  "bold",
        })

    def _switch_tab(self, idx):
        self._current_tab = idx
        for i, b in enumerate(self._tab_btns):
            b.configure(fg=ACCENT if i == idx else TEXT_MUTED)
        # Mostra/oculta eixos
        self.axes[0].set_visible(idx == 0)
        self.axes[1].set_visible(idx == 1)
        self.canvas.draw()

    # Estado vazio 
    def _draw_empty_state(self):
        for ax in self.axes:
            ax.clear()
            ax.set_facecolor(PLOT_BG)
            ax.set_xticks([]); ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
        self.axes[0].text(0.5, 0.52, "⬡", fontsize=48, ha="center", va="center",
                          color=BORDER, transform=self.axes[0].transAxes)
        self.axes[0].text(0.5, 0.38, "Carregue um arquivo .txt\npara visualizar o grafo",
                          fontsize=10, ha="center", va="center", color=TEXT_DIM,
                          transform=self.axes[0].transAxes, linespacing=1.8)
        self.axes[0].set_title("Grafo Original")
        self.axes[1].text(0.5, 0.52, "⬡", fontsize=48, ha="center", va="center",
                          color=BORDER, transform=self.axes[1].transAxes)
        self.axes[1].text(0.5, 0.38, "Processe o grafo\npara ver as sugestões",
                          fontsize=10, ha="center", va="center", color=TEXT_DIM,
                          transform=self.axes[1].transAxes, linespacing=1.8)
        self.axes[1].set_title("Grafo Final (Sugestões)")
        self.axes[0].set_visible(True)
        self.axes[1].set_visible(False)
        self.canvas.draw()

    # Ações 
    def acao_carregar(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not path:
            return
        try:
            self.caminho_arquivo = path
            fname = path.split("/")[-1].split("\\")[-1]
            self.lbl_arquivo.configure(text=fname, fg=ACCENT2)
            self.log_area.configure(state=tk.NORMAL)
            self.log_area.delete(1.0, tk.END)
            self.log_area.configure(state=tk.DISABLED)
            self._log(f"✓ {fname} carregado", "ok")

            self.grafo_entrada = logic.carregar_grafo(self.caminho_arquivo)
            self._log(f"  {len(self.grafo_entrada)} nós lidos", "dim")

            xs = [n.x for n in self.grafo_entrada]
            ys = [n.y for n in self.grafo_entrada]
            if all(x == 0 for x in xs) and all(y == 0 for y in ys):
                self._log("⚠ Todos os nós em (0,0) — use coordenadas distintas", "warn")

            self.sccs = []
            self.conexoes_sugeridas = []
            self._draw_empty_cards()
            self._draw_original_only()
            self.btn_processar.configure(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Erro de Leitura", str(e))
            self._log(f"✗ {e}", "err")

    def acao_processar(self):
        try:
            if not self.grafo_entrada:
                return
            self._log("\n▶ Iniciando processamento…", "accent")

            # SCCs
            g_trabalho = logic.ops.copy_graph(self.grafo_entrada)
            self.sccs = []
            while g_trabalho:
                gi  = logic.ops.inverted(g_trabalho)
                sni = logic.DFS_visit(gi)
                sn  = g_trabalho[logic.Node.find_node(g_trabalho, sni)]
                bfg  = logic.BFS(g_trabalho, sn)
                bfgi = logic.BFS(gi, sni)
                scc  = logic.ops.intersect(bfg, bfgi)
                self.sccs.append(scc)
                g_trabalho = logic.ops.minus(g_trabalho, scc)

            self._log(f"  {len(self.sccs)} SCC(s) encontrado(s)", "ok")
            for i, scc in enumerate(self.sccs):
                cor = SCC_COLORS[i % len(SCC_COLORS)]
                nomes = ", ".join(n.name for n in scc)
                self._log(f"  [{i+1}] {nomes}", "normal")

            # Sugestões de conexão
            self.conexoes_sugeridas = []
            sccs_ativos = list(self.sccs)
            while len(sccs_ativos) > 1:
                menor_dist = float("inf")
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
                for n in sccs_ativos[indices[0]]:
                    for neigh in self.grafo_entrada[Node.find_node(self.grafo_entrada, n)].neighbors:
                        if Node.find_node(sccs_ativos[indices[1]], neigh) != -1:
                            ab_ba = (True, False)
                            break
                if not ab_ba[0]:
                    for m in sccs_ativos[indices[1]]:
                        for meigh in self.grafo_entrada[Node.find_node(self.grafo_entrada, m)].neighbors:
                            if Node.find_node(sccs_ativos[indices[0]], meigh) != -1:
                                ab_ba = (False, True)
                                break
                if par_escolhido[0]:
                    n1, n2 = par_escolhido
                    self.conexoes_sugeridas.append((n1.name, n2.name, menor_dist, ab_ba))
                    idx1, idx2 = indices
                    sccs_ativos[idx1] = ops.dumb_unite(sccs_ativos[idx1], sccs_ativos[idx2])
                    sccs_ativos.pop(idx2)

            if self.conexoes_sugeridas:
                self._log(f"\n💡 {len(self.conexoes_sugeridas)} aresta(s) sugerida(s):", "warn")
                for u, v, d, ab in self.conexoes_sugeridas:
                    seta = f"{'<' if not ab[1] else ''}-{'>' if not ab[0] else ''}"
                    self._log(f"  {u} {seta} {v}  (dist: {d:.1f})", "normal")
            else:
                self._log("✓ Grafo já é fortemente conexo!", "ok")

            self._update_cards()
            self._draw_grafos()
            self._switch_tab(0)
            self._log("\n✓ Concluído.", "ok")

        except Exception as e:
            messagebox.showerror("Erro de Processamento", str(e))
            self._log(f"✗ {e}", "err")

    def acao_limpar(self):
        self.caminho_arquivo   = ""
        self.grafo_entrada     = []
        self.sccs              = []
        self.conexoes_sugeridas = []
        self.lbl_arquivo.configure(text="Nenhum arquivo selecionado", fg=TEXT_DIM)
        self.btn_processar.configure(state=tk.DISABLED)
        self.log_area.configure(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.configure(state=tk.DISABLED)
        self._log("Área limpa. Carregue um arquivo.", "dim")
        self._draw_empty_cards()
        self._draw_empty_state()

    # Plotagem 
    def _preparar_nx(self, nodes_list, extra_edges=None):
        G = nx.DiGraph()
        node_map = {n.name: n for n in nodes_list}
        pos = {}
        for name, node in node_map.items():
            G.add_node(name)
            pos[name] = (node.x, node.y)
        for name, node in node_map.items():
            for nb in node.neighbors:
                G.add_edge(name, nb.name)
        if extra_edges:
            for u, v in extra_edges:
                G.add_edge(u, v)
        return G, pos

    def _scc_color_map(self, G):
       
        color_map = {}
        for i, scc in enumerate(self.sccs):
            c = SCC_COLORS[i % len(SCC_COLORS)]
            for n in scc:
                color_map[n.name] = c
        # fallback para nós sem SCC
        for name in G.nodes():
            if name not in color_map:
                color_map[name] = TEXT_DIM
        return color_map

    def _draw_original_only(self):
        ax = self.axes[0]
        ax.clear()
        ax.set_facecolor(PLOT_BG)
        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)

        G, pos = self._preparar_nx(self.grafo_entrada)
        if not pos:
            return

        pos = self._normalize_pos(pos)
        node_colors = [BG_HOVER] * len(G.nodes())

        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=700,
                               node_color=node_colors,
                               edgecolors=ACCENT, linewidths=1.5)
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=9,
                                font_color=TEXT_PRIMARY, font_weight="bold")
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=TEXT_DIM,
                               width=1.2, arrows=True, arrowsize=14,
                               connectionstyle="arc3,rad=0.1",
                               arrowstyle="-|>",
                               node_size=700)
        ax.set_title("Grafo Original", color=TEXT_PRIMARY)
        ax.axis("off")

        self.axes[1].set_visible(False)
        self.axes[0].set_visible(True)
        self.canvas.draw()

    def _draw_grafos(self):
        ax0 = self.axes[0]
        ax0.clear()
        ax0.set_facecolor(PLOT_BG)
        for spine in ax0.spines.values():
            spine.set_edgecolor(BORDER)

        G_orig, pos = self._preparar_nx(self.grafo_entrada)
        pos = self._normalize_pos(pos)
        c_map = self._scc_color_map(G_orig)

        node_colors_orig = [c_map.get(n, BG_HOVER) for n in G_orig.nodes()]
        nx.draw_networkx_nodes(G_orig, pos, ax=ax0, node_size=750,
                               node_color=node_colors_orig,
                               edgecolors=BG_DARK, linewidths=1.8)
        nx.draw_networkx_labels(G_orig, pos, ax=ax0, font_size=9,
                                font_color="white", font_weight="bold")
        nx.draw_networkx_edges(G_orig, pos, ax=ax0, edge_color="#3a3f5c",
                               width=1.3, arrows=True, arrowsize=14,
                               connectionstyle="arc3,rad=0.08",
                               node_size=750)

        # Legenda SCCs
        patches = []
        for i, scc in enumerate(self.sccs):
            c = SCC_COLORS[i % len(SCC_COLORS)]
            nomes = ",".join(n.name for n in scc)
            patches.append(mpatches.Patch(color=c, label=f"SCC {i+1}: {nomes}"))
        if patches:
            ax0.legend(handles=patches, loc="lower left", fontsize=7,
                       facecolor=BG_CARD, edgecolor=BORDER,
                       labelcolor=TEXT_MUTED, framealpha=0.85)

        ax0.set_title("Grafo Original — SCCs coloridos", color=TEXT_PRIMARY)
        ax0.axis("off")

        # grafo final com sugestões 
        ax1 = self.axes[1]
        ax1.clear()
        ax1.set_facecolor(PLOT_BG)
        for spine in ax1.spines.values():
            spine.set_edgecolor(BORDER)

        # Arestas novas
        extra = []
        for u, v, _, ab in self.conexoes_sugeridas:
            if not ab[0]: extra.append((u, v))
            if not ab[1]: extra.append((v, u))

        G_final, _ = self._preparar_nx(self.grafo_entrada, extra_edges=extra)
        node_colors_final = [c_map.get(n, BG_HOVER) for n in G_final.nodes()]

        nx.draw_networkx_nodes(G_final, pos, ax=ax1, node_size=750,
                               node_color=node_colors_final,
                               edgecolors=BG_DARK, linewidths=1.8)
        nx.draw_networkx_labels(G_final, pos, ax=ax1, font_size=9,
                                font_color="white", font_weight="bold")

        # Arestas originais
        nx.draw_networkx_edges(G_final, pos, ax=ax1,
                               edgelist=list(G_orig.edges()),
                               edge_color="#3a3f5c", width=1.3,
                               arrows=True, arrowsize=14,
                               connectionstyle="arc3,rad=0.08",
                               node_size=750)

        # Arestas sugeridas
        if extra:
            nx.draw_networkx_edges(G_final, pos, ax=ax1,
                                   edgelist=extra,
                                   edge_color=ACCENT2, width=2.2,
                                   style="dashed", arrows=True, arrowsize=18,
                                   connectionstyle="arc3,rad=0.18",
                                   node_size=750)
            patch_sug = mpatches.Patch(color=ACCENT2, label="Arestas sugeridas")
            ax1.legend(handles=[patch_sug], loc="lower left", fontsize=7,
                       facecolor=BG_CARD, edgecolor=BORDER,
                       labelcolor=TEXT_MUTED, framealpha=0.85)

        title_suffix = "" if self.conexoes_sugeridas else " ✓ Já conexo"
        ax1.set_title(f"Grafo Final{title_suffix}", color=TEXT_PRIMARY)
        ax1.axis("off")

        self.fig.tight_layout(pad=3.0)
        self.axes[0].set_visible(True)
        self.axes[1].set_visible(True)
        self.canvas.draw()

    def _normalize_pos(self, pos):
        if not pos:
            return pos
        xs = [v[0] for v in pos.values()]
        ys = [v[1] for v in pos.values()]
        if len(set(xs)) == 1 and len(set(ys)) == 1:
            G_temp = nx.DiGraph()
            G_temp.add_nodes_from(pos.keys())
            return nx.spring_layout(G_temp, seed=42)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        rx = max_x - min_x or 1
        ry = max_y - min_y or 1
        return {k: ((v[0]-min_x)/rx*0.85+0.075, (v[1]-min_y)/ry*0.85+0.075)
                for k, v in pos.items()}


if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap(None)
    except Exception:
        pass
    app = GraphApp(root)
    root.mainloop()