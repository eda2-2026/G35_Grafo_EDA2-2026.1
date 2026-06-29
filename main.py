import math
from node import Node
from dfs_visit import DFS_visit
from bfs import BFS
import graph_ops as ops
import vals as dbg
import sys

def calcular_distancia(n1, n2):
    return math.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2)

def carregar_grafo(caminho_arquivo):
    g = []
    with open(caminho_arquivo, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"): continue
            
            args = line.split()
            if len(args) == 3: # Nó: Nome X Y
                g.append(Node(args[0], float(args[1]), float(args[2])))
            elif len(args) == 2: # Aresta: Origem Destino
                if(args[0] == args[1]): continue # Ignora arestas de um nó à sí mesmo
                ind1 = Node.find_node_by_name(g, args[0])
                ind2 = Node.find_node_by_name(g, args[1])
                if ind1 != -1 and ind2 != -1:
                    g[ind1].connect(g[ind2])
    return g

def main():
    # Carrega o grafo original
    grafo_original = carregar_grafo(sys.argv[1])
    g_trabalho = ops.copy_graph(grafo_original)
    
    # Identifica os SCCs 
    sccs = []
    while g_trabalho:
        gi = ops.inverted(g_trabalho)
        sni = DFS_visit(gi) 
        sn = g_trabalho[Node.find_node(g_trabalho, sni)]
        
        bfg = BFS(g_trabalho, sn)
        bfgi = BFS(gi, sni)
        scc = ops.intersect(bfg, bfgi)
        
        sccs.append(scc)
        g_trabalho = ops.minus(g_trabalho, scc)

    print(f"Foram encontrados {len(sccs)} componentes fortemente conexos.")


    conexoes_sugeridas = []
    
    sccs_ativos = [s for s in sccs] 

    while len(sccs_ativos) > 1:
        menor_dist = float('inf')
        par_nós = (None, None)
        indices_scc = (0, 0)
        ab_ba = (False, False)

        for i in range(len(sccs_ativos)):
            for j in range(i + 1, len(sccs_ativos)):
                for no_a in sccs_ativos[i]:
                    for no_b in sccs_ativos[j]:
                        d = calcular_distancia(no_a, no_b)
                        if d < menor_dist:
                            menor_dist = d
                            par_nós = (no_a, no_b)
                            indices_scc = (i, j)
        
        # Checa se já existe conexão entre os sccs
        for n in sccs_ativos[indices_scc[0]]:
            for neigh in grafo_original[Node.find_node(grafo_original,n)].neighbors:
                # print(f"{n.name} -> {neigh.name} {Node.find_node(sccs_ativos[indices_scc[1]],neigh) == -1}")
                if(Node.find_node(sccs_ativos[indices_scc[1]],neigh) != -1):
                    ab_ba = (True, False)
                    break
        if(not ab_ba[0]):
            for m in sccs_ativos[indices_scc[1]]:
                for meigh in grafo_original[Node.find_node(grafo_original,m)].neighbors:
                    if(Node.find_node(sccs_ativos[indices_scc[0]], meigh) != -1):
                        ab_ba = (False, True)
                        break
        
        if par_nós[0]:
            n1, n2 = par_nós
            conexoes_sugeridas.append((n1.name, n2.name, menor_dist, ab_ba))
            # Une os SCCs na lista para a próxima iteração
            idx1, idx2 = indices_scc
            sccs_ativos[idx1] = ops.dumb_unite(sccs_ativos[idx1], sccs_ativos[idx2])
            sccs_ativos.pop(idx2)

    # Saída de Resultados
    print("\n--- Arestas sugeridas para conectividade total ---")
    for u, v, d, ab in conexoes_sugeridas:
        print(f"Unir {u} {"" if ab[0] else "<"}-{"" if ab[1] else ">"} {v} (Distância: {d:.2f})")

if __name__ == "__main__":
    main()
