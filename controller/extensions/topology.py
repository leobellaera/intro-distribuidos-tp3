import sys
from random import sample
from pox.core import core
from collections import deque
from pox.lib.util import dpid_to_str

LINKS = 'links'
SWITCH = 'switch'
NEIGHBOURS = 'neighbours'

log = core.getLogger()

class Topology:
    def __init__(self):
        self.graph = {}


    def add_switch(self, switch):
        entry = {SWITCH: switch, NEIGHBOURS: [], LINKS: []}
        self.graph[dpid_to_str(switch.dpid)] = entry


    def get_switch(self, dpid):
        return self.graph[dpid_to_str(dpid)][SWITCH]


    def add_link(self, link):
        dpid1 = dpid_to_str(link.dpid1)
        dpid2 = dpid_to_str(link.dpid2)

        # agrega el link a los switch_controllers
        self.graph[dpid1][LINKS].append(link)
        self.graph[dpid2][LINKS].append(link)
        
        # setea los dpis vecinos para ambos switches
        # conectados al link
        self.graph[dpid1][NEIGHBOURS].append(dpid2)
        self.graph[dpid2][NEIGHBOURS].append(dpid1)


    def remove_link(self, link):
        dpid1 = dpid_to_str(link.dpid1)
        dpid2 = dpid_to_str(link.dpid2) 

        # quita el link a los switch_controllers
        self.graph[dpid1][LINKS] = filter(lambda x: x.uni != link.uni, self.graph[dpid1][LINKS])
        self.graph[dpid2][LINKS] = filter(lambda x: x.uni != link.uni, self.graph[dpid2][LINKS])
        
        # remueve los switches de la lista de vecinos 
        self.graph[dpid1][NEIGHBOURS].remove(dpid2)
        self.graph[dpid2][NEIGHBOURS].remove(dpid1)


    def remove_switch(self, dpid):
        # primero buscamos para todos los vecinos del switch removido
        # y lo removemos de su lista de vecinos

        dpid = dpid_to_str(dpid)
    
        for neighbour in self.graph[dpid][NEIGHBOURS]:
            self.graph[neighbour][NEIGHBOURS].remove(dpid)
        
        # removemos el switch del grafo
        del self.graph[dpid]


    def get_shortest_path_output_port(self, dpid_from, dpid_to):
        # devuelve el camino mas corto para ir desde
        # un switch dpid_from hasta un switch dpid_to

        shortest_path = self._shortest_path(dpid_to_str(dpid_from), dpid_to_str(dpid_to))

        sws_path = []
        for dpid in shortest_path:
            sws_path.append(self.graph[dpid][SWITCH])

        log.info('| TOPOLOGY | shortest path: %s', str(shortest_path))

        if len(sws_path) == 0: return None

        next_sw_to_go = sws_path[0]
        log.info('| TOPOLOGY | next_switch_to_go: %s', next_sw_to_go.dpid)

        # para el primer switch del camino, buscamos cual 
        # es el link adyacente a nostros y obtenemos el puerto
        # por el cual deberiamos forwardear el paquete para
        # enviarselo a el
        for link in self.graph[dpid_to_str(dpid_from)][LINKS]:
            log.info('| TOPOLOGY | link dpid 1: [%s] port 1: [%i]', dpid_to_str(link.dpid1), link.port1)
            log.info('| TOPOLOGY | link dpid 2: [%s] port 2: [%i]', dpid_to_str(link.dpid2), link.port2)

            if link.dpid1 == next_sw_to_go.dpid:
                return link.port2
            if link.dpid2 == next_sw_to_go.dpid:
                return link.port1

        return None


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

            for dpid_v in sample(self.graph[dpid_u][NEIGHBOURS], len(self.graph[dpid_u][NEIGHBOURS])):

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

    def flush_flow_tables(self):
        for switch in self.graph:
            self.graph[switch][SWITCH].flush_flow_table()
