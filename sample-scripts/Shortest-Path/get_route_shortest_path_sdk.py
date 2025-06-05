#!/usr/bin/python3

import sys
from com.cisco.wae.opm.network import open_plan
from com.cisco.wae.opm.network.simulation.route import RouteSimulation
from com.cisco.wae.opm.network.simulation.route.manager import RouteManager

input_pln = sys.argv[1]
node_a = sys.argv[2]
node_b = sys.argv[3]
metric_type = sys.argv[4]
traffic = sys.argv[5]
cp_host = sys.argv[6]
cp_port = sys.argv[7]
protocol = 'ssl'


with open_plan(input_pln, cp_host, cp_port, protocol) as network:

    model = network.model
    nodes = model.nodes
    route_simulation = RouteSimulation(model)
    node_src = nodes[{'name':node_a}]
    node_dst = nodes[{'name':node_b}]
    route = route_simulation.shortest_path(node_src,node_dst,metric_type)
    route_interfaces = route.interfaces

    routing_path = []
    for route_interface in route_interfaces:
        routing_path.append(route_interface.key)

    route_interface_util_list = []
    for interface in route.interface_usage:
        if interface.simulated_capacity:
            route_interface_util_list.append((interface.simulated_traffic + float(traffic))/interface.simulated_capacity*100)
            route_interface_util_list.sort(reverse=True)

    route_details = {
        "minimum_latency": round(route.minimum_latency, 2),
        "average_latency": round(route.average_latency, 2),
        "maximum_latency": round(route.maximum_latency, 2),
        "total_path_metric": route.total_path_metric,
        "maximum_interface_utilization": round(route_interface_util_list[0], 2),
        "routing_path": str(routing_path)
        }
    print(route_details)