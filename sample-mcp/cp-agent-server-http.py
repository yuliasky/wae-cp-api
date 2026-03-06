import os
from dotenv import load_dotenv, find_dotenv

# CP Design APIs
import com.cisco.wae.design
from com.cisco.wae.design.tools import SAFailureType
from com.cisco.wae.design.tools import SimAnalysis
from com.cisco.wae.design.tools import SimAnalysisOptions
from com.cisco.wae.design.model.net import TrafficLevelKey
from com.cisco.wae.design.model.net import NodeKey
from com.cisco.wae.design.model.net import QueueKey
from com.cisco.wae.design.model.net import InterfaceKey
from com.cisco.wae.design.sim import FailureScenarioRecord

# CP OPM APIs
from com.cisco.wae.opm.network import open_plan
from com.cisco.wae.opm.network.simulation.route import RouteSimulation
from com.cisco.wae.opm.network.simulation.route.manager import RouteManager

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

load_dotenv(find_dotenv())

auth = None

if len(os.getenv("AUTH_STATIC_TOKEN", "")) > 0:
    auth = StaticTokenVerifier({os.getenv("AUTH_STATIC_TOKEN"): {"scopes": ["read", "write"], "client_id": "static"}})

# Initialize FastMCP server
mcp = FastMCP("CP Agent MCP Prototype", include_fastmcp_meta=False, auth=auth)

# Constants
cp_host = '10.10.10.10'
cp_port = '30744'
protocol = 'ssl'
global_plan_file = '/opt/cw-plan-sdk/cw-planning/ai-agent/test_new_agent/plan_files/us_wan.txt'

# Helper Functions

def get_int_wc_util_traffic(int_wc_rec_list):
    # Get the worst case traffic utilization and its corresponding interface name
    int_wc_util_dic = {}
    index = 0
    for int_wc_rec in int_wc_rec_list:
        int_wc_util_dic[index] = {'iface':(int_wc_rec.iface.sourceKey.name + ':' + int_wc_rec.iface.name), 'wcUtil':int_wc_rec.wcUtil}
        index += 1
    int_wc_util_dic = dict(sorted(int_wc_util_dic.items(), key=lambda x: (x[1]['wcUtil']), reverse=True))
    first_value_wc_util = next(iter(int_wc_util_dic.values()), None)
    max_int_wc_util = {'maximum_worst_case_utilization_interface_name':first_value_wc_util['iface'],
                        'maximum_worst_case_interface_utilization_percentage': round(first_value_wc_util['wcUtil'], 2)}
    
    # Get the worst case traffic and its corresponding interface name
    int_wc_traffic_dic = {}
    index = 0
    for int_wc_rec in int_wc_rec_list:
        int_wc_traffic_dic[index] = {'iface':(int_wc_rec.iface.sourceKey.name + ':' + int_wc_rec.iface.name), 'wcTraffic':int_wc_rec.wcTraffic}
        index += 1
    int_wc_traffic_dic = dict(sorted(int_wc_traffic_dic.items(), key=lambda x: (x[1]['wcTraffic']), reverse=True))
    first_value_wc_traffic = next(iter(int_wc_traffic_dic.values()), None)
    max_int_wc_traffic = {'maximum_worst_case_traffic_interface_name':first_value_wc_traffic['iface'],
                        'maximum_worst_case_interface_traffic_Mbps': round(first_value_wc_traffic['wcTraffic'], 2)}

    merge_dict = max_int_wc_util.copy()
    merge_dict.update(max_int_wc_traffic)

    return merge_dict

# MCP tools

@mcp.tool()
async def get_worst_case_traffic_utilization(failure_type, plan_file=global_plan_file):
    """This function will query the underlying Crosswork Planning tool that will compute, for the network selected worst case failure scenarios.
    Based on the input parameter failure_type, the tool will compute among all possible failures of such type(s) what is the worst case utilization and traffic 
    across the entire network. It will return a dictionary that contains the details of the worst case data.

    Args:
        failure_type: {
                    "type":"List of strings",
                    "description":"Contains a list of the type or types of failures that we are interested in evaluating. It can be one or a combination of the following: Nodes, Circuits, Sites",
                    "examples": ["Nodes"], ["Circuits"], ["Nodes", "Circuits"], ["Sites"], ["Sites", "Nodes"], ... pay attention that all of them should have the first letter in uppercase
                }
        plan_file: {
                    "description":"Contains the name of the plan file that will be used to run the failure simulation",
                    "value": "The value will always be taken from a global variable called plan_file".
                }
    """
    with open(plan_file, 'rb') as file_r:
        # Establish connection with the CP server
        conn = com.cisco.wae.design.ServiceConnectionManager.newServiceConnection(cp_host, cp_port, protocol)
        # Read the input plan file and transform to Bytes
        plan = conn.getPlanManager().newPlanFromBytes(file_r.read())
        # Get access to the Tool Manager and Sim Analysis tool
        tool_manager = conn.getToolManager()
        sim_analysis = tool_manager.newSimAnalysis()

        traffic_level_key = plan.getNetwork().getTrafficLevelManager().getAllTrafficLevelKeys()[0].name

        failure_type_dic = {'Nodes':SAFailureType.SA_FAILURETYPE_NODES, 'Sites':SAFailureType.SA_FAILURETYPE_SITES, 'Circuits':SAFailureType.SA_FAILURETYPE_CIRCUITS,
            'Ports':SAFailureType.SA_FAILURETYPE_PORTS, 'PortCircuits':SAFailureType.SA_FAILURETYPE_PORTCIRCUITS}
        failure_type_list = []

        # Create a list with the different Failure Types selected by the user
        for failure in failure_type:
            failure_type_list.append(failure_type_dic[failure])

        # Set the structure with the options that will be passed for Sim Analysis execution
        sim_analysis_options = SimAnalysisOptions(
            failures=failure_type_list,
            trafficLevels=[TrafficLevelKey(name=traffic_level_key)]
        )

        # Run Sim Analysis tool
        sim_analysis.run(netObj=plan.getNetwork(), options=sim_analysis_options)

        # Get a list of records from Sim Analysis results with all interfaces worst-case attributes
        int_wc_rec_list = sim_analysis.getAllInterfaceWCRecords()
        # Call functions to get the Maximum Interface worst-case traffic and utilization values
        merge_dict = get_int_wc_util_traffic(int_wc_rec_list)

        # Close connection with CP server
        com.cisco.wae.design.ServiceConnectionManager.shutdownService(conn)

        return merge_dict

@mcp.tool()
async def run_specific_failure_simulation(object_name, object_type, plan_file=global_plan_file):
    """This function will query the underlying Crosswork Planning tool that will compute, for the network selected, a specific failure scenario.
    Based on the input parameters object_name and object_type. The tool will compute a failure of the object of such specific type, and will determine what is 
    interface with the maximum utilization and traffic after the failure is computed. It will return a dictionary that contains the details of most impacted 
    interface and its correspondng utilization and traffic, after the failure is computed.

    Args:
        object_name: {
                    "description":"Contains the name of the object that we are interested in evaluating the failure. If an interface is provided as object for evaluating the failure,
                    then the corresponding node name has to be provided too, and the object_name parameter will be formatted as node_name:interface_name",
                    "examples":"node_name:interface_name", "node_name" "node_name:site", "node_name.site", ...
                }
        object_type: {
                    "description":"Contains the type of the object that we are interested in evaluating the failure. It can be one of the following: node, interface".
                }
        plan_file: {
                    "description":"Contains the name of the plan file that will be used to run the failure simulation",
                    "value": "The value will always be taken from a global variable called plan_file".
                }
    """
    with open(plan_file, 'rb') as file_r:
        # Establish connection with the CP server
        conn = com.cisco.wae.design.ServiceConnectionManager.newServiceConnection(cp_host, cp_port, protocol)
        # Read the input plan file and transform to Bytes
        plan = conn.getPlanManager().newPlanFromBytes(file_r.read())
        # Get access to the Sim Manager
        sim = conn.getSimulationManager()

        traffic_lvl_manager = plan.getNetwork().getTrafficLevelManager()
        traffic_level = traffic_lvl_manager.getTrafficLevel(key=TrafficLevelKey(name='Default'))
        queue_manager = plan.getNetwork().getQueueManager()
        queue = queue_manager.getQueue(key=QueueKey(name=''))

        if object_type == "node":
            node_manager = plan.getNetwork().getNodeManager()
            if node_manager.hasNode(key=NodeKey(name=object_name)):
                node_key_list = [NodeKey(name=object_name)]
                failure_scenario_rec = FailureScenarioRecord(
                    nodeKeys=node_key_list
                )
                route_sim = sim.newRouteSimulation(plan=plan, failureScenario=failure_scenario_rec)
                traffic_sim = sim.newTrafficSimulation(routeSim=route_sim, trafficLevel=traffic_level, queue=queue)
            else:
                pass
        elif object_type == "interface":
            interface_manager = plan.getNetwork().getInterfaceManager()
            node_name = object_name.split(':')[0]
            int_name = object_name.split(':')[1]
            int_key = InterfaceKey(sourceKey=NodeKey(name=node_name), name=int_name)
            if interface_manager.hasInterface(key=int_key):
                interface = interface_manager.getInterface(key=int_key)
                circuit = interface.getCircuit()
                circuit_key = circuit.getKey()
                circuit_key_list = [circuit_key]
                failure_scenario_rec = FailureScenarioRecord(
                    circuitKeys=circuit_key_list
                )
                route_sim = sim.newRouteSimulation(plan=plan, failureScenario=failure_scenario_rec)
                traffic_sim = sim.newTrafficSimulation(routeSim=route_sim, trafficLevel=traffic_level, queue=queue)
            else:
                pass
        else:
            pass

        int_sim_rec_map = traffic_sim.getAllInterfaceSimulatedTrafficRecords()

        # Get the most impacted interface after failure, and its corresponding utilization and traffic
        int_sim_util_dic = {}
        index = 0
        for int_sim_rec in int_sim_rec_map:
            if int_sim_rec_map[int_sim_rec].utilSim:
                int_sim_util_dic[index] = {'iface':(int_sim_rec.sourceKey.name + ':' + int_sim_rec.name), 'utilSim':int_sim_rec_map[int_sim_rec].utilSim, 'trafficSim':int_sim_rec_map[int_sim_rec].trafficSim}
                index += 1
        int_sim_util_dic = dict(sorted(int_sim_util_dic.items(), key=lambda x: (x[1]['utilSim']), reverse=True))
        first_value_sim_util = next(iter(int_sim_util_dic.values()), None)
        max_int_sim_util = {'most_impacted_interface_name':first_value_sim_util['iface'],
                        'interface_utilization_percentage': round(first_value_sim_util['utilSim'], 2),
                        'interface_traffic_Mbps': round(first_value_sim_util['trafficSim'], 2)}

        return max_int_sim_util

@mcp.tool()
async def get_route_shortest_path(node_a, node_b, metric_type, traffic, plan_file):
    """This function will query the underlying Crosswork Planning tool that will calculate, for the network selected, the shortest routing path between two nodes, 
    based on the input parameters node_a, node_b, a specific metric_type and a traffic value that will be carried through the routing path. The tool will compute the shortest 
    rounting path, and will determine the details of the routing path. It will return a dictionary that contains details such as mimumum, average and maximum latency, 
    the maximum interface utilization across the routing path and will also contain the detailed routing path specifying the interfaces across the path.

    Args:
        node_a {
                    "description":"Contains the name of the node or router that we are interested in evaluating as the source node for the routing path",
                    "examples": "node_name" "node_name:site", "node_name.site", ...
                }
        node_b: {
                    "description":"Contains the name of the node or router that we are interested in evaluating as the destination node for the routing path",
                    "examples": "node_name" "node_name:site", "node_name.site", ...
                }
        metric_type: {
                    "description":"Contains the value that will be used to optimiza the routing path. It can be on of the following values: igp, te or latency.
                    If no value is specified then use by default igp",
                    "examples": "igp", "te", "latency", ... pay attention that all of them should be in lowercase.
                }
        traffic: {
                    "type":"Float",
                    "units":"Mbps",
                    "description":"Contains the value of the traffic that will be carried through the routing path. This value should be in Mbps. If different units than Mbps
                    is provided, then value should be converted to Mbps (example: if value is 10G, then it should be converted to 10*1000=10000Mbps)",
                    "examples": "100Mbps", "1000M","1G"
                }
        plan_file: {
                    "description":"Contains the name of the plan file that will be used to calculate the shortest path",
                    "value": "The value will always be taken from a global variable called plan_file".
                }
    """
    with open_plan(plan_file, cp_host, cp_port, protocol) as network:
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

        return route_details  


def main():
    # Initialize and run the server
    mcp.run(transport='http', host='0.0.0.0', port=3000)

if __name__ == "__main__":
    main()