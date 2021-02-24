from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
from pox.host_tracker.host_tracker import host_tracker

log = core.getLogger()

class SwitchController:
    def __init__(self, dpid, connection, topology):
        self.connection = connection
        
        # El SwitchController se agrega como 
        # handler de los eventos del switch
        self.connection.addListeners(self)
        
        # This component attempts to keep track of hosts 
        # in the network where they are and how they are 
        # configured (at least their MAC/IP addresses).  
        # When things change, the component raises a HostEvent
        self.host_tracker = host_tracker()
        
        # repo de jemplo donde se explica el funcionamiento del host_tracker
        # https://github.com/kbmorris/sdn/blob/master/pox/misc/gephi_topo.py
        
        self.topology = topology
        self.dpid = dpid

        # cuenta la cantidad de paquetes que pasaron 
        # por el switch durante su tiempo de vida
        # self.packet_count = 0


    def _handle_PacketIn(self, event):
        # Esta funcion es llamada cada vez que el switch recibe un paquete
        # y no encuentra en su tabla una regla para rutearlo
        packet = event.parsed
        if not packet: return

        # packet.src -> src mac address 
        # packet.dst -> dst mac address
        if packet.type == 34525: return # sale ignorar ipv6

        log.info("Packet arrived to switch %s from %s to %s", \
                  self.dpid, packet.src, packet.dst)

        # obtenemos la mac del host al  
        # cual le queremos enviar el paquete 
        mac_entry = self.host_tracker.getMacEntry(packet.dst)

        if not mac_entry: return

        # primero revisamos si la mac esta conectada
        # a nostros (somos un switch del edge)
        output_port = self._calc_output_port(mac_entry)

        if output_port == None: return # descartamos

        log.info("HANDLE_PACKET_IN: output port %s", str(output_port))

        self._set_flow_table(event, output_port)
        #self._forward(event, output_port)


    def _calc_output_port(self, mac_entry):
        dpid = mac_entry.dpid

        # si nosotros somos el switch en que el host
        # esta conectado, devolvemos el puerto para 
        # fowardear el paquete a nuestro host
        if dpid == self.dpid: return mac_entry.port

        # obtenemos todos los switches que conforman
        # el camino al ultimo switch (en el que esta
        # conectado el switch con la mac_address)
        return self.topology.get_shortest_path_output_port(self.dpid, dpid)


    def _forward(self, event, output_port):
        # Instructs the switch to resend a packet that it had sent to us.

        msg = of.ofp_packet_out()
        msg.data = event.ofp

        # Add an action to send to the specified port
        action = of.ofp_action_output(port = output_port)
        msg.actions.append(action)

        # Send message to switch
        self.connection.send(msg)


    def _set_flow_table(self, event, output_port):
        log.info("Switch %s creating flow in output port %s", self.dpid, output_port)
        packet = event.parsed
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, event.port)
        msg.idle_timeout = 5
        msg.actions.append(of.ofp_action_output(port=output_port))
        msg.data = event.ofp
        self.connection.send(msg)


    def flush_flow_table(self):
        msg = of.ofp_flow_mod(command=of.OFPFC_DELETE)
        self.connection.send(msg)
