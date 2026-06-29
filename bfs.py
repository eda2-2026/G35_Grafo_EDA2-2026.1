from collections import deque

from node import *

import graph_ops as ops



class _BFS_Data:

    def __init__(self):

        self.visited = set()

        self.q = deque()

    def queue(self, n):

        self.q.append(n)

    def dequeue(self):

        return self.q.popleft()





def BFS(graph: list[Node], node: Node) -> list[Node]:

    data = _BFS_Data()

    g = []



    _BFS(node, data)

    while(data.q):

        _BFS(data.dequeue(), data)



    for n in graph:

        if(n in data.visited):

            g.append(n.copy_shallow())



    for n in g:

        for neigh in graph[Node.find_node(graph, n)].neighbors:

            if(neigh in data.visited):

                n.connect(g[Node.find_node(g, neigh)])

               



    # ops.print_graph(g)



    return g





def _BFS(node: Node, data: _BFS_Data):

    data.visited.add(node)



    for neigh in node.neighbors:

        if(neigh not in data.visited):

            data.queue(neigh)