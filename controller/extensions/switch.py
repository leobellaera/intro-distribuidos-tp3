from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.host_tracker.host_tracker import host_tracker

log = core.getLogger()


class SwitchController:
    def __init__(self, dpid, connection, topology, table_hard_timeout):
        log.info(
            "New switch has come up, table_hard_timeout: %s",
            table_hard_timeout
        )
        self.connection = connection

        # El SwitchController se agrega como
        # handler de los eventos del switch
        self.connection.addListeners(self)

        # El host_tracker sirve para obtener las direcciones MAC
        # de los hosts de la red
        self.host_tracker = host_tracker()

        # repo de jemplo donde se explica el funcionamiento del host_tracker
        # https://github.com/kbmorris/sdn/blob/master/pox/misc/gephi_topo.py

        self.topology = topology
        self.dpid = dpid
        self.table_hard_timeout = table_hard_timeout

    def _handle_PacketIn(self, event):
        # Esta funcion es llamada cada vez que el switch recibe un paquete
        # y no encuentra en su tabla una regla para rutearlo
        packet = event.parsed
        if not packet:
            return

        # packet.src -> src mac address
        # packet.dst -> dst mac address
        if packet.type == 34525:
            # ignoramos paquetes ipv6
            return

        log.info(
            "Packet arrived to switch %s from %s to %s",
            self.dpid, packet.src, packet.dst
        )

        # obtenemos la mac del host al
        # cual le queremos enviar el paquete
        mac_entry = self.host_tracker.getMacEntry(packet.dst)

        if not mac_entry:
            return

        # primero revisamos si la mac esta conectada
        # a nostros (somos un switch del edge)
        output_port = self._calc_output_port(mac_entry)

        if output_port == None:
            # descartamos
            return

        log.info("HANDLE_PACKET_IN: output port %s", str(output_port))

        # enviamos el paquete a traves del puerto obtenido
        self._forward(event, output_port)
        # actualizamos la tabla de flujo
        self._set_flow_table(event, output_port)

    def _calc_output_port(self, mac_entry):
        dpid = mac_entry.dpid

        # si nosotros somos el switch en que el host
        # esta conectado, devolvemos el puerto para
        # fowardear el paquete a nuestro host
        if dpid == self.dpid:
            return mac_entry.port

        # obtenemos todos los switches que conforman
        # el camino al ultimo switch (en el que esta
        # conectado el switch con la mac_address)
        return self.topology.get_shortest_path_output_port(self.dpid, dpid)

    def _forward(self, event, output_port):
        # Se le indica al switch que envie el paquete que recibio

        msg = of.ofp_packet_out()
        msg.data = event.ofp

        # Indicamos la accion de mandar a traves del puerto output_port
        action = of.ofp_action_output(port=output_port)
        msg.actions.append(action)

        # Send message to switch
        self.connection.send(msg)

    def _set_flow_table(self, event, output_port):
        log.info(
            "Switch %s creating flow in output port %s",
            self.dpid, output_port
        )
        packet = event.parsed
        msg = of.ofp_flow_mod()

        header_l3 = packet.next
        segment_l4 = header_l3.next
        msg.match.dl_type = packet.type
        msg.match.nw_src = header_l3.srcip
        msg.match.nw_dst = header_l3.dstip
        msg.match.nw_proto = header_l3.protocol
        if (
            (header_l3.protocol == header_l3.TCP_PROTOCOL) or
            (header_l3.protocol == header_l3.UDP_PROTOCOL)
        ):
            msg.match.tp_src = segment_l4.srcport
            msg.match.tp_dst = segment_l4.dstport

        # msg.match = of.ofp_match.from_packet(packet, event.port)
        msg.hard_timeout = int(self.table_hard_timeout)
        msg.actions.append(of.ofp_action_output(port=output_port))
        # msg.data = event.ofp
        self.connection.send(msg)

    def flush_flow_table(self):
        msg = of.ofp_flow_mod(command=of.OFPFC_DELETE)
        self.connection.send(msg)
