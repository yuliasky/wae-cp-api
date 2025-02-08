#!/usr/bin/python3

import sys
import re
from datetime import datetime,timedelta
import json
import com.cisco.wae.design

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from pprint import pprint
from com.cisco.wae.design.tools import SAFailureType
from com.cisco.wae.design.tools import SimAnalysis
from com.cisco.wae.design.tools import SimAnalysisOptions
from com.cisco.wae.design.model.net import TrafficLevelKey

#plan_file = '/opt/cw-plan-sdk/cw-planning/plan-files/us_wan.txt'
cp_host = '172.20.163.100'
cp_port = '30744'
protocol = 'ssl'

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
    #print(json.dumps(merge_dict))

    return merge_dict

def get_worst_case_traffic_utilization(failure_type, plan_file):
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
        merge_dict = get_int_wc_util_traffic(int_wc_rec_list)

        # Close connection with CP server
        com.cisco.wae.design.ServiceConnectionManager.shutdownService(conn)

        return merge_dict

def main(argv=None):
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_desc = 'Run Sim Analysis and Get Worst-Case Traffic Util'

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_desc, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-failure-type", required=True, type=str, nargs='+', help="Failure Sets [Nodes Sites Circuits Ports PortCircuits] (required)")

        # Process arguments
        args = parser.parse_args()
        failure_type = args.failure_type

    except:
        return 0

    print(datetime.now())

    print(datetime.now())

# end main()


if __name__ == '__main__':
    main()
    exit(0)
