from pox.lib.util import dpid_to_str

class Topology:
    SWITCH = 'switch'
    NEIGHBOURS = 'neighbours'

    # estructura de la todopologia
    # {    
    #   dpid => {
    #             SWITCH => SwitchController
    #             NEIGHBOURS => [dpid's ...]
    #           } 
    # }

    def ___init__(self):
        self.graph = {}


    def add_switch(self, dpid, switch):
        entry = {SWITCH: switch, NEIGHBOURS: []}
        self.graph[dpid_to_str(dpid)] = entry


    def add_link(self, link):
        dpid1 = dpid_to_str(link.dpid1)
        dpid2 = dpid_to_str(link.dpid2)

        # agrega el link a los switch_controllers
        self.graph[dpid1][SWITCH].add_link(link)
        self.graph[dpid2][SWITCH].add_link(link)
        
        # setea los dpis vecinos para ambos switches
        # conectados al link
        self.graph[dpid1][NEIGHBOURS].append(dpid2)
        self.graph[dpid2][NEIGHBOURS].append(dpid1)


    def remove_switch(self, dpid):
        # primero buscamos para todos los vecinos del switch removido
        # y lo removemos de su lista de vecinos
        for neighbour in self.graph[dpid_to_str(dpid)][NEIGHBOURS]:
            self.graph[neighbour][NEIGHBOURS].remove(dpid_to_str(dpid))
        
        # removemos el switch del grafo
        del self.graph[dpid_to_str(dpid)]


    def get_shortest_path(self, dpid_from, dpid_to):
        # devuelve el camino mas corto para ir desde
        # un switch dpid_from hasta un switch dpid_to
        
        shortest_paths = _dijkstra(dpid_to_str(dpid_from))

        # de los caminos minimos, buscamos en aquel que 
        # que termina en un switch con dpid_to 
        for path in shortest_paths:
            last_swithc = path[-1]

            if last_swithc.dpid == dpid_to:
                return path

        # devolvemos None si no se encontro ningun camino
        # de dpid_from a dpid_to
        return None

    def __min_distance(dist, visited)
        # A utility function to find the vertex with
        # minimum distance value, from the set of vertices
        # not yet included in shortest path tree

    def __are_neighbours(dpid_i, dpid_j)

    def _dijkstra(self, dpid_src):
        # devuelve el camino minimo del switch dpid_src
        # a todos los otros switches de la todopologia

        # la cantidad de vertices es la cantidad de 
        # switches en nuestra topologia
        num_switches = len(self.graph)

        dist = {}
        visited = {}

        # inicializamos las distancias de todos los
        # switches y los marcamos como no visitados
        for dpid in self.graph.keys():
            dist[dpid] = sys.maxsize
            visited[dpid] = False

        dist[dpid_src] = 0
 
        for count in num_switches:
 
            # Pick the minimum distance vertex from
            # the set of vertices not yet processed.
            # u is always equal to src in first iteration
            dpid_u = self.__min_distance(dist, visited)
 
            # Put the minimum distance vertex in the
            # shotest path tree
            visited[dpid_u] = True
 
            # Update dist value of the adjacent vertices
            # of the picked vertex only if the current
            # distance is greater than new distance and
            # the vertex in not in the shotest path tree
            for dpid_v in self.graph.keys():
                if __are_neighbours(dpid_u, dpid_v) and not visited[dpid_v] and 
                dist[dpid_v] > dist[dpid_u] + 1: # 1 poruqe asumimos que el la red no es pedsada
                
                    dist[dpid_v] = dist[dpid_u] + self.graph[dpid_u][dpid_v]