"""
Este archivo ejemplifica la creacion de una topologia de mininet
En este caso estamos creando una topologia muy simple con la siguiente forma

   host --- switch --- switch --- host
"""

import os
from mininet.topo import Topo

TREE_LEVELS = 3

class Example( Topo ):
  def __init__( self, half_ports = 2, **opts ):
    Topo.__init__(self, **opts)

    n = TREE_LEVELS
    switches = {}

    for i in range(n):

        switches[i] = []
        for j in range (0, 2 ** i):
            sw = self.addSwitch("sw" + str(2 ** i + j))
            switches[i].append(sw)

        if i == 0:
            continue

        for sw1 in switches[i]:
            for sw2 in switches[i-1]:
                self.addLink(sw1, sw2)

    h1 = self.addHost("h1")
    h2 = self.addHost("h2")
    h3 = self.addHost("h3")

    self.addLink(switches[0][0], h1)
    self.addLink(switches[0][0], h2)
    self.addLink(switches[0][0], h3)

    for i in range(2 ** (n - 1)):
        hs = self.addHost("h" + str(4 + i))
        self.addLink(switches[n-1][i], hs)


topos = { 'example': Example }
