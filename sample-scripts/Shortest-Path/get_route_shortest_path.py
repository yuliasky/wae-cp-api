#!/bin/python

import sys
from com.cisco.wae.opm.network import open_plan
from com.cisco.wae.opm.network.simulation.route import RouteSimulation
from com.cisco.wae.opm.network.simulation.route.manager import RouteManager

input_pln = sys.argv[1]
node_a = sys.argv[2]
node_b = sys.argv[3]
metric_type = sys.argv[4]


with open_plan(input_pln) as network:

    model = network.model
    nodes = model.nodes
    route_simulation = RouteSimulation(model)
    route_manager = RouteManager(route_simulation)
    demands = route_manager.demands
    node_src = nodes[{'name':node_a}]
    node_dst = nodes[{'name':node_b}]
    route = route_simulation.shortest_path(node_src,node_dst,metric_type)
    route_interfaces = route.interfaces

    routing_path = []
    for route_interface in route_interfaces:
        routing_path.append(route_interface.key)

    route_interface_util_list = []
    for interface in route.interface_usage:
        route_interface_util_list.append(interface.simulated_utilization)
        route_interface_util_list.sort(reverse=True)

    route_details = {
        "minimum_latency": route.minimum_latency,
        "average_latency": route.average_latency,
        "maximum_latency": route.maximum_latency,
        "total_path_metric": route.total_path_metric,
        "maximum_interface_utilization": round(route_interface_util_list[0], 2),
        "routing_path": routing_path
        }
    print(route_details)