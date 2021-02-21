from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class SwitchData:
  def __init__(self, sw, port):
    self.switch = sw
    self.flow_count = 0
    self.port = port

class SwitchController:
  def __init__(self, dpid, connection, topology):
    self.dpid = dpid
    self.connection = connection
    # El SwitchController se agrega como handler de los eventos del switch
    self.connection.addListeners(self)
    self.links = []
    self.topology = topology

  def _handle_PacketIn(self, event):
    """
    Esta funcion es llamada cada vez que el switch recibe un paquete
    y no encuentra en su tabla una regla para rutearlo
    """
    packet = event.parsed
    log.info("Packet arrived to switch %s from %s to %s", self.dpid, packet.src, packet.dst)

    # TODO: Hay dos problemas a resolver:
    # Si es un link en el borde debe identificar si el paquete viene de un host conectado a el:
    # Si lo es, enviar a los otros host y/o enviar a la red
    # Si no lo es, no reinsertar en la red, distribuirlo a los host o descartarlo si no existen

    # Veo en donde estoy en la topologia
    # if self._is_end():
    #   self._send_to_host(event)
    # else:
    #   self._send_to_link(event)
    self._send_to_link(event)


  def addLink(self, sw, port):
    self.links.append(SwitchData(sw, port))
    log.info("SW %s connected to SW %s at port %s", self.dpid, sw.dpid, port)



  def _is_end(self):
    link_cnt = len(self.links)
    other_link_count = 0
    for sd in self.links:
      print("%s: %s, %s", sd.switch.dpid, len(sd.switch.links), link_cnt)
      if len(sd.switch.links) > other_link_count:
        other_link_count = len(sd.switch.links)

    return (other_link_count > link_cnt)


  def _send_to_host(self, event):
    packet = event.parsed  # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return
    #TODO: Implement send to host
    # Primera version deberia hacer flood a todos los host en el router
    # salvo que conozca exactamente la direccion
    log.info("Switch %s received and sending to host", self.dpid)


  def _send_to_link(self, event):
    # Lo dirijo a un link
    incoming_port = event.port
    incoming_links = None
    # Get which link sent the packet to determine direction of the flow
    for l in self.links:
      if l.port == incoming_port:
        incoming_links = len(l.switch.links)
        break

    #Get best upper or lower level link to establish a flow
    out = None
    if incoming_links > len(self.links): #Viene de abajo
      outputs = [sw for sw in self.links
                          if len(sw.switch.links) < len(self.links)]
      out = sorted(outputs, key=lambda x: x.flow_count)[0]
    else: # vienes de arriba
      outputs = [sw for sw in self.links
                 if len(sw.switch.links) > len(self.links)]
      out = sorted(outputs, key=lambda x: x.flow_count)[0]

    #Create flow matching all packet fields
    log.info("Switch %s received and sending to link %s", self.dpid, out.switch.dpid)
    packet = event.parsed
    out.flow_count += 1
    msg = of.ofp_flow_mod()
    msg.match = of.ofp_match.from_packet(packet, event.port)
    msg.idle_timeout = 30
    msg.actions.append(
      of.ofp_action_output(port=out.port))
    msg.data = event.ofp
    self.connection.send(msg)
