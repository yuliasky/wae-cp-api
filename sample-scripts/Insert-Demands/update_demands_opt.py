#!/usr/bin/python3

import sys
import re
import csv
import datetime
import com.cisco.wae.design

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from com.cisco.wae.design.model.net import DemandRecord
from com.cisco.wae.design.model.net import DemandEndpointKey
from com.cisco.wae.design.model.net import ServiceClassKey
from com.cisco.wae.design.model.net import TrafficLevelKey
from com.cisco.wae.design.model.traffic import DemandTrafficKey

def update_demand_list(plan,demandList, traffic_level_key):
    demand_manager = plan.getNetwork().getDemandManager()
    demand_traffic_manager=plan.getTrafficManager().getDemandTrafficManager()
    demandRecList=[]
    demandTrafficDic={}
    for demand in demandList:
        demand_source = demand["source"]
        demand_dest = demand['destination']
        demand_traffic = demand['traffic']
        demand_name = demand['name']
        demandRec = DemandRecord(
            source=DemandEndpointKey(key=demand_source),
            destination=DemandEndpointKey(key=demand_dest),
            serviceClass=ServiceClassKey(name='Default'),
            name=demand_name,)
        demandRecList.append(demandRec)
        '''
            Assuming each newly created demand has an unique name
        '''
        demandTrafficDic[demand_name]=demand_traffic
    new_demands=demand_manager.newDemands(demandRecList)
    print("Setting traffic")
    print(datetime.datetime.now())
    demandTrafficMap={}
    for key, dmd in new_demands.items():
        new_demand_traffic_key = DemandTrafficKey(dmdKey=key, traffLvlKey=TrafficLevelKey(name=traffic_level_key))
        demandTrafficMap[new_demand_traffic_key]=float(demandTrafficDic[dmd.getName()])
    demand_traffic_manager.setTraffics(demandTrafficMap)

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

        # Process arguments
        args = parser.parse_args()
        plan_file = args.plan_file
        out_file = args.out_file
        demands_file = args.demands_file

    except:
        return 0

    print(datetime.datetime.now())
    conn = com.cisco.wae.design.ServiceConnectionManager.newService()
    plan = conn.getPlanManager().newPlanFromFileSystem(plan_file)

    traffic_level_key = plan.getNetwork().getTrafficLevelManager().getAllTrafficLevelKeys()[0].name

    # Collect data from input files
    demands_file_dict = csv.DictReader(open(demands_file, 'r'))
    demand_dict_list=list(demands_file_dict)
    update_demand_list(plan,demand_dict_list, traffic_level_key)
    plan.serializeToFileSystem(out_file)
    com.cisco.wae.design.ServiceConnectionManager.shutdownService(conn)
    print(datetime.datetime.now())
# end main()


if __name__ == '__main__':
    main()
    exit(0)
