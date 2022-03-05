#!/usr/bin/env python

import sys

from functools import partial

from mininet.net import Mininet
from mininet.node import UserSwitch, OVSKernelSwitch, Controller
from mininet.topo import Topo
from mininet.log import lg, info
from mininet.util import irange, quietRun
from mininet.link import TCLink
from mininet.cli import CLI
flush = sys.stdout.flush


class ClusterTopo( Topo ):

    def build( self):
        switchCounter = 3
        numberOfRacks = 16 #should always be a power of 2
        serversPerRack = 10
        numberOfT2Switches = numberOfRacks //4
        numberOfT1Switches = numberOfT2Switches//2
        borderRouter = self.addSwitch('s0')
        access1 = self.addSwitch('s1')
        access2 = self.addSwitch('s2')
        self.addLink(borderRouter, access1)
        self.addLink(borderRouter, access2)
        t1Switches = []
        t2Switches = []
        torSwitches = []
        hosts = []
        for rack in range(numberOfRacks):
            torSwitches.append(self.addSwitch('s' + str(switchCounter)))
            switchCounter += 1
            for server in range(serversPerRack):
                hosts.append(self.addHost('h'+str(rack*10 + server)))
                self.addLink(hosts[rack*10 + server], torSwitches[rack])
        for t2Switch in range(numberOfT2Switches):
            crossTierLinks = numberOfRacks // numberOfT2Switches
            t2Switches.append(self.addSwitch('s'+str(switchCounter)))
            switchCounter += 1
            for s in range(t2Switch*crossTierLinks, t2Switch*crossTierLinks + crossTierLinks):
                self.addLink(t2Switches[t2Switch], torSwitches[s])
        for t1Switch in range(numberOfT1Switches):
            crossTierLinks = numberOfT2Switches//numberOfT1Switches
            t1Switches.append(self.addSwitch('s'+str(switchCounter)))
            switchCounter += 1
            for s in range(t1Switch*crossTierLinks, t1Switch*crossTierLinks+crossTierLinks):
                self.addLink(t1Switches[t1Switch], t2Switches[s])
            if t1Switch < numberOfT2Switches//2:
                self.addLink(t1Switches[t1Switch], access1)
            else:
                self.addLink(t1Switches[t1Switch], access2)

topo = ClusterTopo()
net = Mininet(topo)
net.start()
CLI(net)
net.stop()

