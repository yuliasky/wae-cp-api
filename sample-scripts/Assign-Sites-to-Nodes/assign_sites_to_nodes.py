#!/bin/python

import sys
from com.cisco.wae.opm.network import open_plan

input_pln = sys.argv[1]
output_pln = sys.argv[2]

with open_plan(input_pln) as network:

    model = network.model
    nodes = model.nodes

    for node in nodes:
        if not node.site:
            print("Node without site is: %-s" % node.name)
            site_name = node.name.split('.')[1]
            node.site = site_name
            
    network.write(output_pln)
