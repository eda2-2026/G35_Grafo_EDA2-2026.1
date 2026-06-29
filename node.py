class Node:

    def __init__(self, name: str, x: float, y: float):

        self.name = name # Nome, deve ser único

        self.x = x # Posição em X

        self.y = y # Posição em Y

        self.neighbors = [] # arestas (vizinhos)





    # cria uma aresta entre esses nós e os nós em "lista_nós"

    # pode ser chamada com uma quantidade arbitraria de argumentos no.connect(no1, no2, no3)

    # ou com uma lista desempacotada: no.connect(*nos_para_conectar)

    def connect(self, *node: Node) -> None:

        for n in node:

            self.neighbors.append(n)





    # Imprime a lista de vizinhos por nome

    def print_vizinhos(self) -> None:

        print("[", end="")



        for i in range(0,len(self.neighbors)-1):

            print(self.neighbors[i].name, end=", ")



        if(self.neighbors):

            print(self.neighbors[-1].name, end="")

        print("]")

   

    # Compara dois nós

    def equals(self, node: Node) -> bool:

        return self.name == node.name and self.x == node.x and self.y == node.y



    # Copia o nó, mas não suas arestas

    def copy_shallow(self) -> Node:

        c = Node(self.name, self.x, self.y)

        return c



    # Encontra um nó em um grafo e retorna o índice

    def find_node(graph: list[Node], node: Node) -> int:

        for i in range(0, len(graph)):

            if(node.equals(graph[i])):

                return i

        return -1

   

    # Encontra um nó em um grafo (a partir do nome) e retorna o índice

    def find_node_by_name(graph: list[Node], name: str) -> int:

        for i in range(0, len(graph)):

            if(graph[i].name == name):

                return i

        return -1

if __name__ == "__main__":

    print("Rodando o arquivo node.py, você quis dizer main.py?")

