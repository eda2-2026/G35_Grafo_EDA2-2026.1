from node import *

import vals as dbg



# Dados adicionais necessários para DFS visit (hash de nós visitados e o último nó removido do stack)

class _DFS_Data:

    def __init__(self):

        self.visited = set()

        self.last = Node("Vazio", 0, 0)



# Devolve um nó em componente source

def DFS_visit(g: list[Node]) -> Node:

    data = _DFS_Data()

    next = 0

    while(next != -1):

        if(dbg.debug and dbg.rich):

            print(f"DFS_visit({g[next].name})...")

        _DFS_visit(g[next], data)

        next = _DFS_first_unvisited(g, data)

    if(dbg.debug and dbg.rich):

        print("-=-=-=-=-=-=-")

    return data.last



# recursivo

def _DFS_visit(n: Node, data: _DFS_Data):

    data.visited.add(n)

    for v in n.neighbors:

        if(v not in data.visited):

            _DFS_visit(v, data)

    data.last = n

   

# retorna o índice do primeiro nó não visitado

def _DFS_first_unvisited(g: list[Node], data: _DFS_Data) -> int:

    for i in range(0, len(g)):

        if(g[i] not in data.visited):

            return i

    return -1





if __name__ == "__main__":

    print("Rodando o arquivo dfs.py, você quis dizer main.py?")

