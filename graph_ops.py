from node import *





# Inversão de grafo

def inverted(graph : list[Node]) -> list[Node]:

    g = []



    # Nós

    for n in graph:

        g.append(n.copy_shallow())

   

    # Arestas

    for i in range(len(graph)-1, -1, -1):

        for j in range(len(graph[i].neighbors)-1, -1, -1):

            ind = Node.find_node(g, graph[i].neighbors[j])

            g[ind].connect(g[i])



    return g        





# Subtração de conjuntos

def minus(g1: list[Node], g2: list[Node]) -> list[Node]:

    g = []



    #Nós

    for n in g1:

        if(Node.find_node(g2, n) == -1):

            g.append(n.copy_shallow())

   



    # Arestas

    for n in g:

        for neigh in g1[Node.find_node(g1, n)].neighbors:

            ind = Node.find_node(g, neigh)

            if(ind != -1):

                n.connect(g[ind])

    return g



# União de conjuntos (burra por que não une as arestas)

def dumb_unite(g1: list[Node], g2: list[Node]) -> list[Node]:

    g = copy_graph(g1)



    g2start = len(g)



    # Nós

    for n in g2:

        g.append(n.copy_shallow())

   

    # Arestas

    for i in range(0, len(g2)):

        ind = i + g2start

        for neigh in g2[i].neighbors:

            ind2 = Node.find_node(g, neigh)

            g[ind].connect(g[ind2])





    return g



# Intersessão de conjuntos

def intersect(g1: list[Node], g2: list[Node]) -> list[Node]:

    g = []



    # nós

    for n in g1:

        if(Node.find_node(g2, n) != -1):

            g.append(n.copy_shallow())



    # Arestas

    for n in g:

        for neigh in g1[Node.find_node(g1, n)].neighbors:

            ind = Node.find_node(g, neigh)

            if(ind != -1):

                n.connect(g[ind])

    return g



# Imprime o grafo (nós e arestas)

def print_graph(graph: list[Node]) -> None:

    for n in graph:

        print(f"{n.name}->", end="")

        n.print_vizinhos()





# Faz uma cópia total do grafo

def copy_graph(graph: list[Node]) -> list[Node]:

    g = []

    for n in graph:

        g.append(n.copy_shallow())



    for i in range(0, len(g)):

        for neigh in graph[i].neighbors:

            ind = Node.find_node(g, neigh)

            g[i].connect(g[ind])

    return g