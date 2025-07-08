#!/usr/bin/python3

import sys
import re
import datetime
import json
import csv
import com.cisco.wae.design

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from com.cisco.wae.design.model import PlanFormat


def main(argv=None):
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_desc = 'Run CS RSVP Optimizer tool'

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_desc, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-plan-file", const="plan_file", required=True, type=str, nargs='?', help="input plan file (required)")
        parser.add_argument("-out-file", const="out_file", required=True, type=str, nargs='?', help="output plan file (required)")
        parser.add_argument("-cs-rsvp-file", const="cs_rsvp_file", required=True, type=str, nargs='?', help="CS RSVP LSP file (required)")

        # Process arguments
        args = parser.parse_args()
        plan_file = args.plan_file
        out_file = args.out_file
        cs_rsvp_file = args.cs_rsvp_file

    except:
        return 0

    print(datetime.datetime.now())
    with open(plan_file, 'rb') as file_r:
        # Establish connection with the CP server
        conn = com.cisco.wae.design.ServiceConnectionManager.newService()
        # Read the input plan file and transform to Bytes
        plan = conn.getPlanManager().newPlanFromBytes(file_r.read())
        # Get access to the Tool Manager and Sim Analysis tool
        tool_manager = conn.getToolManager()
        cs_rsvp_optimizer = tool_manager.newGenericTool()
        engineToolName = "cs_rsvp_optimizer"

        # Collect data from input CS RSVP LSP file
        cs_rsvp_file_dict = csv.DictReader(open(cs_rsvp_file, 'r'))
        # Create lsps data dictionaries with inputs from file
        for cs_rsvp_lsp in cs_rsvp_file_dict:
            cs_rsvp_source = cs_rsvp_lsp["source"]
            cs_rsvp_dest = cs_rsvp_lsp["destination"]
            cs_rsvp_assoc_id = cs_rsvp_lsp['association_id']
            cs_rsvp_traffic = cs_rsvp_lsp['traffic']

            opts = {"cs-rsvp-lsp-table": [{
                        "NodeA": cs_rsvp_source,
                        "NodeB": cs_rsvp_dest,
                        "AssociationId": cs_rsvp_assoc_id,
                        "SourceAddress": "",
                        "GlobalId": "",
                        "BW" : cs_rsvp_traffic,
                        "DisjointType" : "nodes,links"
                    }],
                "cs-rsvp-lsp-path-table": [
                    {
                        "NodeA": cs_rsvp_source,
                        "NodeB": cs_rsvp_dest,
                        "AssociationId": cs_rsvp_assoc_id,
                        "PathOption": "1",
                        "SourceAddress": "",
                        "GlobalId": "",
                        "Disjoint": "T"
                    },
                    {
                        "NodeA": cs_rsvp_source,
                        "NodeB": cs_rsvp_dest,
                        "AssociationId": cs_rsvp_assoc_id,
                        "PathOption": "2",
                        "SourceAddress": "",
                        "GlobalId": "",
                        "Disjoint": "T"
                    },
                    {
                        "NodeA": cs_rsvp_source,
                        "NodeB": cs_rsvp_dest,
                        "AssociationId": cs_rsvp_assoc_id,
                        "PathOption": "3",
                        "SourceAddress": "",
                        "GlobalId": "",
                        "Disjoint": "F"
                    },
                    {
                        "NodeA": cs_rsvp_source,
                        "NodeB": cs_rsvp_dest,
                        "AssociationId": cs_rsvp_assoc_id,
                        "PathOption": "4",
                        "SourceAddress": "",
                        "GlobalId": "",
                        "Disjoint": "F"
                    }
                ]}

            # Run CS RSVP Optimizer tool
            cs_rsvp_optimizer.runTool(plan.getNetwork(), engineToolName, json.dumps(opts))

        # Write to output plan file
        with open(out_file, 'wb') as file_w:
            file_w.write(plan.serializeToBytes(format=PlanFormat.PlnFile))
        # Close connection with CP server
        com.cisco.wae.design.ServiceConnectionManager.shutdownService(conn)
    print(datetime.datetime.now())

# end main()


if __name__ == '__main__':
    main()
    exit(0)
