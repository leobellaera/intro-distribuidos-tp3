from pox.core import core
import pox.openflow.discovery
import pox.openflow.spanning_tree
import pox.forwarding.l2_learning
from pox.lib.util import dpid_to_str
from extensions.topology import Topology
from extensions.switch import SwitchController

log = core.getLogger()
table_idle_timeout = 30

class Controller:
    def __init__ (self):

        self.connections = set()
        self.topology = Topology()

        # Esperando que los modulos openflow y openflow_discovery esten listos
        core.call_when_ready(self.startup, ('openflow', 'openflow_discovery'))


    def startup(self):
        # Esta funcion se encarga de inicializar el controller
        # Agrega el controller como event handler para los
        # eventos de openflow y openflow_discovery

        core.openflow.addListeners(self)
        core.openflow_discovery.addListeners(self)
        log.info('Controller initialized')


    def _handle_ConnectionUp(self, event):
        # Esta funcion es llamada cada vez que un 
        # nuevo switch establece conexion
        # Se encarga de crear un nuevo switch controller 
        # para manejar los eventos de cada switch
        if event.connection not in self.connections:
            log.info("Switch %s has come up.", dpid_to_str(event.dpid))

            self.connections.add(event.connection)
            sc = SwitchController(event.dpid, event.connection, self.topology, table_idle_timeout)
            self.topology.add_switch(sc)


    def _handle_LinkEvent(self, event):
        # Esta funcion es llamada cada vez que 
        # openflow_discovery descubre un nuevo enlace
        
        link = event.link
        # link posee la sigueinte informacion
        # (dpid1, port1) ---------- (dpid2, port2)
        self.topology.flush_flow_tables()
        if event.added:
            log.info("Link up")
            self.topology.add_link(link)
        if event.removed:
            log.info("Link down")
            self.topology.remove_link(link)


    def _handle_ConnectionDown(self, event):
        # Esta funcion es llamada cada vez que un 
        # switch existente corta su conexion
        # Se encarga de remover el nuevo switch controller 
        # tanto de las conexiones como de la topologia
        self.topology.flush_flow_tables()
        if event.connection in self.connections:
            self.connections.remove(event.connection)
            self.topology.remove_switch(event.dpid)


def launch(ttl = 30):

    # Seteamos el ttl
    global table_idle_timeout
    table_idle_timeout = ttl

    # Inicializando el modulo openflow_discovery
    pox.openflow.discovery.launch()

    # Registrando el Controller en pox.core para 
    # que sea ejecutado
    core.registerNew(Controller)
