#!/usr/bin/python3

import sys
import re
import csv
import datetime
import com.cisco.wae.design

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from com.cisco.wae.design.model.net import NodeKey
from com.cisco.wae.design.model.net import InterfaceKey
from com.cisco.wae.design.model.net import TrafficLevelKey
from com.cisco.wae.design.model.net import QueueKey
from com.cisco.wae.design.model.net import LSPKey
from com.cisco.wae.design.model.net import NamedPathKey
from com.cisco.wae.design.model.net import LSPRecord
from com.cisco.wae.design.model.net import LSPPathRecord
from com.cisco.wae.design.model.net import NamedPathRecord
from com.cisco.wae.design.model.net import NamedPathHopRecord
from com.cisco.wae.design.model.net import HopType

def insert_lsps(plan, lsp_source, lsp_dest, lsp_name, lsp_traffic, path_hops, lsp_type):
    tags = set()
    tags.add(lsp_type)
    lsp_record = LSPRecord(
        sourceKey=NodeKey(name=lsp_source),
        destinationKey=NodeKey(name=lsp_dest),
        name=lsp_name,
        tags=list(tags)
    )
    node_manager = plan.getNetwork().getNodeManager()
    has_node_source = node_manager.hasNode(key=NodeKey(name=lsp_source))
    has_node_dest = node_manager.hasNode(key=NodeKey(name=lsp_dest))
    if has_node_source == True and has_node_dest == True:
        lsp_manager = plan.getNetwork().getLSPManager()
        lsp_meas_traff = plan.getTrafficManager().getMeasuredTrafficManager().getLSPMeasuredTraffic()
        lsp_key = LSPKey(sourceKey=NodeKey(name=lsp_source), name=lsp_name)
        has_lsp = lsp_manager.hasLSP(key=lsp_key)
        if has_lsp == False:
            lsp = lsp_manager.newLSP(lspRec=lsp_record)
            traffic_lvl_manager = plan.getNetwork().getTrafficLevelManager()
            traffic_level = traffic_lvl_manager.getTrafficLevel(key=TrafficLevelKey(name='Default'))
            queue_manager = plan.getNetwork().getQueueManager()
            queue = queue_manager.getQueue(key=QueueKey(name=''))
            if lsp_traffic != 'na':
                lsp_meas_traff.setLSPTrafficValue(lsp=lsp, trafficLevel=traffic_level, queue=queue, traffic=float(lsp_traffic))
            #Insert LSP Path
            lsp_path_manager = plan.getNetwork().getLSPPathManager()
            lsp_path_record = LSPPathRecord(
                lKey=lsp_key,
                pathOption=1,
                active=True
            )
            lsp_path = lsp_path_manager.newLSPPath(pathRec=lsp_path_record)
            #Insert Named Path
            if path_hops != '':
                insert_named_paths(plan, lsp_source, lsp_name, path_hops, lsp_path)

def insert_named_paths(plan, lsp_source, lsp_name, path_hops, lsp_path):
    # This function will insert Named Paths and Named Path Hops for each new LSP Path.
    # Each Hop in the Named Path is separated by semicolon (;) and each attribute in the Hop
    # (node or interface) is separated by colon (:) - i.e node:interface
    named_path_manager = plan.getNetwork().getNamedPathManager()
    named_path_record = NamedPathRecord(
        sourceKey=NodeKey(name=lsp_source),
        name=('path_' + lsp_name),
        active=True
    )
    named_path = named_path_manager.newNamedPath(pathRec=named_path_record)
    node_manager = plan.getNetwork().getNodeManager()
    list_path_hops = path_hops.split(';')
    for hop in list_path_hops:
        hop_members = hop.split(':')
        hop_node = hop_memebers[0]
        hop_int = hop_memebers[1]
        has_node = node_manager.hasNode(key=NodeKey(name=hop_node))
        if has_node == True:
            named_path_hop_rec = NamedPathHopRecord(
                nodeHop=NodeKey(name=hop_node),
                ifaceHop=InterfaceKey(sourceKey=NodeKey(name=hop_node), name=hop_int),
                type=HopType.PathStrict
            )
            named_path.addHop(hopRec=named_path_hop_rec)
        else:
            break
    if has_node == True:
        lsp_path.setNamedPath(np=named_path)
    else:
        print(lsp_name)
        print(lsp_source)
        print(hop_node)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_desc = 'Insert LSPs and LSP Traffic into plan file'

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_desc, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-plan-file", const="plan_file", required=True, type=str, nargs='?', help="input plan file (required)")
        parser.add_argument("-out-file", const="out_file", required=True, type=str, nargs='?', help="output plan file (required)")
        parser.add_argument("-lsps-file", const="lsps_file", required=True, type=str, nargs='?', help="lsps file (required)")

        # Process arguments
        args = parser.parse_args()
        plan_file = args.plan_file
        out_file = args.out_file
        lsps_file = args.lsps_file

    except:
        return 0

    print(datetime.datetime.now())
    conn = com.cisco.wae.design.ServiceConnectionManager.newService()
    plan = conn.getPlanManager().newPlanFromFileSystem(plan_file)

    # Collect data from input LSP file
    lsps_file_dict = csv.DictReader(open(lsps_file, 'r'))
    # Create lsps data dictionaries with inputs from file
    for lsp in lsps_file_dict:
        lsp_source = lsp["source"]
        lsp_dest = lsp["destination"]
        lsp_name = lsp['name']
        lsp_traffic = lsp['traffic']
        path_hops = lsp['hops']
        lsp_type = lsp['type']
        insert_lsps(plan, lsp_source, lsp_dest, lsp_name, lsp_traffic, path_hops, lsp_type)

    plan.serializeToFileSystem(out_file)
    com.cisco.wae.design.ServiceConnectionManager.shutdownService(conn)
    print(datetime.datetime.now())

# end main()


if __name__ == '__main__':
    main()
    exit(0)