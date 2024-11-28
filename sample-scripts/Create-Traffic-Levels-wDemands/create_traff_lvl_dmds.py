#!/Users/jpalomin/Programas/WAE-Design-k9-7.5.2.1-MacOSX-x86_64/bin/design_api_python

import sys
import re
import csv
import datetime
import com.cisco.wae.design

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from com.cisco.wae.design.model.net import TrafficLevelRecord
from com.cisco.wae.design.model.net import TrafficLevelKey
from com.cisco.wae.design.model.traffic import DemandTrafficKey

def create_traffic_levels(plan, traffic_level_count, traffic_inc_pct):
    traffic_level_manager = plan.getNetwork().getTrafficLevelManager()
    # Create new traffic levels and update corresponding demands
    for i in range(1, (traffic_level_count + 1)):
        traffic_level_record = TrafficLevelRecord(name=("Level_" + str(i)))
        new_traffic_level = traffic_level_manager.newTrafficLevel(traffic_level_record)
        new_traffic_level_key = new_traffic_level.getKey()
        prev_traffic_level_key = traffic_level_manager.getAllTrafficLevelKeys()[i-1]
        update_demands(plan, new_traffic_level_key, prev_traffic_level_key, traffic_inc_pct)

def update_demands(plan, new_traffic_level_key, prev_traffic_level_key, traffic_inc_pct):
    # Update demands table
    demand_manager = plan.getNetwork().getDemandManager()
    demand_traffic_manager = plan.getTrafficManager().getDemandTrafficManager()
    demand_key_list = demand_manager.getAllDemandKeys()
    for demand_key in demand_key_list:
        prev_demand_traffic_key = DemandTrafficKey(dmdKey=demand_key, traffLvlKey=TrafficLevelKey(name=prev_traffic_level_key.name))
        prev_traffic = demand_traffic_manager.getTraffic(prev_demand_traffic_key)
        new_traffic = prev_traffic + ((prev_traffic*traffic_inc_pct)/100)
        new_demand_traffic_key = DemandTrafficKey(dmdKey=demand_key, traffLvlKey=TrafficLevelKey(name=new_traffic_level_key.name))
        demand_traffic_manager.setTraffic(key=new_demand_traffic_key, traffic=float(new_traffic))

def main(argv=None):
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_desc = 'Create traffic levels and update demands traffic'

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_desc, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-plan-file", const="plan_file", required=True, type=str, nargs='?', help="input plan file (required)")
        parser.add_argument("-out-file", const="out_file", required=True, type=str, nargs='?', help="output plan file (required)")
        parser.add_argument("-traffic-level-count", required=True, type=int, nargs='?', help="count of traffic levels")
        parser.add_argument("-traffic-inc-pct", required=True, type=int, nargs='?', help="percentage for increasing traffic")

        # Process arguments
        args = parser.parse_args()
        plan_file = args.plan_file
        out_file = args.out_file
        traffic_level_count = args.traffic_level_count
        traffic_inc_pct = args.traffic_inc_pct

    except:
        return 0

    print(datetime.datetime.now())
    conn = com.cisco.wae.design.ServiceConnectionManager.newService()
    plan = conn.getPlanManager().newPlanFromFileSystem(plan_file)
    sim = conn.getSimulationManager()

    # Create traffic levels as per input count
    create_traffic_levels(plan, traffic_level_count, traffic_inc_pct)

    plan.serializeToFileSystem(out_file)
    com.cisco.wae.design.ServiceConnectionManager.shutdownService(conn)
    print(datetime.datetime.now())

# end main()


if __name__ == '__main__':
    main()
    exit(0)
