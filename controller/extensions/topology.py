import sys
from pox.core import core
from collections import deque
from pox.lib.util import dpid_to_str

SWITCH = 'switch'
NEIGHBOURS = 'neighbours'

log = core.getLogger()

class Topology:
    def __init__(self):
        self.graph = {}


    def add_switch(self, switch):
        entry = {SWITCH: switch, NEIGHBOURS: []}
        self.graph[dpid_to_str(switch.dpid)] = entry


    def get_switch(self, dpid):
        return self.graph[dpid_to_str(dpid)][SWITCH]


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

        shortest_path = self._shortest_path(dpid_to_str(dpid_from), dpid_to_str(dpid_to))

        sp_switch = []
        for dpid in shortest_path:
            sp_switch.append(self.graph[dpid][SWITCH])

        log.info('shortest path: %s', str(shortest_path))

        return sp_switch


    def __min_distance(self, dist, visited):
        # A utility function to find the vertex with
        # minimum distance value, from the set of vertices
        # not yet included in shortest path tree

        # Initilaize minimum distance for next node
        _min = sys.maxsize
 
        # Search not nearest vertex not in the
        # shortest path tree
        dpid_with_min_dist = None

        for dpid in self.graph.keys():
            if dist[dpid] < _min and not visited[dpid]:
                _min = dist[dpid]
                dpid_with_min_dist = dpid
 
        return dpid_with_min_dist


    def __are_neighbours(self, dpid_u, dpid_v):
        return dpid_v in self.graph[dpid_u][NEIGHBOURS]


    def _shortest_path(self, dpid_from, dpid_to):        
        log.info('Shortest path of from %s to %s', dpid_from, dpid_to)

        visited = {}
        parents = {}

        queue = deque()
        queue.append(dpid_from)

        visited[dpid_from] = True
        parents[dpid_from] = None

        while queue: # mientras tiene cosas
            dpid_u = queue.popleft()

            if dpid_u == dpid_to:
                break

            for dpid_v in self.graph[dpid_u][NEIGHBOURS]:

                if not dpid_v in visited:
                    visited[dpid_v] = True
                    parents[dpid_v] = dpid_u
                    queue.append(dpid_v)

        if not dpid_to in visited:
            return []
            
        dpid = dpid_to
        shortest_path =	[]
        
        while parents[dpid]:
            shortest_path.append(dpid)
            dpid = parents[dpid]
            
        shortest_path.reverse()
        return shortest_path
