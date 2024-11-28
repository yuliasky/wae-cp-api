#!/usr/bin/python3

import sys
import re
import csv
import datetime
import com.cisco.wae.design

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from com.cisco.wae.design.model import PlanFormat
from com.cisco.wae.design.model.net import DemandRecord
from com.cisco.wae.design.model.net import DemandEndpointKey
from com.cisco.wae.design.model.net import ServiceClassKey
from com.cisco.wae.design.model.net import TrafficLevelKey
from com.cisco.wae.design.model.traffic import DemandTrafficKey

def update_demands(plan, demand_source, demand_dest, demand_traffic, demand_name, traffic_level_key):
    # Update demands table
    demand_manager = plan.getNetwork().getDemandManager()
    demand_traffic_manager = plan.getTrafficManager().getDemandTrafficManager()
    # Create new demand
    new_demand_record = DemandRecord(
        source=DemandEndpointKey(key=demand_source),
        destination=DemandEndpointKey(key=demand_dest),
        serviceClass=ServiceClassKey(name='Default'),
        name=demand_name,
    )
    new_demand = demand_manager.newDemand(new_demand_record)
    new_demand_key = new_demand.getKey()
    new_demand_traffic_key = DemandTrafficKey(dmdKey=new_demand_key, traffLvlKey=TrafficLevelKey(name=traffic_level_key))
    demand_traffic_manager.setTraffic(key=new_demand_traffic_key, traffic=float(demand_traffic))

def main(argv=None):
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_desc = 'Insert new Demands into plan file'

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_desc, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-plan-file", const="plan_file", required=True, type=str, nargs='?', help="input plan file (required)")
        parser.add_argument("-out-file", const="out_file", required=True, type=str, nargs='?', help="output plan file (required)")
        parser.add_argument("-demands-file", const="demands_file", required=True, type=str, nargs='?', help="demands file (required)")
        parser.add_argument("-cp-host", const="cp_host", required=True, type=str, nargs='?', help="Crosswork Planning Host (required)")
        parser.add_argument("-cp-port", const="cp_port", required=True, type=str, nargs='?', help="Crosswork Planning Port (required)")

        # Process arguments
        args = parser.parse_args()
        plan_file = args.plan_file
        out_file = args.out_file
        demands_file = args.demands_file
        cp_host = args.cp_host
        cp_port = args.cp_port
        protocol = 'ssl'

    except:
        return 0

    print(datetime.datetime.now())
    with open(plan_file, 'rb') as file_r:
        conn = com.cisco.wae.design.ServiceConnectionManager.newServiceConnection(cp_host, cp_port, protocol)
        plan = conn.getPlanManager().newPlanFromBytes(file_r.read())

        traffic_level_key = plan.getNetwork().getTrafficLevelManager().getAllTrafficLevelKeys()[0].name

        # Collect data from input files
        demands_file_dict = csv.DictReader(open(demands_file, 'r'))
        # Create demands data dictionaries with inputs from files
        for demand in demands_file_dict:
            print(demand)
            demand_source = demand["source"]
            demand_dest = demand['destination']
            demand_traffic = demand['traffic']
            demand_name = demand['name']
            update_demands(plan, demand_source, demand_dest, demand_traffic, demand_name, traffic_level_key)

        with open(out_file, 'wb') as file_w:
            file_w.write(plan.serializeToBytes(format=PlanFormat.DbFile))
        com.cisco.wae.design.ServiceConnectionManager.shutdownService(conn)
    print(datetime.datetime.now())

# end main()


if __name__ == '__main__':
    main()
    exit(0)
