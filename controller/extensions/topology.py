from pox.lib.util import dpid_to_str

SWITCH = 'switch'
NEIGHBOURS = 'neighbours'

"""
{
    dpid = {
        switch: sw,
        neighbours = []
    }
}
"""

X puerto_enmtra------púerto_salida Y

# expects dpid as string
class Topology:
    def ___init__(self, n_switches):
        self.graph = {}

    def add_switch(self, dpid, switch):
        self.graph[dpid_to_str(dpid)] = {
            SWITCH: switch,
            NEIGHBOURS: [],
        }

    def add_link(self, link):
        dpid1 = dpid_to_str(link.dpid1)
        dpid2 = dpid_to_str(link.dpid2)
    
        self.graph[dpid1][NEIGHBOURS].append(dpid2)
        self.graph[dpid2][NEIGHBOURS].append(dpid1)

        self.graph[dpid1][SWITCH].add_link(link)
        self.graph[dpid2][SWITCH].add_link(link)

    def remove_switch(self, dpid):
        for neighbour in self.graph[dpid_to_str(dpid)][NEIGHBOURS]:
            self.graph[neighbour][NEIGHBOURS].remove(dpid_to_str(dpid))
        del self.graph[dpid_to_str(dpid)]

    def get_neighbour_switches(self, dpid):
        switches = []
        for neighbour in self.graph[dpid_to_str(dpid)][NEIGHBOURS]
            switches.append(self.graph[neighbour][SWITCH])
        return switches
