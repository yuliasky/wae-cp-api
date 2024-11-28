#!/usr/bin/python3

import sys
import re
import datetime
import com.cisco.wae.design

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from com.cisco.wae.design.tools import SAFailureType
from com.cisco.wae.design.tools import SimAnalysis
from com.cisco.wae.design.tools import SimAnalysisOptions
from com.cisco.wae.design.model.net import TrafficLevelKey

def get_int_wc_util(int_wc_rec_list):
    # This function will read from a list of records containing all interfaces worst-case attributes
    # and will get the worst-case Utilization value for each interface. It will append the values
    # into a new list and then will sort the list in descending order. Finally will get the first
    # value in the list representing the Maximum worst-case interface utilization value in the model
    # after running simulation analysis
    int_wc_util_list = []
    for int_wc_rec in int_wc_rec_list:
        int_wc_util_list.append(int_wc_rec.wcUtil)
    int_wc_util_list.sort(reverse=True)
    print("\nMaximum Worst-Case Interface Utilization is: {} %".format(round(int_wc_util_list[0], 2)))

def get_int_wc_traffic(int_wc_rec_list):
    # This function will read from a list of records containing all interfaces worst-case attributes
    # and will get the worst-case Traffic value for each interface. It will append the values
    # into a new list and then will sort the list in descending order. Finally will get the first
    # value in the list representing the Maximum worst-case interface traffic value in the model
    # after running simulation analysis
    int_wc_traffic_list = []
    for int_wc_rec in int_wc_rec_list:
        int_wc_traffic_list.append(int_wc_rec.wcTraffic)
    int_wc_traffic_list.sort(reverse=True)
    print("\nMaximum Worst-Case Interface Traffic is: {} Mbps\n".format(round(int_wc_traffic_list[0], 2)))

def main(argv=None):
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_desc = 'Run Sim Analysis and Get Worst-Case Traffic Util'

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_desc, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-plan-file", const="plan_file", required=True, type=str, nargs='?', help="input plan file (required)")
        parser.add_argument("-cp-host", const="cp_host", required=True, type=str, nargs='?', help="Crosswork Planning Host (required)")
        parser.add_argument("-cp-port", const="cp_port", required=True, type=str, nargs='?', help="Crosswork Planning Port (required)")
        parser.add_argument("-failure-type", required=True, type=str, nargs='+', help="Failure Sets [Nodes Sites Circuits Ports PortCircuits] (required)")

        # Process arguments
        args = parser.parse_args()
        plan_file = args.plan_file
        failure_type = args.failure_type
        cp_host = args.cp_host
        cp_port = args.cp_port
        protocol = 'ssl'

    except:
        return 0

    print(datetime.datetime.now())
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
            #print("Failure Type for {} is {}".format(failure, failure_type_dic[failure]))
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
        get_int_wc_util(int_wc_rec_list)
        get_int_wc_traffic(int_wc_rec_list)

        # Close connection with CP server
        com.cisco.wae.design.ServiceConnectionManager.shutdownService(conn)
    print(datetime.datetime.now())

# end main()


if __name__ == '__main__':
    main()
    exit(0)
