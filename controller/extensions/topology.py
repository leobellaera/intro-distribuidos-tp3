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
