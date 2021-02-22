from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.host_tracker.host_tracker import host_tracker

log = core.getLogger()

class SwitchController:
    def __init__(self, dpid, connection, topology):
-        self.connection = connection

        # El SwitchController se agrega como 
        # handler de los eventos del switch
        self.connection.addListeners(self)
        
        # This component attempts to keep track of hosts 
        # in the network – where they are and how they are 
        # configured (at least their MAC/IP addresses).  
        # When things change, the component raises a HostEvent
        self.host_tracker = host_tracker()
        
        # repo de jemplo donde se explica el funcionamiento del host_tracker
        # https://github.com/kbmorris/sdn/blob/master/pox/misc/gephi_topo.py
        
        self.topology = topology
        self.dpid = dpid
        self.links = []  


    def add_link(self, link):
        # se agrega un nuevo link del switch a otro
        # nuevo switch

        self.links.append(link)


    def _handle_PacketIn(self, event):
        # Esta funcion es llamada cada vez que el switch recibe un paquete
        # y no encuentra en su tabla una regla para rutearlo
        packet = event.parsed

        # packet.src -> src mac address 
        # packet.dst -> dst mac address
        log.info("Packet arrived to switch %s from %s to %s", \
                  self.dpid, packet.src, packet.dst)

        # obtenemos la mac del host al  
        # cual le queremos enviar el paquete 
        mac_entry = self.host_tracker.getMacEntry(packet.dst)

        # primero revisamos si la mac esta conectada
        # a nostros (somos un switch del edge)
        output_port = self._calc_output_port(mac_entry)
        self._forward(packet, output_port)


    def _calc_output_port(self, mac_entry):
        sw_with_macaddr = self.topology.get(mac_entry.dpid)
       
        # obtenemos todos los switches que conforman
        # el camino al ultimo switch (en el que esta
        # conectado el switch con la mac_address)
        sws_path = self.topology.get_shortest_path(dpid, sw_with_macaddr.dpid)    
        
        if len(sws_path) == 0: return None

        next_sw_to_go = sws_path[0]
        # para el primer switch del camino, buscamos cual 
        # es el link adyacente a nostros y obtenemos el puerto
        # por el cual deberiamos forwardear el paquete para
        # enviarselo a el
        for link in next_sw_to_go.links:
            if self._is_connected_to_me(link)
                return link.port1 if link.dpid2 == self.dpid else link.port2

        return None


    def _is_connected_to_me(self, link)
        # retorna true si una de las puntas del link 
        # posee nuestro dpid. De esa forma sabemos si 
        # somos una de las extremidades del switch
        return link.dpi1 == self.dpid or link.dpid2 == self.dpid


# TODO:
# programar el forward
# programar el djisktra o shortes path
